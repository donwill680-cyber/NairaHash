from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=120)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    referral_code: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    referral_code: str
    btc_wallet_address: Optional[str] = None
    btc_balance: float = 0.0
    total_earned_btc: float = 0.0
    is_admin: bool = False
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TaskCreate(BaseModel):
    title: str
    description: str
    category: str
    reward_btc: float = 0.0
    difficulty: str = "easy"


class TaskRead(TaskCreate):
    id: str
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class TaskCompletionRequest(BaseModel):
    completion_proof: Optional[str] = None


class WalletTransactionRead(BaseModel):
    id: str
    kind: str
    amount_btc: float
    fiat_amount_ngn: Optional[float] = None
    status: str
    reference: Optional[str] = None
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class WithdrawalRequestCreate(BaseModel):
    amount_btc: float = Field(..., gt=0)
    wallet_address: str = Field(..., min_length=26)
    note: Optional[str] = None


class WithdrawalRequestRead(BaseModel):
    id: str
    amount_btc: float
    wallet_address: str
    status: str
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DashboardSummary(BaseModel):
    total_earned_btc: float
    btc_balance: float
    active_tasks: int
    total_referrals: int
    pending_withdrawals: int
