from fastapi import FastAPI
from app.routers import wms

app = FastAPI(title="WMS Adapter")
app.include_router(wms.router)

@app.get("/health")
def health():
    return {"ok": True}
