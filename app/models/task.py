from sqlalchemy import String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from uuid import uuid4

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    referral_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    referred_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    btc_wallet_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    btc_balance: Mapped[float] = mapped_column(Numeric(18, 8), default=0.0)
    total_earned_btc: Mapped[float] = mapped_column(Numeric(18, 8), default=0.0)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tasks: Mapped[list["TaskCompletion"]] = relationship("TaskCompletion", back_populates="user")
    wallet_transactions: Mapped[list["WalletTransaction"]] = relationship("WalletTransaction", back_populates="user")
    withdrawals: Mapped[list["WithdrawalRequest"]] = relationship("WithdrawalRequest", back_populates="user")
