"""
EduBoost V2 — Auth Router
Register, login, and JWT refresh with HTTP-only cookie for refresh token.
"""
from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.refresh_tokens import (
    consume_refresh_token,
    revoke_refresh_token,
    revoke_refresh_token_jti,
    store_refresh_token,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    hash_email,
    hash_password,
    require_parent_or_admin,
    verify_password,
)
from app.core.token_revocation import revoke_token, revoke_user_tokens
from app.domain.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.models import UserRole
from app.repositories.repositories import ConsentRepository, GuardianRepository, LearnerRepository
from app.core.rate_limit import limiter


router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "eduboost_refresh"
DEV_GUARDIAN_EMAIL = "dev.guardian@eduboost.local"
DEV_GUARDIAN_PASSWORD = "DevPass123!"
DEV_GUARDIAN_NAME = "Dev Guardian"
DEV_LEARNER_NAME = "DevLearner"


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
async def register(request: Request, body: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    repo = GuardianRepository(db)
    audit = FourthEstateService(db)

    submitted_email = getattr(body, "email")
    email_hash = hash_email(submitted_email)
    if await repo.get_by_email_hash(email_hash):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    role = UserRole(body.role)
    guardian = await repo.create(
        email_hash=email_hash,
        email_encrypted=submitted_email,
        display_name=body.display_name,
        role=role,
        password_hash=hash_password(body.password),
    )

    refresh = create_refresh_token(guardian.id, guardian.role)
    access = create_access_token(guardian.id, guardian.role, {"refresh_jti": decode_token(refresh).get("jti")})

    await store_refresh_token(refresh)
    _set_refresh_cookie(response, refresh)
    await audit.auth_event("USER_REGISTERED", guardian.id, {"role": role.value})

    return TokenResponse(access_token=access, expires_in=900)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/hour")
async def login(request: Request, body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    repo = GuardianRepository(db)
    audit = FourthEstateService(db)

    submitted_email = getattr(body, "email")
    email_hash = hash_email(submitted_email)
    guardian = await repo.get_by_email_hash(email_hash)
    if not guardian or not verify_password(body.password, guardian.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    refresh = create_refresh_token(guardian.id, guardian.role)
    access = create_access_token(guardian.id, guardian.role, {"refresh_jti": decode_token(refresh).get("jti")})

    await store_refresh_token(refresh)
    _set_refresh_cookie(response, refresh)
    await audit.auth_event("USER_LOGIN", guardian.id)

    return TokenResponse(access_token=access, expires_in=900)


@router.post("/dev-session")
async def create_dev_session(response: Response, db: AsyncSession = Depends(get_db)):
    """
    Non-production bootstrap endpoint for the local learner flow.
    Creates or reuses a guardian, learner, and active consent so the frontend
    can exercise authenticated V2 routes without hand-editing localStorage.
    """
    if settings.is_production():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    guardian_repo = GuardianRepository(db)
    learner_repo = LearnerRepository(db)
    consent_repo = ConsentRepository(db)
    audit = FourthEstateService(db)

    email_hash = hash_email(DEV_GUARDIAN_EMAIL)
    guardian = await guardian_repo.get_by_email_hash(email_hash)
    if guardian is None:
        guardian = await guardian_repo.create(
            email_hash=email_hash,
            email_encrypted=DEV_GUARDIAN_EMAIL,
            display_name=DEV_GUARDIAN_NAME,
            role=UserRole.PARENT,
            password_hash=hash_password(DEV_GUARDIAN_PASSWORD),
        )

    learners = await learner_repo.get_by_guardian(guardian.id)
    learner = next((item for item in learners if item.display_name == DEV_LEARNER_NAME), None)
    if learner is None:
        learner = await learner_repo.create(
            guardian_id=guardian.id,
            display_name=DEV_LEARNER_NAME,
            grade=3,
            language="en",
        )

    if await consent_repo.get_active(learner.id) is None:
        await consent_repo.create(
            guardian_id=guardian.id,
            learner_id=learner.id,
            policy_version="1.0",
        )

    refresh = create_refresh_token(guardian.id, guardian.role)
    access = create_access_token(guardian.id, guardian.role, {"refresh_jti": decode_token(refresh).get("jti")})
    await store_refresh_token(refresh)
    _set_refresh_cookie(response, refresh)
    await audit.auth_event("DEV_SESSION_BOOTSTRAPPED", guardian.id, {"learner_id": learner.id})

    return {
        "access_token": access,
        "token_type": "bearer",
        "expires_in": 900,
        "guardian_id": guardian.id,
        "learner": {
            "learner_id": learner.id,
            "id": learner.id,
            "display_name": learner.display_name,
            "nickname": learner.display_name,
            "grade": learner.grade,
            "language": getattr(learner.language, "value", learner.language),
            "avatar": 0,
            "streak_days": learner.streak_days,
        },
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    body: RefreshRequest | None = None,
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

    new_refresh = create_refresh_token(guardian.id, guardian.role)
    access = create_access_token(guardian.id, guardian.role, {"refresh_jti": decode_token(new_refresh).get("jti")})
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
        path="/api/v2/auth",
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cookie_refresh: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
):
    """
    Revoke the current access token and clear the refresh token cookie.
    """
    # Revoke this specific access token (by JTI)
    jti = current_user.get("jti")
    exp = current_user.get("exp")
    if jti and exp:
        await revoke_token(jti, exp)
    await revoke_refresh_token_jti(current_user.get("refresh_jti"))
    if cookie_refresh:
        await revoke_refresh_token(cookie_refresh)
    
    # Clear refresh cookie
    response.delete_cookie(REFRESH_COOKIE, path="/api/v2/auth")
    
    # Audit the logout
    audit = FourthEstateService(db)
    await audit.auth_event("USER_LOGOUT", current_user.get("sub"))
    
    return None


@router.post("/revoke-all", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_all_tokens(
    response: Response,
    current_user: dict = Depends(require_parent_or_admin),
    db: AsyncSession = Depends(get_db),
    cookie_refresh: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
):
    """
    Revoke ALL tokens for the current user (logout from all devices).
    Useful for security incidents or password changes.
    """
    user_id = current_user.get("sub")
    await revoke_user_tokens(user_id)
    if cookie_refresh:
        await revoke_refresh_token(cookie_refresh)
    
    # Clear refresh cookie
    response.delete_cookie(REFRESH_COOKIE, path="/api/v2/auth")
    
    # Audit the revocation
    audit = FourthEstateService(db)
    await audit.auth_event("USER_TOKENS_REVOKED_ALL", user_id)
    
    return None
