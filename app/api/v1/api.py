from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal
from app.deps import get_current_admin
from app.models.task import Task
from app.models.user import User
from app.models.wallet import WithdrawalRequest

router = APIRouter(prefix="/admin", tags=["admin"])


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@router.get("/overview")
async def admin_overview(db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)) -> dict:
    total_users = await db.execute(select(User))
    total_tasks = await db.execute(select(Task))
    pending_withdrawals = await db.execute(select(WithdrawalRequest).where(WithdrawalRequest.status == "pending"))
    return {
        "admin": current_admin.email,
        "total_users": len(total_users.scalars().all()),
        "total_tasks": len(total_tasks.scalars().all()),
        "pending_withdrawals": len(pending_withdrawals.scalars().all()),
    }
