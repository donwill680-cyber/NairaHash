from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ledger import credit_demo_reward
from app.db import AsyncSessionLocal
from app.deps import get_current_user
from app.models import RewardRule, TaskReward, User, RewardLedgerEntry

router = APIRouter(prefix="/rewards", tags=["rewards"])


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@router.get("/rules")
async def list_reward_rules(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(RewardRule).where(RewardRule.active.is_(True)))
    return [
        {
            "id": rule.id,
            "name": rule.name,
            "rule_type": rule.rule_type,
            "amount_sats": rule.amount_sats,
            "description": rule.description,
            "interval_minutes": rule.interval_minutes,
        }
        for rule in result.scalars().all()
    ]


@router.get("/tasks")
async def list_tasks(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(TaskReward).where(TaskReward.active.is_(True)))
    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "reward_sats": task.reward_sats,
            "category": task.category,
        }
        for task in result.scalars().all()
    ]


@router.post("/claim-daily")
async def claim_daily(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(
        select(RewardRule).where(RewardRule.rule_type == "daily_reward", RewardRule.active.is_(True))
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Daily reward rule is not configured")

    source_ref = f"daily_reward:{current_user.id}:{__import__('datetime').date.today().isoformat()}"
    duplicate = await db.execute(
        select(RewardLedgerEntry).where(
            RewardLedgerEntry.user_id == current_user.id,
            RewardLedgerEntry.source_type == "daily_reward",
            RewardLedgerEntry.source_ref == source_ref,
        )
    )
    if duplicate.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Daily reward already claimed")

    ok, error = await credit_demo_reward(
        db=db,
        user_id=current_user.id,
        amount_sats=rule.amount_sats,
        source_type="daily_reward",
        source_ref=source_ref,
        description="Daily reward credited",
    )
    if not ok:
        raise HTTPException(status_code=400, detail=error or "Unable to credit reward")

    await db.commit()
    return {"status": "credited", "amount_sats": rule.amount_sats}


@router.post("/claim-task/{task_id}")
async def claim_task(task_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    task = await db.get(TaskReward, task_id)
    if not task or not task.active:
        raise HTTPException(status_code=404, detail="Task not found")

    ok, error = await credit_demo_reward(
        db=db,
        user_id=current_user.id,
        amount_sats=task.reward_sats,
        source_type="task_reward",
        source_ref=task_id,
        description=f"Task reward: {task.title}",
    )
    if not ok:
        raise HTTPException(status_code=400, detail=error or "Task already claimed")

    await db.commit()
    return {"status": "credited", "amount_sats": task.reward_sats, "task_title": task.title}
