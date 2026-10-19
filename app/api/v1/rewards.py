from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal
from app.deps import get_current_user
from app.models import RewardRule, RewardTransaction, TaskReward, User, WithdrawalRequest

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_user)) -> dict:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "referral_code": current_user.referral_code,
        "btc_wallet_address": current_user.btc_wallet_address,
        "demo_balance_sats": current_user.demo_balance_sats,
        "real_balance_sats": current_user.real_balance_sats,
        "total_rewards_sats": current_user.total_rewards_sats,
        "is_verified": current_user.is_verified,
    }


@router.get("/summary")
async def get_summary(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    task_result = await db.execute(select(TaskReward).where(TaskReward.active.is_(True)))
    rule_result = await db.execute(select(RewardRule).where(RewardRule.active.is_(True)))
    withdrawal_result = await db.execute(
        select(WithdrawalRequest).where(
            WithdrawalRequest.user_id == current_user.id,
            WithdrawalRequest.status.in_(["pending", "processing"]),
        )
    )

    return {
        "demo_balance_sats": current_user.demo_balance_sats,
        "real_balance_sats": current_user.real_balance_sats,
        "total_earned_sats": current_user.total_rewards_sats,
        "active_tasks": len(task_result.scalars().all()),
        "active_rules": len(rule_result.scalars().all()),
        "pending_withdrawals": len(withdrawal_result.scalars().all()),
    }


@router.get("/transactions")
async def list_transactions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(
        select(RewardTransaction)
        .where(RewardTransaction.user_id == current_user.id)
        .order_by(RewardTransaction.created_at.desc())
    )
    return [
        {
            "id": tx.id,
            "kind": tx.kind,
            "amount_sats": tx.amount_sats,
            "status": tx.status,
            "reference": tx.reference,
            "description": tx.description,
            "created_at": tx.created_at.isoformat(),
        }
        for tx in result.scalars().all()
    ]
