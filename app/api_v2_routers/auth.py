"""
EduBoost V2 — Auth Router
Register, login, and JWT refresh with HTTP-only cookie for refresh token.
"""
from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.refresh_tokens import consume_refresh_token, store_refresh_token
from app.core.security import Role, create_access_token, create_refresh_token, hash_email, hash_password, verify_password
from app.core.config import settings
from app.domain.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.repositories.repositories import GuardianRepository
from app.services.fourth_estate import FourthEstateService

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "eduboost_refresh"


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    repo = GuardianRepository(db)
    audit = FourthEstateService(db)

    email_hash = hash_email(body.email)
    if await repo.get_by_email_hash(email_hash):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    guardian = await repo.create(
        email_hash=email_hash,
        email_encrypted=body.email,  # In production: AES-encrypt before storing
        display_name=body.display_name,
        role=body.role,
        password_hash=hash_password(body.password),
    )

    access = create_access_token(guardian.id, Role(guardian.role))
    refresh = create_refresh_token(guardian.id, Role(guardian.role))

    await store_refresh_token(refresh)
    _set_refresh_cookie(response, refresh)
    await audit.auth_event("USER_REGISTERED", guardian.id, {"role": body.role})

    return TokenResponse(access_token=access, expires_in=900)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    repo = GuardianRepository(db)
    audit = FourthEstateService(db)

    email_hash = hash_email(body.email)
    guardian = await repo.get_by_email_hash(email_hash)
    if not guardian or not verify_password(body.password, guardian.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access = create_access_token(guardian.id, Role(guardian.role))
    refresh = create_refresh_token(guardian.id, Role(guardian.role))

    await store_refresh_token(refresh)
    _set_refresh_cookie(response, refresh)
    await audit.auth_event("USER_LOGIN", guardian.id)

    return TokenResponse(access_token=access, expires_in=900)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest | None = None,
    response: Response,
    db: AsyncSession = Depends(get_db),
    cookie_refresh: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
):
    token = (body.refresh_token if body else None) or cookie_refresh
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required")

    payload = await consume_refresh_token(token)

    repo = GuardianRepository(db)
    guardian = await repo.get_by_id(payload["sub"])
    if not guardian or not guardian.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account inactive")

    access = create_access_token(guardian.id, Role(guardian.role))
    new_refresh = create_refresh_token(guardian.id, Role(guardian.role))
    await store_refresh_token(new_refresh)
    _set_refresh_cookie(response, new_refresh)

    return TokenResponse(access_token=access, expires_in=900)


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        REFRESH_COOKIE,
        token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/api/v2/auth/refresh",
    )
