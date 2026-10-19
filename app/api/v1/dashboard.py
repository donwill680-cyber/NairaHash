from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user
from app.db import AsyncSessionLocal
from app.models.user import User
from app.models.wallet import WithdrawalRequest, WalletTransaction
from app.schemas import WithdrawalRequestCreate, WithdrawalRequestRead, WalletTransactionRead

router = APIRouter(prefix="/wallet", tags=["wallet"])


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@router.get("/summary")
async def wallet_summary(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    txs = await db.execute(select(WalletTransaction).where(WalletTransaction.user_id == current_user.id).order_by(WalletTransaction.created_at.desc()))
    result = {
        "btc_balance": float(current_user.btc_balance),
        "total_earned_btc": float(current_user.total_earned_btc),
        "transactions": [
            {
                "id": tx.id,
                "kind": tx.kind,
                "amount_btc": float(tx.amount_btc),
                "status": tx.status,
                "reference": tx.reference,
            }
            for tx in txs.scalars().all()
        ],
    }
    return result


@router.post("/withdraw", response_model=WithdrawalRequestRead, status_code=status.HTTP_201_CREATED)
async def request_withdrawal(
    payload: WithdrawalRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WithdrawalRequest:
    if float(current_user.btc_balance) < float(payload.amount_btc):
        raise HTTPException(status_code=400, detail="Insufficient BTC balance")

    request = WithdrawalRequest(
        user_id=current_user.id,
        amount_btc=payload.amount_btc,
        wallet_address=payload.wallet_address,
        note=payload.note,
        status="pending",
    )
    db.add(request)
    current_user.btc_balance = float(current_user.btc_balance) - float(payload.amount_btc)

    tx = WalletTransaction(
        user_id=current_user.id,
        kind="withdrawal",
        amount_btc=payload.amount_btc,
        status="pending",
        reference=request.id,
    )
    db.add(tx)
    await db.commit()
    await db.refresh(request)
    return request


@router.get("/transactions", response_model=list[WalletTransactionRead])
async def list_transactions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[WalletTransaction]:
    result = await db.execute(
        select(WalletTransaction).where(WalletTransaction.user_id == current_user.id).order_by(WalletTransaction.created_at.desc())
    )
    return list(result.scalars().all())
