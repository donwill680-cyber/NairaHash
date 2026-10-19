from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RewardLedgerEntry, RewardTransaction, Notification, User


def sats_to_btc(sats: int) -> Decimal:
    return Decimal(sats) / Decimal(100_000_000)


def btc_to_sats(btc: Decimal | float | int | str) -> int:
    return int((Decimal(str(btc)) * Decimal(100_000_000)).to_integral_value())


async def credit_demo_reward(
    db: AsyncSession,
    user_id: str,
    amount_sats: int,
    source_type: str,
    source_ref: str,
    description: str,
) -> tuple[bool, str | None]:
    if amount_sats <= 0:
        return False, "Reward amount must be positive"

    existing = await db.execute(
        select(RewardLedgerEntry).where(
            RewardLedgerEntry.user_id == user_id,
            RewardLedgerEntry.source_type == source_type,
            RewardLedgerEntry.source_ref == source_ref,
        )
    )
    if existing.scalar_one_or_none():
        return False, "Duplicate reward detected"

    user = await db.get(User, user_id)
    if not user:
        return False, "User not found"

    new_balance = user.demo_balance_sats + amount_sats
    user.demo_balance_sats = new_balance
    user.total_rewards_sats += amount_sats

    ledger_entry = RewardLedgerEntry(
        user_id=user_id,
        source_type=source_type,
        source_ref=source_ref,
        delta_sats=amount_sats,
        balance_after_sats=new_balance,
        status="credited",
        description=description,
    )
    db.add(ledger_entry)

    tx = RewardTransaction(
        user_id=user_id,
        kind="credit",
        amount_sats=amount_sats,
        balance_after_sats=new_balance,
        status="completed",
        reference=source_ref,
        description=description,
    )
    db.add(tx)

    notif = Notification(
        user_id=user_id,
        title="Reward credited",
        body=f"{description} ({amount_sats} sats)",
        kind="reward",
    )
    db.add(notif)

    return True, None


async def debit_demo_balance(
    db: AsyncSession,
    user_id: str,
    amount_sats: int,
    source_type: str,
    source_ref: str,
    description: str,
) -> tuple[bool, str | None]:
    if amount_sats <= 0:
        return False, "Withdrawal amount must be positive"

    user = await db.get(User, user_id)
    if not user:
        return False, "User not found"
    if user.demo_balance_sats < amount_sats:
        return False, "Insufficient demo balance"

    new_balance = user.demo_balance_sats - amount_sats
    user.demo_balance_sats = new_balance

    entry = RewardLedgerEntry(
        user_id=user_id,
        source_type=source_type,
        source_ref=source_ref,
        delta_sats=-amount_sats,
        balance_after_sats=new_balance,
        status="debited",
        description=description,
    )
    db.add(entry)

    tx = RewardTransaction(
        user_id=user_id,
        kind="debit",
        amount_sats=amount_sats,
        balance_after_sats=new_balance,
        status="pending",
        reference=source_ref,
        description=description,
    )
    db.add(tx)

    return True, None
