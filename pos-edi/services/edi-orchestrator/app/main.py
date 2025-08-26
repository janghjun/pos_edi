from fastapi import FastAPI
from app.workers.po_consumer import POConsumer

app = FastAPI(title="EDI Orchestrator")

consumer = POConsumer()
@app.on_event("startup")
async def startup():
    consumer.start()

@app.get("/health")
def health():
    return {"ok": True}
