from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import verify_password
from src.models.user import User


async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
    """Verify email/password credentials. Returns User or None."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    return await db.get(User, user_id)
