from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.services import odoo_service
from src.schemas.payment import PaymentRequest, PaymentResponse, TicketResponse
from src.db.session import get_db
from src.services.db_service import DBService
from src.services.payment_service import (
    PaymentService,
)  
from src.services.odoo_service import OdooService
from src.config.settings import setup_cors

app = FastAPI()

setup_cors(app)


# Dependency to get PaymentService instance
def get_payment_service(
    db: Session = Depends(get_db),
    odoo: OdooService = Depends(
        lambda: odoo_service
    ),  # odoo_service is already a singleton instance
) -> PaymentService:
    db_service_instance = DBService(db)
    return PaymentService(db_service=db_service_instance, odoo_service=odoo)


@app.get("/")
def read_root():
    return FileResponse("src/static/index.html")


@app.get("/tickets", response_model=TicketResponse)
def get_tickets(db: Session = Depends(get_db)):
    try:
        db_service_instance = DBService(db)
        tickets = db_service_instance.get_all_payment_events()
        return {"tickets": tickets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/record-payment", response_model=PaymentResponse)
def record_payment(
    data: PaymentRequest, payment_service: PaymentService = Depends(get_payment_service)
):
    try:
        return payment_service.process_payment(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
