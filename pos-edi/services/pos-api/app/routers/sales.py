from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from kafka import KafkaProducer
import os, json

router = APIRouter()
BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
producer = KafkaProducer(bootstrap_servers=[BROKER], value_serializer=lambda v: json.dumps(v).encode('utf-8'))

class Item(BaseModel):
    sku: str
    qty: int
    unit_price: float
    discount: float = 0.0

class CreateSale(BaseModel):
    store_id: str
    pos_txn_id: str
    items: List[Item]
    customer_id: Optional[str] = None
    payment: dict
    coupon_codes: Optional[List[str]] = None

@router.post("/sales")
def create_sale(payload: CreateSale):
    event = {
        "event_id": payload.pos_txn_id,
        "event_ts": datetime.utcnow().isoformat()+"Z",
        **payload.model_dump()
    }
    producer.send('sales.v1', event)
    return {"pos_ack": True, "published": "sales.v1"}
