from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.v1.api import api_router
from app.config import settings
from app.db import init_db

app = FastAPI(
    title="NairaHash",
    description="Professional Bitcoin rewards platform for earning, tracking, and withdrawing BTC rewards.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def read_root() -> HTMLResponse:
    template_path = Path("app/templates/index.html")
    html = template_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.get("/health")
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": "NairaHash API",
        "environment": settings.environment,
    }


app.include_router(api_router, prefix="/api/v1")
