from sqlalchemy import String, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from uuid import uuid4

from app.db import Base


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    referrer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    referred_user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    bonus_btc: Mapped[float] = mapped_column(Numeric(18, 8), default=0.0)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
