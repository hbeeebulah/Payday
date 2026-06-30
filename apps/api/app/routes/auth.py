"""Authentication routes — register, login, and current user."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_employer, get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import User
from app.models.enums import UserRole
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    StaffLookupRequest,
    StaffLookupResponse,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_response(user: User) -> AuthResponse:
    token = create_access_token(subject=user.id, role=user.role.value)
    return AuthResponse(access_token=token, user=UserRead.model_validate(user))


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        email=str(payload.email).lower(),
        phone=payload.phone.strip(),
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    result = await db.execute(select(User).where(User.email == str(payload.email).lower()))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return _auth_response(user)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/staff/lookup", response_model=StaffLookupResponse)
async def lookup_staff_by_email(
    payload: StaffLookupRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_employer),
) -> StaffLookupResponse:
    """Find a registered staff account by email (employer onboarding)."""
    email = str(payload.email).lower()
    result = await db.execute(
        select(User).where(User.email == email, User.role == UserRole.STAFF)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return StaffLookupResponse(found=False, user=None)
    return StaffLookupResponse(found=True, user=UserRead.model_validate(user))
