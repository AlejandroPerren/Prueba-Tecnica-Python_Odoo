from datetime import datetime
from src.schemas.payment import PaymentRequest, PaymentResponse
from src.services.db_service import DBService
from src.services.odoo_service import OdooService


class PaymentService:
    def __init__(self, db_service: DBService, odoo_service: OdooService):
        self.db_service = db_service
        self.odoo_service = odoo_service

    def process_payment(self, data: PaymentRequest) -> PaymentResponse:
        event = None

        try:
            # -----------------------------
            # CREATE PAYMENT EVENT (PENDING)
            # -----------------------------
            event = self.db_service.create_payment_event(
                amount=data.amount,
                event_date=data.date
            )

            # -----------------------------
            # GET ODOO IDS
            # -----------------------------
            debit_acc = self.odoo_service.get_account_id_by_code("1.1.3.01.010")
            credit_acc = self.odoo_service.get_account_id_by_code("1.1.3.01.020")
            journal_id = self.odoo_service.get_cash_journal_id()

            # -----------------------------
            # CREATE MOVE IN ODOO (DRAFT)
            # -----------------------------
            move_vals = {
                "journal_id": journal_id,
                "date": data.date.date().isoformat(),
                "ref": f"API-PAYMENT-{event.event_id}",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": debit_acc,
                            "name": "Pago recibido",
                            "debit": data.amount,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": credit_acc,
                            "name": "Pago recibido",
                            "debit": 0.0,
                            "credit": data.amount,
                        },
                    ),
                ],
            }

            odoo_move_id = self.odoo_service.create_account_move(move_vals)

            # -----------------------------
            # POST MOVE (PUBLISH IN ODOO)
            # -----------------------------
            self.odoo_service.post_account_move(odoo_move_id)

            # -----------------------------
            # UPDATE PAYMENT EVENT (COMPLETED)
            # -----------------------------
            self.db_service.update_payment_event_success(
                event_id=event.event_id,
                odoo_move_id=odoo_move_id
            )

            return PaymentResponse(
                status="success",
                event_id=event.event_id,
                odoo_move_id=odoo_move_id,
            )

        except Exception as e:
            if event and event.event_id:
                self.db_service.update_payment_event_failed(event.event_id)
            raise e
