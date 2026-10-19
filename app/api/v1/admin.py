from fastapi import APIRouter

from app.core.security import fetch_btc_price_ngn

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/price")
async def btc_price() -> dict:
    value = await fetch_btc_price_ngn()
    return {
        "currency": "NGN",
        "price_ngn": value,
        "source": "CoinGecko",
    }
