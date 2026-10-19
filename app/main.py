from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=120)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    referral_code: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    role: str = "user"
    referral_code: str
    btc_wallet_address: str | None = None
    demo_balance_sats: int = 0
    real_balance_sats: int = 0
    total_rewards_sats: int = 0
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RewardRuleCreate(BaseModel):
    name: str
    rule_type: str
    amount_sats: int = Field(..., ge=0)
    description: str | None = None
    interval_minutes: int | None = Field(None, ge=1)
