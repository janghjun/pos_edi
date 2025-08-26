from fastapi import APIRouter
import httpx, os
from datetime import datetime

router = APIRouter()
HQ_BASE = os.getenv("HQ_BASE", "http://hq-api:8000")
WMS_BASE = os.getenv("WMS_BASE", "http://wms-adapter:8000")

@router.post("/supplier/po")
def receive_po(po: dict):
    po_no = po.get("po_no")
    asn_no = f"ASN-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    asn_payload = {
        "po_no": po_no,
        "asn_no": asn_no,
        "eta": datetime.utcnow().isoformat()+"Z",
        "lines": [{"sku": line["sku"], "ship_qty": line["qty"]} for line in po.get("lines", [])]
    }
    with httpx.Client(timeout=10.0) as client:
        client.post(f"{HQ_BASE}/edi/asn", json=asn_payload)
        client.post(f"{WMS_BASE}/inbound-expected", json={"asn_no": asn_no, **po})
        client.post(f"{WMS_BASE}/simulate-receipt", json={
            "asn_no": asn_no, "store_id": po.get("store_id"),
            "lines": [{"sku": l["sku"], "accept_qty": l["qty"], "reject_qty": 0} for l in po.get("lines", [])]
        })
    return {"ok": True, "asn_no": asn_no}
