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


def get_account_by_code(models, db, uid, pwd, code):
    acc = models.execute_kw(
        db, uid, pwd,
        "account.account", "search_read",
        [[["code", "=", code]]],
        {"fields": ["id", "name"], "limit": 1}
    )
    if not acc:
        raise Exception(f"Account with code {code} not found in Odoo.")
    return acc[0]["id"]


def get_cash_journal(models, db, uid, pwd):
    journal = models.execute_kw(
        db, uid, pwd,
        "account.journal", "search_read",
        [[["type", "=", "cash"]]],
        {"fields": ["id"], "limit": 1}
    )
    if not journal:
        raise Exception("No cash journal found in Odoo.")
    return journal[0]["id"]


@app.post("/record-payment")
def record_payment(data: PaymentRequest):
    db = None
    cursor = None
    event_id = None

    try:
        # -----------------------------
        # START MYSQL TRANSACTION
        # -----------------------------
        db = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = db.cursor()
        db.start_transaction()

        cursor.execute("""
            INSERT INTO payment_events (amount, event_date, sync_status)
            VALUES (%s, %s, 'PENDING')
        """, (data.amount, data.date))
        event_id = cursor.lastrowid

        # -----------------------------
        # AUTHENTICATE ODOO
        # -----------------------------
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

        if not uid:
            raise Exception("Authentication failed to Odoo.")

        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        # -----------------------------
        # GET EXACT ACCOUNTS
        # -----------------------------
        debit_acc = get_account_by_code(models, ODOO_DB, uid, ODOO_PASSWORD, "1105")  # Caja General
        credit_acc = get_account_by_code(models, ODOO_DB, uid, ODOO_PASSWORD, "4105")  # Clientes Nacionales
        journal_id = get_cash_journal(models, ODOO_DB, uid, ODOO_PASSWORD)

        # -----------------------------
        # CREATE MOVE IN ODOO
        # -----------------------------
        move_vals = {
            "journal_id": journal_id,
            "date": data.date.date().isoformat(),
            "line_ids": [
                (0, 0, {
                    "account_id": debit_acc,
                    "name": "Pago recibido",
                    "debit": data.amount,
                    "credit": 0,
                }),
                (0, 0, {
                    "account_id": credit_acc,
                    "name": "Pago recibido",
                    "debit": 0,
                    "credit": data.amount,
                })
            ]
        }

        move_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "account.move", "create", [move_vals]
        )

        # -----------------------------
        # COMMIT SUCCESS
        # -----------------------------
        cursor.execute("""
            UPDATE payment_events
            SET sync_status = 'COMPLETED', odoo_move_id = %s
            WHERE event_id = %s
        """, (move_id, event_id))

        db.commit()

        return {"status": "success", "event_id": event_id, "odoo_move_id": move_id}

    except Exception as e:
        if db and cursor and event_id:
            cursor.execute("""
                UPDATE payment_events
                SET sync_status = 'FAILED'
                WHERE event_id = %s
            """, (event_id,))
            db.commit()

        raise HTTPException(status_code=500, detail=str(e))

