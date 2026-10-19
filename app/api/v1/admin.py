from fastapi import APIRouter
import httpx

from app.config import settings

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/price")
async def btc_price() -> dict:
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": settings.btc_reference_currency.lower()}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
            value = payload.get("bitcoin", {}).get(settings.btc_reference_currency.lower())
            if value:
                return {"currency": settings.btc_reference_currency, "price": float(value), "source": "CoinGecko"}
    except Exception:
        pass
    return {"currency": settings.btc_reference_currency, "price": 4500000.0, "source": "fallback"}
