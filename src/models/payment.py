from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PaymentEvent(Base):
    __tablename__ = 'payment_events'

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    event_date = Column(DateTime, nullable=False)
    odoo_move_id = Column(Integer, nullable=True)
    sync_status = Column(Enum('PENDING', 'COMPLETED', 'FAILED'), nullable=False)
