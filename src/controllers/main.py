# technical_test_odoo/controllers/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

from src.config import settings
from src.services import db_service, odoo_service

app = FastAPI()

class PaymentRequest(BaseModel):
    amount: float
    date: datetime


@app.post("/record-payment")
def record_payment(data: PaymentRequest):
    db_conn = None
    cursor = None
    event_id = None

    try:
        # -----------------------------
        # START MYSQL TRANSACTION
        # -----------------------------
        db_conn = db_service.get_db_connection()
        cursor = db_conn.cursor()
        db_conn.start_transaction()

        event_id = db_service.create_payment_event(cursor, data.amount, data.date)

        # -----------------------------
        # AUTHENTICATE AND CONNECT ODOO
        # -----------------------------
        uid = odoo_service.get_odoo_uid()
        models = odoo_service.get_odoo_models_proxy()

        # -----------------------------
        # GET ODOO IDS
        # -----------------------------
        debit_acc = odoo_service.get_account_id_by_code(models, settings.ODOO_DB, uid, settings.ODOO_PASSWORD, "1105")
        credit_acc = odoo_service.get_account_id_by_code(models, settings.ODOO_DB, uid, settings.ODOO_PASSWORD, "4105")
        journal_id = odoo_service.get_cash_journal_id(models, settings.ODOO_DB, uid, settings.ODOO_PASSWORD)

        # -----------------------------
        # CREATE MOVE IN ODOO
        # -----------------------------
        move_vals = {
            "journal_id": journal_id,
            "date": data.date.date().isoformat(),
            "line_ids": [
                (0, 0, {"account_id": debit_acc, "name": "Pago recibido", "debit": data.amount, "credit": 0}),
                (0, 0, {"account_id": credit_acc, "name": "Pago recibido", "debit": 0, "credit": data.amount}),
            ],
        }
        move_id = odoo_service.create_account_move(models, settings.ODOO_DB, uid, settings.ODOO_PASSWORD, move_vals)

        # -----------------------------
        # COMMIT SUCCESS
        # -----------------------------
        db_service.update_payment_event_success(cursor, event_id, move_id)
        db_conn.commit()

        return {"status": "success", "event_id": event_id, "odoo_move_id": move_id}

    except Exception as e:
        if db_conn and cursor and event_id:
            db_service.update_payment_event_failed(cursor, event_id)
            db_conn.commit()

        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close()
