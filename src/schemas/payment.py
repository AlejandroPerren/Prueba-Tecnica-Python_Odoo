from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class PaymentRequest(BaseModel):
    amount: float
    date: datetime

class PaymentResponse(BaseModel):
    status: str
    event_id: int
    odoo_move_id: int

class Ticket(BaseModel):
    event_id: int
    amount: float
    event_date: datetime
    odoo_move_id: Optional[int]
    sync_status: str

    class Config:
        from_attributes = True

class TicketResponse(BaseModel):
    tickets: List[Ticket]
