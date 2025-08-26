from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db, q

router = APIRouter()

@router.post("/edi/asn")
def receive_asn(body: dict, db: Session = Depends(get_db)):
    po_no = body.get("po_no")
    asn_no = body.get("asn_no")
    po_id = q(db, "SELECT po_id FROM purchase_orders WHERE po_no=:po", po=po_no).scalar_one()
    q(db, "INSERT INTO asn(asn_no, po_id, eta, status) VALUES (:a,:p,NOW(),'IN_TRANSIT')", a=asn_no, p=po_id)
    for ln in body.get("lines", []):
        q(db, "INSERT INTO asn_lines(asn_id, sku, ship_qty) VALUES((SELECT asn_id FROM asn WHERE asn_no=:a), :s, :q)",
          a=asn_no, s=ln["sku"], q=ln["ship_qty"])
    q(db, "UPDATE purchase_orders SET status='CONFIRMED' WHERE po_id=:p", p=po_id)
    db.commit(); return {"ok": True}

@router.post("/edi/inbound")
def inbound(body: dict, db: Session = Depends(get_db)):
    asn_no = body.get("asn_no"); store_id = body.get("store_id")
    asn_id = q(db, "SELECT asn_id FROM asn WHERE asn_no=:a", a=asn_no).scalar_one()
    q(db, "INSERT INTO inbound_receipts(asn_id, store_id, received_at, status) VALUES (:a,:s,NOW(),'RECEIVED')", a=asn_id, s=store_id)
    rcp_id = q(db, "SELECT LAST_INSERT_ID()").scalar_one()
    for ln in body.get("lines", []):
        q(db, "INSERT INTO inbound_receipt_lines(receipt_id, sku, accept_qty, reject_qty, reject_reason) VALUES(:r,:sku,:a,:rej,:reason)",
          r=rcp_id, sku=ln["sku"], a=ln.get("accept_qty",0), rej=ln.get("reject_qty",0), reason=ln.get("reject_reason"))
        q(db, "INSERT INTO inventory_snapshot(store_id, sku, on_hand) VALUES(:s,:sku,:a) ON DUPLICATE KEY UPDATE on_hand=on_hand+:a",
          s=store_id, sku=ln["sku"], a=ln.get("accept_qty",0))
    q(db, "UPDATE asn SET status='CLOSED' WHERE asn_id=:a", a=asn_id)
    q(db, "UPDATE purchase_orders p JOIN asn a ON a.po_id=p.po_id SET p.status='RECEIVED' WHERE a.asn_id=:a", a=asn_id)
    db.commit(); return {"ok": True}
