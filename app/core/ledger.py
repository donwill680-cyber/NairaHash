from __future__ import annotations

import random
import string
from datetime import datetime, timezone
from decimal import Decimal

import httpx

from app.config import settings


def sats_to_btc(sats: int) -> Decimal:
    return Decimal(sats) / Decimal(100_000_000)


def btc_to_sats(btc: Decimal | float | int) -> int:
    amount = Decimal(str(btc))
    return int((amount * Decimal(100_000_000)).to_integral_value())


def format_btc_from_sats(sats: int) -> str:
    return f"{sats_to_btc(sats):.8f} BTC"


def generate_referral_code(email: str) -> str:
    seed = email.split("@")[0].upper().replace("-", "")[:6]
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"NA{seed or 'HASH'}{suffix}"


async def fetch_btc_price_ngn() -> float:
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": settings.btc_reference_currency.lower()}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            value = data.get("bitcoin", {}).get(settings.btc_reference_currency.lower())
            if value:
                return float(value)
    except Exception:
        pass
    return 4500000.0


def format_ngn(value: float | int) -> str:
    return f"₦{float(value):,.2f}"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
