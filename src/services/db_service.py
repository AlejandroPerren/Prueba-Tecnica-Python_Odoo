from sqlalchemy.orm import Session
from datetime import datetime
from src.models.payment import PaymentEvent
from typing import List

class DBService:
    def __init__(self, db: Session):
        self.db = db

    def create_payment_event(self, amount: float, date: datetime) -> PaymentEvent:
        """Inserts a new payment event with a 'PENDING' status."""
        new_event = PaymentEvent(
            amount=amount,
            event_date=date,
            sync_status='PENDING'
        )
        self.db.add(new_event)
        self.db.commit()
        self.db.refresh(new_event)
        return new_event

    def update_payment_event_success(self, event_id: int, odoo_move_id: int) -> PaymentEvent:
        """Updates a payment event to 'COMPLETED'."""
        event = self.db.query(PaymentEvent).filter(PaymentEvent.event_id == event_id).one()
        event.sync_status = 'COMPLETED'
        event.odoo_move_id = odoo_move_id
        self.db.commit()
        self.db.refresh(event)
        return event

    def update_payment_event_failed(self, event_id: int) -> PaymentEvent:
        """Updates a payment event to 'FAILED'."""
        event = self.db.query(PaymentEvent).filter(PaymentEvent.event_id == event_id).one()
        event.sync_status = 'FAILED'
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_all_payment_events(self) -> List[PaymentEvent]:
        """Retrieves all payment events."""
        return self.db.query(PaymentEvent).order_by(PaymentEvent.event_id.desc()).all()

# This service is stateful (depends on a session), so we don't create a singleton instance here.
# It will be instantiated per request using FastAPI's dependency injection.
