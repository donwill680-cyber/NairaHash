from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user
from app.db import AsyncSessionLocal
from app.models.task import Task, TaskCompletion
from app.models.user import User
from app.schemas import TaskCompletionRequest, TaskCreate, TaskRead

router = APIRouter(prefix="/tasks", tags=["tasks"])


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@router.get("", response_model=list[TaskRead])
async def list_tasks(db: AsyncSession = Depends(get_db)) -> list[Task]:
    result = await db.execute(select(Task).where(Task.is_active.is_(True)).order_by(Task.created_at.desc()))
    return list(result.scalars().all())


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> Task:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create tasks")

    task = Task(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        reward_btc=payload.reward_btc,
        difficulty=payload.difficulty,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/{task_id}/complete", status_code=status.HTTP_201_CREATED)
async def complete_task(
    task_id: str,
    payload: TaskCompletionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    existing = await db.execute(
        select(TaskCompletion).where(TaskCompletion.user_id == current_user.id, TaskCompletion.task_id == task_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Task already completed")

    completion = TaskCompletion(
        user_id=current_user.id,
        task_id=task_id,
        completion_proof=payload.completion_proof,
        reward_paid=False,
    )
    db.add(completion)
    current_user.total_earned_btc = float(current_user.total_earned_btc) + float(task.reward_btc)
    current_user.btc_balance = float(current_user.btc_balance) + float(task.reward_btc)

    await db.commit()
    return {"message": "Task completed successfully", "reward_btc": float(task.reward_btc)}
