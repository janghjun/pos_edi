from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db, q

router = APIRouter()

@router.put("/policy/{store_id}/{sku}")
def upsert_policy(store_id: str, sku: str, body: dict, db: Session = Depends(get_db)):
    safety = int(body.get("safety_stock", 0))
    reorder = int(body.get("reorder_point", 0))
    lead = int(body.get("lead_time_day", 2))
    q(db, """
        INSERT INTO inventory_policy (store_id, sku, safety_stock, reorder_point, lead_time_day)
        VALUES (:store_id, :sku, :s, :r, :l)
        ON DUPLICATE KEY UPDATE safety_stock=:s, reorder_point=:r, lead_time_day=:l
    """, store_id=store_id, sku=sku, s=safety, r=reorder, l=lead)
    db.commit()
    return {"ok": True}

@router.get("/snapshot")
def get_snapshot(store_id: str, sku: str, db: Session = Depends(get_db)):
    row = q(db, """
        SELECT store_id, sku, on_hand, updated_at
        FROM inventory_snapshot WHERE store_id=:store_id AND sku=:sku
    """, store_id=store_id, sku=sku).mappings().first()
    if not row:
        raise HTTPException(404, "snapshot not found")
    return dict(row)
