from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.core.permissions import Permission, role_has_all_permissions
from src.core.security import decode_token
from src.database import async_session_factory
from src.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, ensuring it is closed after use."""
    async with async_session_factory() as session:
        yield session


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Decode the JWT bearer token and load the corresponding user from the database.

    Raises HTTP 401 if the token is invalid, expired, or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return user


def require_permission(*perms: Permission):
    """Return a FastAPI dependency that verifies the current user's role has all
    of the specified permissions.

    Usage::

        @router.get("/alerts", dependencies=[Depends(require_permission(Permission.ALERTS_VIEW))])
        async def list_alerts(...): ...
    """
    required = set(perms)

    async def _check_permissions(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if not role_has_all_permissions(current_user.role, required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _check_permissions


async def verify_edge_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> str:
    """Validate the API key sent by edge devices.

    Edge devices authenticate via a shared secret in the ``X-API-Key`` header
    rather than JWT tokens.
    """
    if x_api_key != settings.edge_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid edge API key",
        )
    return x_api_key
