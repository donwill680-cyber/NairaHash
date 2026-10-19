from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.ledger import credit_demo_reward
from app.db import Base
from app.models import User


@pytest.mark.asyncio
async def test_credit_demo_reward() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(engine, expire_on_commit=False, class_=object)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    user = User(
        email="ledger@example.com",
        full_name="Ledger User",
        password_hash="x",
        referral_code="NALEDGER",
    )

    async with engine.connect() as conn:
        from sqlalchemy.ext.asyncio import AsyncSession

        session = AsyncSession(bind=conn)
        session.add(user)
        await session.commit()
        await session.refresh(user)

        ok, err = await credit_demo_reward(session, user.id, 5000, "daily_reward", "daily-test", "Daily reward")
        assert ok is True
        assert err is None
        assert user.demo_balance_sats == 5000
        await session.commit()

        second, _ = await credit_demo_reward(session, user.id, 5000, "daily_reward", "daily-test", "Daily reward")
        assert second is False
