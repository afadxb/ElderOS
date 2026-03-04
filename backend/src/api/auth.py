from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, get_current_user
from src.core.security import create_access_token
from src.models.user import User
from src.schemas.auth import LoginRequest, LoginResponse, UserResponse
from src.services.auth_service import authenticate

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate(db, body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id, user.role)
    return LoginResponse(
        user=UserResponse.model_validate(user),
        token=token,
    )


@router.post("/logout")
async def logout():
    """Stateless JWT — logout is handled client-side by discarding the token."""
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post("/login-by-role", response_model=LoginResponse)
async def login_by_role(role: str, db: AsyncSession = Depends(get_db)):
    """Dev-mode endpoint: login as a role without credentials."""
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.role == role).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"No user with role '{role}'")
    token = create_access_token(user.id, user.role)
    return LoginResponse(
        user=UserResponse.model_validate(user),
        token=token,
    )
