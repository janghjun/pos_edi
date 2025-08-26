from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SaleItem(BaseModel):
    sku: str
    qty: int
    unit_price: float
    discount: float = 0.0

class SaleEvent(BaseModel):
    event_id: str
    event_ts: datetime
    store_id: str
    pos_txn_id: str
    items: List[SaleItem]
    customer_id: Optional[str] = None
    payment: dict
    coupon_codes: Optional[List[str]] = None
