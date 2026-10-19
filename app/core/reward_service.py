from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, RewardTransaction, User, UserRewardLedger


async def ensure_unique_reward_credit(
    db: AsyncSession,
    user_id: str,
    source_type: str,
    source_ref: str,
    amount_sats: int,
    description: str,
    balance_key: str = "demo_balance_sats",
) -> tuple[bool, str | None]:
    existing = await db.execute(
        select(UserRewardLedger).where(
            UserRewardLedger.user_id == user_id,
            UserRewardLedger.source_type == source_type,
            UserRewardLedger.source_ref == source_ref,
        )
    )
    if existing.scalar_one_or_none():
        return False, "Reward already processed"

    user = await db.get(User, user_id)
    if not user:
        return False, "User not found"

    current_balance = getattr(user, balance_key)
    new_balance = current_balance + amount_sats
    user.demo_balance_sats = new_balance if balance_key == "demo_balance_sats" else user.demo_balance_sats
    user.real_balance_sats = user.real_balance_sats
    user.total_rewards_sats = user.total_rewards_sats + amount_sats

    ledger_entry = UserRewardLedger(
        user_id=user_id,
        source_type=source_type,
        source_ref=source_ref,
        delta_sats=amount_sats,
        balance_after_sats=new_balance,
        status="credited",
        description=description,
    )
    db.add(ledger_entry)

    txn = RewardTransaction(
        user_id=user_id,
        kind="credit",
        amount_sats=amount_sats,
        balance_after_sats=new_balance,
        status="completed",
        reference=source_ref,
        description=description,
    )
    db.add(txn)

    notification = Notification(
        user_id=user_id,
        title="Reward credited",
        body=f"{description} ({amount_sats} sats)",
        kind="reward",
    )
    db.add(notification)

    return True, None
