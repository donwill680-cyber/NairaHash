from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.config import settings
from app.db import init_db
from app.tasks.reward_scheduler import run_reward_cycle

app = FastAPI(
    title="NairaHash",
    description="Bitcoin rewards and earning platform with secure ledger, admin controls, and automated reward processing.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

scheduler = BackgroundScheduler()


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()
    if settings.enable_background_tasks:
        scheduler.add_job(run_reward_cycle, "interval", minutes=settings.schedule_interval_minutes, id="nairhash_reward_cycle")
        scheduler.start()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    if scheduler.running:
        scheduler.shutdown()


@app.get("/", response_class=HTMLResponse)
async def home() -> HTMLResponse:
    with open("app/templates/landing.html", "r", encoding="utf-8") as fh:
        return HTMLResponse(content=fh.read())


@app.get("/auth", response_class=HTMLResponse)
async def auth_page() -> HTMLResponse:
    with open("app/templates/auth.html", "r", encoding="utf-8") as fh:
        return HTMLResponse(content=fh.read())


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page() -> HTMLResponse:
    with open("app/templates/dashboard.html", "r", encoding="utf-8") as fh:
        return HTMLResponse(content=fh.read())


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": "NairaHash API", "environment": settings.environment}


app.include_router(api_router, prefix="/api/v1")
