from fastapi import APIRouter
import httpx, os

router = APIRouter()
HQ_BASE = os.getenv("HQ_BASE", "http://hq-api:8000")

@router.post("/inbound-expected")
def inbound_expected(body: dict):
    return {"ok": True}

@router.post("/simulate-receipt")
def simulate_receipt(body: dict):
    payload = {
        "asn_no": body.get("asn_no"),
        "store_id": body.get("store_id"),
        "received_at": body.get("received_at", None),
        "lines": body.get("lines", [])
    }
    with httpx.Client(timeout=10.0) as client:
        client.post(f"{HQ_BASE}/edi/inbound", json=payload)
    return {"ok": True}
