from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import xmlrpc.client
from datetime import datetime

app = FastAPI()

# -------------------------------------
# Configuration
# -------------------------------------

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "paymentsdb"
}

ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo"
ODOO_USER = "admin"
ODOO_PASSWORD = "admin"

# -------------------------------------
# Request Schema
# -------------------------------------

class PaymentRequest(BaseModel):
    amount: float
    date: datetime

# -------------------------------------
# Endpoint
# -------------------------------------

@app.post("/record-payment")
def record_payment(data: PaymentRequest):
    try:
        db = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = db.cursor()

        # 1. Insert event with PENDING status
        cursor.execute("""
            INSERT INTO payment_events (amount, event_date, sync_status)
            VALUES (%s, %s, 'PENDING')
        """, (data.amount, data.date))

        event_id = cursor.lastrowid
        db.commit()

        # 2. Odoo Authentication
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

        if not uid:
            raise Exception("Authentication to Odoo failed")

        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        # 3. Create accounting journal entry (account.move)
        move_vals = {
            "journal_id": 1,  # Must exist
            "line_ids": [
                # Debit line
                (0, 0, {
                    "account_id": 1105,  # Caja General
                    "name": "Pago recibido",
                    "debit": data.amount,
                    "credit": 0,
                }),
                # Credit line
                (0, 0, {
                    "account_id": 4105,  # Clientes Nacionales
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

        # 4. Update MySQL to COMPLETED
        cursor.execute("""
            UPDATE payment_events 
            SET sync_status = 'COMPLETED', odoo_move_id = %s
            WHERE event_id = %s
        """, (move_id, event_id))

        db.commit()

        return {"status": "success", "event_id": event_id, "odoo_move_id": move_id}

    except Exception as e:
        # 5. Mark event as FAILED
        cursor.execute("""
            UPDATE payment_events 
            SET sync_status = 'FAILED'
            WHERE event_id = %s
        """, (event_id,))
        db.commit()

        raise HTTPException(status_code=500, detail=str(e))
