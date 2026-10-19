from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ledger import ensure_unique_reward_credit
from app.models import RewardRule, User


async def get_or_create_daily_rule(db: AsyncSession) -> RewardRule:
    result = await db.execute(select(RewardRule).where(RewardRule.rule_type == "daily_reward", RewardRule.active.is_(True)))
    rule = result.scalar_one_or_none()
    if rule:
        return rule
    rule = RewardRule(
        name="Daily reward",
        rule_type="daily_reward",
        amount_sats=5000,
        description="Daily reward for active users",
        interval_minutes=60 * 24,
        active=True,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


async def process_daily_rewards_for_user(db: AsyncSession, user: User) -> bool:
    rule = await get_or_create_daily_rule(db)
    now = datetime.utcnow()
    last_daily = await db.execute(
        select(UserRewardLedger).where(
            UserRewardLedger.user_id == user.id,
            UserRewardLedger.source_type == "daily_reward",
        ).order_by(UserRewardLedger.created_at.desc())
    )
    latest = last_daily.scalar_one_or_none()
    if latest and now - latest.created_at.replace(tzinfo=None) < timedelta(days=1):
        return False

    from app.models import UserRewardLedger

    ok, _ = await ensure_unique_reward_credit(
        db,
        user.id,
        "daily_reward",
        f"daily-{now.date()}",
        rule.amount_sats,
        "Daily reward credited",
    )
    return ok


async def process_task_reward(db: AsyncSession, user_id: str, task_id: str, reward_sats: int) -> bool:
    from app.models import UserRewardLedger

    ok, _ = await ensure_unique_reward_credit(
        db,
        user_id,
        "task_reward",
        task_id,
        reward_sats,
        "Task reward credited",
    )
    return ok
