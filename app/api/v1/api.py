from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal
from app.deps import get_current_admin
from app.models import AuditLog, MiningProvider, RewardRule, RewardTransaction, TaskReward, User, WithdrawalRequest

router = APIRouter(prefix="/admin", tags=["admin"])


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@router.get("/overview")
async def overview(current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)) -> dict:
    total_users = await db.execute(select(User))
    total_tasks = await db.execute(select(TaskReward))
    pending_withdrawals = await db.execute(select(WithdrawalRequest).where(WithdrawalRequest.status == "pending"))
    total_providers = await db.execute(select(MiningProvider))
    return {
        "admin_email": current_admin.email,
        "users": len(total_users.scalars().all()),
        "tasks": len(total_tasks.scalars().all()),
        "pending_withdrawals": len(pending_withdrawals.scalars().all()),
        "providers": len(total_providers.scalars().all()),
    }


@router.get("/users")
async def list_users(current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "demo_balance_sats": user.demo_balance_sats,
            "real_balance_sats": user.real_balance_sats,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
        }
        for user in result.scalars().all()
    ]


@router.post("/reward-rules")
async def create_reward_rule(
    name: str,
    rule_type: str,
    amount_sats: int,
    description: str | None = None,
    interval_minutes: int | None = None,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    rule = RewardRule(
        name=name,
        rule_type=rule_type,
        amount_sats=amount_sats,
        description=description,
        interval_minutes=interval_minutes,
        active=True,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return {"id": rule.id, "status": "created"}


@router.post("/tasks")
async def create_task(
    title: str,
    description: str,
    reward_sats: int,
    category: str = "general",
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    task = TaskReward(
        title=title,
        description=description,
        reward_sats=reward_sats,
        category=category,
        active=True,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return {"id": task.id, "status": "created"}


@router.post("/providers")
async def create_provider(
    name: str,
    provider_type: str = "legitimate",
    reward_rate_sats_per_day: int = 0,
    api_endpoint: str | None = None,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    provider = MiningProvider(
        name=name,
        provider_type=provider_type,
        reward_rate_sats_per_day=reward_rate_sats_per_day,
        api_endpoint=api_endpoint,
        enabled=True,
    )
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    return {"id": provider.id, "status": "created"}


@router.post("/withdrawals/{withdrawal_id}/approve")
async def approve_withdrawal(
    withdrawal_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    request = await db.get(WithdrawalRequest, withdrawal_id)
    if not request:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Withdrawal is not pending")

    request.status = "approved"
    request.reviewed_by = current_admin.id
    request.reviewed_at = datetime.utcnow()

    log = AuditLog(
        actor_id=current_admin.id,
        actor_role=current_admin.role,
        action="approve_withdrawal",
        entity_type="withdrawal_request",
        entity_id=request.id,
        details=f"Approved withdrawal of {request.amount_sats} sats",
    )
    db.add(log)
    await db.commit()
    return {"status": "approved", "withdrawal_id": request.id}


@router.get("/transactions")
async def list_transactions(current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(RewardTransaction).order_by(RewardTransaction.created_at.desc()))
    return [
        {
            "id": tx.id,
            "user_id": tx.user_id,
            "kind": tx.kind,
            "amount_sats": tx.amount_sats,
            "status": tx.status,
            "description": tx.description,
            "created_at": tx.created_at.isoformat(),
        }
        for tx in result.scalars().all()
    ]
