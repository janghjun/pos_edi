import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import events, inventory, po, settlement, edi
from app.workers.sales_consumer import SalesConsumer

app = FastAPI(title="HQ API")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(edi.router, tags=["edi"])
app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
app.include_router(po.router, prefix="/po", tags=["po"])
app.include_router(settlement.router, prefix="/settlement", tags=["settlement"])

consumer = SalesConsumer()

@app.on_event("startup")
async def startup():
    consumer.start()

@app.get("/health")
def health():
    return {"ok": True}
