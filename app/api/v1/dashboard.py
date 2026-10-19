from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import create_access_token, generate_referral_code, hash_password, verify_password
from app.db import AsyncSessionLocal
from app.models import User
from app.schemas import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    code = payload.referral_code or generate_referral_code(payload.email)
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        referral_code=code,
        role="user",
        btc_wallet_address="bc1qexamplewalletaddress",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login_json(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.email)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login-form")
async def login_form(username: str, password: str, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(User).where(User.email == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.email)
    return {"access_token": token, "token_type": "bearer"}
