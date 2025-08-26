from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import sales

app = FastAPI(title="POS API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(sales.router)

@app.get("/health")
def health():
    return {"ok": True}
