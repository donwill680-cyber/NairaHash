from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal
from app.deps import get_current_user
from app.models.task import Task, TaskCompletion
from app.models.user import User
from app.models.wallet import WithdrawalRequest
from app.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    active_tasks = await db.execute(select(Task).where(Task.is_active.is_(True)))
    completions = await db.execute(select(TaskCompletion).where(TaskCompletion.user_id == current_user.id))
    withdrawals = await db.execute(select(WithdrawalRequest).where(WithdrawalRequest.user_id == current_user.id, WithdrawalRequest.status == "pending"))

    return {
        "total_earned_btc": float(current_user.total_earned_btc),
        "btc_balance": float(current_user.btc_balance),
        "active_tasks": len(active_tasks.scalars().all()),
        "total_referrals": 0,
        "pending_withdrawals": len(withdrawals.scalars().all()),
    }


@router.get("/me")
async def current_user_profile(current_user: User = Depends(get_current_user)) -> dict:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "referral_code": current_user.referral_code,
        "btc_wallet_address": current_user.btc_wallet_address,
        "btc_balance": float(current_user.btc_balance),
        "total_earned_btc": float(current_user.total_earned_btc),
        "is_admin": current_user.is_admin,
    }
