import asyncio

from sqlalchemy import select

from app.config import settings
from app.core.security import hash_password
from app.db import AsyncSessionLocal
from app.models import User


async def seed_admin() -> None:
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(User).where(User.email == settings.admin_email))
        user = existing.scalar_one_or_none()

        if user is not None:
            print(f"Admin already exists: {user.email}")
            return

        admin = User(
            email=settings.admin_email,
            full_name="NairaHash Admin",
            password_hash=hash_password(settings.admin_password),
            role="admin",
            is_active=True,
            referral_code="NAIRADMIN",
        )

        db.add(admin)
        await db.commit()
        print(f"Admin created successfully: {settings.admin_email}")
        print(f"Admin login URL: {settings.app_url}/admin/login")


if __name__ == "__main__":
    asyncio.run(seed_admin())
