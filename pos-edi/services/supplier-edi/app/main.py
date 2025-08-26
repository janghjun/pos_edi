from fastapi import FastAPI
from app.routers import supplier

app = FastAPI(title="Supplier EDI")
app.include_router(supplier.router)

@app.get("/health")
def health():
    return {"ok": True}
