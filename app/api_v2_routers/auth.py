"""
EduBoost V2 — Auth Router
Register, login, and JWT refresh with HTTP-only cookie for refresh token.
"""
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status  # noqa: F401
from fastapi.responses import JSONResponse
from app.core.envelope_route import EnvelopedRoute
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_application_service import AuthApplicationService  # noqa: F401
from app.api_v2_deps.auth_service import get_auth_application_service  # noqa: F401

from app.api_v2_deps.auth_runtime import AuthRuntimeContext, get_auth_runtime_context
from app.core.config import settings
from app.core.database import get_db
from app.core.refresh_tokens import (  # noqa: F401
    consume_refresh_token,
    list_user_refresh_sessions,
    revoke_all_refresh_tokens_for_user,
    revoke_refresh_token,
    revoke_refresh_token_jti,
    store_refresh_token,
)
from app.core.security import (  # noqa: F401
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
from app.services.auth_token_claims import build_access_token_claims, merge_refresh_claims
from app.domain.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.models import UserRole  # noqa: F401
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
):
    # code_911_950_auth_lifecycle_delegate
    return await auth_service.register(
            request=request,
            body=body,
            response=response,
            db=db,
            auth_runtime=auth_runtime,
    )

@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_runtime: AuthRuntimeContext = Depends(get_auth_runtime_context),
):
    # code_911_950_auth_lifecycle_delegate
    return await auth_service.login(
            request=request,
            body=body,
            response=response,
            db=db,
            auth_runtime=auth_runtime,
    )

@router.post("/dev-session")
async def create_dev_session(
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_runtime: AuthRuntimeContext = Depends(get_auth_runtime_context),
):
    """
    Non-production bootstrap endpoint for the local learner flow.
    Creates or reuses a guardian, learner, and active consent so the frontend
    can exercise authenticated V2 routes without hand-editing localStorage.
    DEV_SESSION_BOOTSTRAPPED
    """
    if settings.is_production():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    # code_911_950_auth_lifecycle_delegate
    return await auth_service.create_dev_session(
            response=response,
            db=db,
            auth_runtime=auth_runtime,
    )

@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def refresh_token(
    request: Request,
    response: Response,
    body: RefreshRequest | None = None,
    db: AsyncSession = Depends(get_db),
    cookie_refresh: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    auth_runtime: AuthRuntimeContext = Depends(get_auth_runtime_context),
):
    # code_911_950_auth_lifecycle_delegate
    return await auth_service.refresh(
            request=request,
            response=response,
            body=body,
            db=db,
            cookie_refresh=cookie_refresh,
            auth_runtime=auth_runtime,
    )

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
    auth_service: AuthApplicationService = Depends(get_auth_application_service),
):
    return await auth_service.logout(response=response, current_user=current_user, db=db, cookie_refresh=cookie_refresh)


@router.post("/revoke-all", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_all_tokens(
    response: Response,
    current_user: dict = Depends(require_parent_or_admin),
    db: AsyncSession = Depends(get_db),
    cookie_refresh: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    auth_service: AuthApplicationService = Depends(get_auth_application_service),
):
    return await auth_service.revoke_all_tokens(response=response, current_user=current_user, db=db, cookie_refresh=cookie_refresh)
