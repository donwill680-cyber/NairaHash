from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db import AsyncSessionLocal
from app.models import User
from app.core.security import OAuth2PasswordBearerScheme


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    token: str = Depends(OAuth2PasswordBearerScheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    subject = decode_access_token(token)
    result = await db.execute(select(User).where(User.email == subject))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account inactive")
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
