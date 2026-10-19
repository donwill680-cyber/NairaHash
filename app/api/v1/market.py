from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal
from app.deps import get_current_user
from app.models import RewardTransaction, User, WithdrawalRequest

router = APIRouter(prefix="/wallet", tags=["wallet"])


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@router.get("/summary")
async def summary(current_user: User = Depends(get_current_user)) -> dict:
    return {
        "demo_balance_sats": current_user.demo_balance_sats,
        "real_balance_sats": current_user.real_balance_sats,
        "total_rewards_sats": current_user.total_rewards_sats,
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


@router.post("/withdraw")
async def request_withdrawal(
    amount_sats: int,
    btc_address: str,
    provider_name: str = "manual",
    note: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if amount_sats <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive")
    if current_user.demo_balance_sats < amount_sats:
        raise HTTPException(status_code=400, detail="Insufficient demo balance")

    request = WithdrawalRequest(
        user_id=current_user.id,
        amount_sats=amount_sats,
        btc_address=btc_address,
        provider_name=provider_name,
        note=note,
        status="pending",
    )
    db.add(request)
    current_user.demo_balance_sats -= amount_sats

    txn = RewardTransaction(
        user_id=current_user.id,
        kind="withdrawal",
        amount_sats=amount_sats,
        balance_after_sats=current_user.demo_balance_sats,
        status="pending",
        reference=request.id,
        description="Withdrawal request initiated",
    )
    db.add(txn)
    await db.commit()
    await db.refresh(request)
    return {"id": request.id, "status": request.status, "amount_sats": request.amount_sats}


@router.get("/withdrawals")
async def list_withdrawals(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(
        select(WithdrawalRequest)
        .where(WithdrawalRequest.user_id == current_user.id)
        .order_by(WithdrawalRequest.created_at.desc())
    )
    return [
        {
            "id": req.id,
            "amount_sats": req.amount_sats,
            "btc_address": req.btc_address,
            "provider_name": req.provider_name,
            "status": req.status,
            "note": req.note,
            "created_at": req.created_at.isoformat(),
        }
        for req in result.scalars().all()
    ]
