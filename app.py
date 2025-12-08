from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import xmlrpc.client
from datetime import datetime

app = FastAPI()

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "paymentsdb"
}

ODOO_URL = "https://altamira2.odoo.com"
ODOO_DB = "altamira2"
ODOO_USER = "maxtaxplay@gmail.com"
ODOO_PASSWORD = "Grisel1102"


class PaymentRequest(BaseModel):
    amount: float
    date: datetime


# ----------------------------------------
# FUNCIONES AUXILIARES
# ----------------------------------------

def get_journal(models, db, uid, pwd):
    """Busca un diario usable en Odoo."""
    preferred = ["cash", "bank", "general"]

    for t in preferred:
        journals = models.execute_kw(
            db, uid, pwd,
            "account.journal", "search_read",
            [[["type", "=", t]]],
            {"fields": ["id", "name", "type"], "limit": 1}
        )
        if journals:
            return journals[0]["id"]

    raise Exception("No usable journal found (cash/bank/general)")


def get_account(models, db, uid, pwd, account_type):
    acc = models.execute_kw(
        db, uid, pwd,
        "account.account", "search_read",
        [[["account_type", "=", account_type]]],
        {"fields": ["id", "name"], "limit": 1}
    )
    if not acc:
        raise Exception(f"No account found for type {account_type}")
    return acc[0]["id"]


# ----------------------------------------
# ENDPOINT PRINCIPAL
# ----------------------------------------

@app.post("/record-payment")
def record_payment(data: PaymentRequest):
    try:
        # -----------------------------
        # INSERT EVENT IN MYSQL
        # -----------------------------
        db = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO payment_events (amount, event_date, sync_status)
            VALUES (%s, %s, 'PENDING')
        """, (data.amount, data.date))
        event_id = cursor.lastrowid
        db.commit()

        # -----------------------------
        # AUTHENTICATE ODOO
        # -----------------------------
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

        if not uid:
            raise Exception("Authentication to Odoo failed")

        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        # -----------------------------
        # GET JOURNAL + ACCOUNTS
        # -----------------------------
        journal_id = get_journal(models, ODOO_DB, uid, ODOO_PASSWORD)
        cash_account_id = get_account(models, ODOO_DB, uid, ODOO_PASSWORD, "asset_cash")
        receivable_account_id = get_account(models, ODOO_DB, uid, ODOO_PASSWORD, "asset_receivable")

        # -----------------------------
        # CREATE JOURNAL ENTRY IN ODOO
        # -----------------------------
        move_vals = {
            "journal_id": journal_id,
            "date": data.date.date().isoformat(),
            "line_ids": [
                (0, 0, {
                    "account_id": cash_account_id,
                    "name": "Pago recibido",
                    "debit": data.amount,
                    "credit": 0,
                }),
                (0, 0, {
                    "account_id": receivable_account_id,
                    "name": "Pago recibido",
                    "debit": 0,
                    "credit": data.amount,
                })
            ]
        }

        move_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "account.move", "create",
            [move_vals]
        )

        # -----------------------------
        # UPDATE MYSQL AS COMPLETED
        # -----------------------------
        cursor.execute("""
            UPDATE payment_events
            SET sync_status = 'COMPLETED', odoo_move_id = %s
            WHERE event_id = %s
        """, (move_id, event_id))
        db.commit()

        return {"status": "success", "event_id": event_id, "odoo_move_id": move_id}

    except Exception as e:

        # Set FAILED
        try:
            cursor.execute("""
                UPDATE payment_events SET sync_status = 'FAILED'
                WHERE event_id = %s
            """, (event_id,))
            db.commit()
        except:
            pass

        raise HTTPException(status_code=500, detail=str(e))
