from fastapi import FastAPI
from app.config import settings
from app.db import init_db
from app.api.v1.api import api_router

app = FastAPI(
    title="NairaHash",
    description="Bitcoin rewards and earning platform for users to complete tasks and withdraw BTC rewards.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()


@app.get("/health")
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": "NairaHash API",
        "environment": settings.environment,
    }


app.include_router(api_router, prefix="/api/v1")
