from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db, q

router = APIRouter()

@router.get("/list")
def list_po(db: Session = Depends(get_db)):
    rows = q(db, """
        SELECT po_no, supplier_id, store_id, status, expected_date, created_at
        FROM purchase_orders ORDER BY po_id DESC LIMIT 100
    """).mappings().all()
    return [dict(r) for r in rows]
