from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Text, UniqueConstraint
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
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    demo_balance_sats: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    real_balance_sats: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_rewards_sats: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    referral_code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    referred_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    btc_wallet_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    rewards: Mapped[list["UserRewardLedger"]] = relationship("UserRewardLedger", back_populates="user")
    transactions: Mapped[list["RewardTransaction"]] = relationship("RewardTransaction", back_populates="user")
    withdrawals: Mapped[list["WithdrawalRequest"]] = relationship("WithdrawalRequest", back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user")


class RewardRule(Base):
    __tablename__ = "reward_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount_sats: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    interval_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MiningProvider(Base):
    __tablename__ = "mining_providers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    provider_type: Mapped[str] = mapped_column(String(50), default="legitimate", nullable=False)
    reward_rate_sats_per_day: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    api_endpoint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TaskReward(Base):
    __tablename__ = "task_rewards"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reward_sats: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="general")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    provider_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserRewardLedger(Base):
    __tablename__ = "user_reward_ledger"
    __table_args__ = (
        UniqueConstraint("user_id", "source_type", "source_ref", name="uq_user_reward_source"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_ref: Mapped[str] = mapped_column(String(200), nullable=False)
    delta_sats: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after_sats: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="credited", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="rewards")


class RewardTransaction(Base):
    __tablename__ = "reward_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    kind: Mapped[str] = mapped_column(String(50), nullable=False)
    amount_sats: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after_sats: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    external_txid: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="transactions")


class WithdrawalRequest(Base):
    __tablename__ = "withdrawal_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    amount_sats: Mapped[int] = mapped_column(Integer, nullable=False)
    btc_address: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(200), default="manual")
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="withdrawals")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str] = mapped_column(String(50), default="info")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    actor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    actor_role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action: Mapped[str] = mapped_column(String(200), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
