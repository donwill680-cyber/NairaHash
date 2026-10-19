from fastapi import APIRouter

from app.api.v1 import admin, auth, dashboard, market, rewards, wallet

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(rewards.router)
api_router.include_router(wallet.router)
api_router.include_router(market.router)
api_router.include_router(admin.router)
