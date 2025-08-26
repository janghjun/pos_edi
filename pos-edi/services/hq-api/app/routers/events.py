from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import SaleEvent
from app.services.sales_service import process_sale_event

router = APIRouter()

@router.post("/sales")
def ingest_sale(event: SaleEvent, db: Session = Depends(get_db)):
    auto_po = process_sale_event(db, event.model_dump())
    db.commit()
    return {"sale_id": event.pos_txn_id, "accepted": True, "auto_po": auto_po}
