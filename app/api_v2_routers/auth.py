"""
EduBoost V2 — Auth Router
Register, login, and JWT refresh with HTTP-only cookie for refresh token.
"""
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from app.core.envelope_route import EnvelopedRoute
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_application_service import AuthApplicationService  # noqa: F401
from app.api_v2_deps.auth_service import get_auth_application_service  # noqa: F401

from app.api_v2_deps.auth_runtime import AuthRuntimeContext, get_auth_runtime_context
from app.core.config import settings
from app.core.database import get_db
from app.core.refresh_tokens import (
    consume_refresh_token,
    list_user_refresh_sessions,
    revoke_all_refresh_tokens_for_user,
    revoke_refresh_token,
    revoke_refresh_token_jti,
    store_refresh_token,
)
from app.core.security import (
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
    decode_token,
    encrypt_pii,
    get_current_user,
    hash_email,
    hash_password,
    require_parent_or_admin,
    verify_password,
)
from app.core.token_revocation import revoke_token, revoke_user_tokens
from app.services.fourth_estate import FourthEstateService
from app.services.auth_token_claims import build_access_token_claims, merge_refresh_claims
from app.domain.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.models import UserRole
from app.core.rate_limit import limiter


# code_631_650_auth_token_claims_repair
def _canonical_access_claims(user, *, existing_claims=None, extra=None):
    return build_access_token_claims(user, existing_claims=existing_claims, extra=extra)


def _canonical_refresh_claims(existing_claims, user):
    return merge_refresh_claims(existing_claims or {}, user)

def _legacy_refresh_error_response(message: str, status_code: int = 401) -> JSONResponse:
    """Return v2-compatible error with legacy top-level detail for integration tests."""
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": message,
            "data": None,
            "error": {
                "code": "invalid_refresh_token",
                "message": message,
                "field_errors": [],
                "remediation": None,
                "details": None,
            },
            "meta": {
                "api_version": "v2",
                "request_id": None,
                "pagination": None,
            },
        },
    )

router = APIRouter(route_class=EnvelopedRoute, prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "eduboost_refresh"
DEV_GUARDIAN_EMAIL = "dev.guardian" + "@" + "eduboost.local"
DEV_GUARDIAN_PASSWORD = "DevPass1234!"
DEV_GUARDIAN_NAME = "Dev Guardian"
DEV_LEARNER_NAME = "DevLearner"


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def register(
    request: Request,
    body: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_runtime: AuthRuntimeContext = Depends(get_auth_runtime_context),
    auth_service: AuthApplicationService = Depends(get_auth_application_service),
):
    # code_911_950_auth_lifecycle_delegate
    return await auth_service.register(
        legacy_impl=_auth_lifecycle_legacy_register_impl,
            request=request,
            body=body,
            response=response,
            db=db,
            auth_runtime=auth_runtime,
            auth_service=auth_service,
    )

async def _auth_lifecycle_legacy_register_impl(
    request: Request,
    body: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_runtime: AuthRuntimeContext = Depends(get_auth_runtime_context),
    auth_service: AuthApplicationService = Depends(get_auth_application_service),
):
    repo = auth_runtime.guardian_repo
    audit = FourthEstateService(db)

    submitted_email = getattr(body, "email")
    email_hash = hash_email(submitted_email)
    if await repo.get_by_email_hash(email_hash):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    role = UserRole(body.role)
    guardian = await repo.create(
        email_hash=email_hash,
        email_encrypted=encrypt_pii(submitted_email.lower().strip()),
        display_name=body.display_name,
        role=role,
        password_hash=hash_password(body.password),
    )

    refresh = create_refresh_token(guardian.id, guardian.role)
    refresh_payload = decode_token(refresh)
    claims = _canonical_access_claims(
        guardian,
        extra={"refresh_jti": refresh_payload.get("jti"), "refresh_family": refresh_payload.get("family")}
    )
    access = create_access_token(guardian.id, guardian.role, claims)

    await store_refresh_token(refresh)
    _set_refresh_cookie(response, refresh)
    await audit.auth_event("USER_REGISTERED", guardian.id, {"role": role.value})

    return TokenResponse(access_token=access, expires_in=900)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_runtime: AuthRuntimeContext = Depends(get_auth_runtime_context),
    auth_service: AuthApplicationService = Depends(get_auth_application_service),
):
    # code_911_950_auth_lifecycle_delegate
    return await auth_service.login(
        legacy_impl=_auth_lifecycle_legacy_login_impl,
            request=request,
            body=body,
            response=response,
            db=db,
            auth_runtime=auth_runtime,
            auth_service=auth_service,
    )

async def _auth_lifecycle_legacy_login_impl(
    request: Request,
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_runtime: AuthRuntimeContext = Depends(get_auth_runtime_context),
    auth_service: AuthApplicationService = Depends(get_auth_application_service),
):
    repo = auth_runtime.guardian_repo
    audit = FourthEstateService(db)

    submitted_email = getattr(body, "email")
    email_hash = hash_email(submitted_email)
    guardian = await repo.get_by_email_hash(email_hash)
    if not guardian or not verify_password(body.password, guardian.password_hash):
        await audit.auth_event("USER_LOGIN_FAILED", guardian.id if guardian else None, {"email_hash": email_hash})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    refresh = create_refresh_token(guardian.id, guardian.role)
    refresh_payload = decode_token(refresh)
    claims = _canonical_access_claims(
        guardian,
        extra={"refresh_jti": refresh_payload.get("jti"), "refresh_family": refresh_payload.get("family")}
    )
    access = create_access_token(guardian.id, guardian.role, claims)

    await store_refresh_token(refresh)
    _set_refresh_cookie(response, refresh)
    await audit.auth_event("USER_LOGIN", guardian.id)

    return TokenResponse(access_token=access, expires_in=900)


@router.post("/dev-session")
async def create_dev_session(response: Response, db: AsyncSession = Depends(get_db), auth_runtime: AuthRuntimeContext = Depends(get_auth_runtime_context), auth_service: AuthApplicationService = Depends(get_auth_application_service)):
    # code_911_950_auth_lifecycle_delegate
    return await auth_service.create_dev_session(
        legacy_impl=_auth_lifecycle_legacy_create_dev_session_impl,
            response=response,
            db=db,
            auth_runtime=auth_runtime,
            auth_service=auth_service,
    )

async def _auth_lifecycle_legacy_create_dev_session_impl(response: Response, db: AsyncSession = Depends(get_db), auth_runtime: AuthRuntimeContext = Depends(get_auth_runtime_context), auth_service: AuthApplicationService = Depends(get_auth_application_service)):
    """
    Non-production bootstrap endpoint for the local learner flow.
    Creates or reuses a guardian, learner, and active consent so the frontend
    can exercise authenticated V2 routes without hand-editing localStorage.
    """
    if settings.is_production():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    guardian_repo = auth_runtime.guardian_repo
    learner_repo = auth_runtime.learner_repo
    consent_repo = auth_runtime.consent_repo
    audit = FourthEstateService(db)

    email_hash = hash_email(DEV_GUARDIAN_EMAIL)
    guardian = await guardian_repo.get_by_email_hash(email_hash)
    if guardian is None:
        guardian = await guardian_repo.create(
            email_hash=email_hash,
            email_encrypted=encrypt_pii(DEV_GUARDIAN_EMAIL.lower().strip()),
            display_name=DEV_GUARDIAN_NAME,
            role=UserRole.PARENT,
            password_hash=hash_password(DEV_GUARDIAN_PASSWORD),
        )

    existing_profiles = await learner_repo.get_by_guardian(guardian.id) if learner_repo is not None else []
    learner = next((item for item in existing_profiles if item.display_name == DEV_LEARNER_NAME), None)
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
    refresh_payload = decode_token(refresh)
    
    # Include the learner IDs in the access token so authorization logic works
    learner_ids = [str(item.id) for item in existing_profiles]
    if str(learner.id) not in learner_ids:
        learner_ids.append(str(learner.id))
        
    guardian.guardian_learner_ids = learner_ids
    claims = _canonical_access_claims(
        guardian,
        extra={
            "refresh_jti": refresh_payload.get("jti"), 
            "refresh_family": refresh_payload.get("family"),
            "guardian_learner_ids": learner_ids
        }
    )
    access = create_access_token(guardian.id, guardian.role, claims)
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
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def refresh_token(
    request: Request,
    response: Response,
    body: RefreshRequest | None = None,
    db: AsyncSession = Depends(get_db),
    cookie_refresh: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    auth_runtime: AuthRuntimeContext = Depends(get_auth_runtime_context),
    auth_service: AuthApplicationService = Depends(get_auth_application_service),
):
    # code_911_950_auth_lifecycle_delegate
    return await auth_service.refresh(
        legacy_impl=_auth_lifecycle_legacy_refresh_impl,
            request=request,
            response=response,
            body=body,
            db=db,
            cookie_refresh=cookie_refresh,
            auth_runtime=auth_runtime,
            auth_service=auth_service,
    )

async def _auth_lifecycle_legacy_refresh_impl(
    request: Request,
    response: Response,
    body: RefreshRequest | None = None,
    db: AsyncSession = Depends(get_db),
    cookie_refresh: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    auth_runtime: AuthRuntimeContext = Depends(get_auth_runtime_context),
    auth_service: AuthApplicationService = Depends(get_auth_application_service),
):
    token = (body.refresh_token if body else None) or cookie_refresh
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required")

    payload = await consume_refresh_token(token)

    repo = auth_runtime.guardian_repo
    guardian = await repo.get_by_id(payload["sub"])
    if not guardian or not guardian.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account inactive")

    new_refresh = create_refresh_token(guardian.id, guardian.role, family_id=payload.get("family"))
    new_refresh_payload = decode_token(new_refresh)
    
    # Query guardian_learner_ids to ensure they are preserved/updated correctly!
    guardian_learner_ids = await auth_runtime.guardian_learner_ids(guardian.id)
    guardian.guardian_learner_ids = [str(item) for item in guardian_learner_ids]
    
    claims = _canonical_access_claims(
        guardian,
        extra={"refresh_jti": new_refresh_payload.get("jti"), "refresh_family": new_refresh_payload.get("family")}
    )
    access = create_access_token(guardian.id, guardian.role, claims)
    await store_refresh_token(new_refresh)
    await FourthEstateService(db).auth_event("USER_TOKEN_REFRESHED", guardian.id)
    _set_refresh_cookie(response, new_refresh)

    return TokenResponse(access_token=access, expires_in=900)


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        REFRESH_COOKIE,
        token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/api/v2/auth",
    )


@router.get("/sessions")
async def list_sessions(current_user: dict = Depends(get_current_user)):
    """Return active refresh-token sessions for the current user.

    The response intentionally exposes only token metadata, never token values.
    """
    return {"sessions": await list_user_refresh_sessions(current_user["sub"])}

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
    await revoke_refresh_token_jti(current_user.get("refresh_jti"), current_user.get("sub"), current_user.get("refresh_family"))
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
    if user_id:
        await revoke_all_refresh_tokens_for_user(user_id)
    if cookie_refresh:
        await revoke_refresh_token(cookie_refresh)
    
    # Clear refresh cookie
    response.delete_cookie(REFRESH_COOKIE, path="/api/v2/auth")
    
    # Audit the revocation
    audit = FourthEstateService(db)
    await audit.auth_event("USER_TOKENS_REVOKED_ALL", user_id)
    
    return None
