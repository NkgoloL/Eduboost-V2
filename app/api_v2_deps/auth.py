"""
EduBoost V2 — Authentication Context and Dependencies

Canonical authentication context for FastAPI v2 routers.
Normalizes JWT claims into a typed structure with convenience methods.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.config import settings
from app.core.security import decode_token, get_current_user as get_current_user_payload
from app.core.token_revocation import is_token_revoked, is_user_revoked
from app.models import UserRole


class TokenType(str, Enum):
    """Token type enumeration."""
    ACCESS = "access"
    REFRESH = "refresh"


class AuthContext(BaseModel):
    """
    Normalized authentication context from JWT claims.
    
    This class provides a typed interface to JWT claims with convenience
    methods for common authorization checks.
    """

    user_id: str
    guardian_id: str | None = None
    learner_id: str | None = None
    roles: list[UserRole] = Field(default_factory=list)
    token_type: TokenType
    raw_claims: dict[str, Any]

    # Timestamps from token
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    jti: str  # JWT ID for revocation

    # Issuer and audience (for environment validation)
    issuer: str | None = None
    audience: str | None = None

    class Config:
        use_enum_values = False

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return UserRole.ADMIN in self.roles

    @property
    def is_parent(self) -> bool:
        """Check if user has parent role."""
        return UserRole.PARENT in self.roles

    @property
    def is_teacher(self) -> bool:
        """Check if user has teacher role."""
        return UserRole.TEACHER in self.roles

    @property
    def is_student(self) -> bool:
        """Check if user has student role."""
        return UserRole.STUDENT in self.roles

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return self.expires_at is not None and datetime.now(timezone.utc) > self.expires_at

    @property
    def subject(self) -> str:
        """Get the subject (user_id) of the token."""
        return self.user_id


def _parse_roles(role: Any) -> list[UserRole]:
    """
    Parse role claim into list of UserRole enums.
    
    Handles:
    - Single UserRole enum
    - Single string value
    - List of UserRole enums
    - List of strings
    """
    if role is None:
        return []

    if isinstance(role, list):
        return [UserRole(r) if isinstance(r, str) else r for r in role]

    if isinstance(role, str):
        return [UserRole(role)]

    if isinstance(role, UserRole):
        return [role]

    return []


def _validate_issuer_and_audience(claims: dict[str, Any]) -> None:
    """
    Validate issuer and audience claims if present.
    
    This prevents token replay across environments (e.g., staging to production).
    """
    issuer = claims.get("iss")
    audience = claims.get("aud")

    # If claims include iss/aud, validate them
    if issuer is not None:
        expected_issuer = settings.APP_BASE_URL.rstrip("/")
        if issuer != expected_issuer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token issuer: expected {expected_issuer}, got {issuer}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    if audience is not None:
        expected_audience = "eduboost-api"
        if audience != expected_audience:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token audience: expected {expected_audience}, got {audience}",
                headers={"WWW-Authenticate": "Bearer"},
            )


def _claims_to_auth_context(claims: dict[str, Any]) -> AuthContext:
    """
    Convert raw JWT claims to typed AuthContext.
    
    This function normalizes inconsistent claim formats and provides
    a stable interface for authorization logic.
    """
    # Extract required claims
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing required 'sub' claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Parse token type
    token_type_str = claims.get("type", "access")
    try:
        token_type = TokenType(token_type_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type: {token_type_str}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Parse roles
    roles = _parse_roles(claims.get("role"))

    # Parse timestamps
    issued_at = claims.get("iat")
    if isinstance(issued_at, (int, float)):
        issued_at = datetime.fromtimestamp(issued_at, tz=timezone.utc)
    elif isinstance(issued_at, datetime):
        issued_at = issued_at
    else:
        issued_at = datetime.now(timezone.utc)

    expires_at = claims.get("exp")
    if isinstance(expires_at, (int, float)):
        expires_at = datetime.fromtimestamp(expires_at, tz=timezone.utc)
    elif isinstance(expires_at, datetime):
        expires_at = expires_at
    else:
        expires_at = datetime.now(timezone.utc)

    # Extract JTI
    jti = claims.get("jti", "")

    # Extract optional guardian/learner IDs
    guardian_id = claims.get("guardian_id")
    learner_id = claims.get("learner_id")

    # Extract issuer and audience
    issuer = claims.get("iss")
    audience = claims.get("aud")

    return AuthContext(
        user_id=str(user_id),
        guardian_id=str(guardian_id) if guardian_id else None,
        learner_id=str(learner_id) if learner_id else None,
        roles=roles,
        token_type=token_type,
        raw_claims=claims,
        issued_at=issued_at,
        expires_at=expires_at,
        jti=jti,
        issuer=issuer,
        audience=audience,
    )


# ── FastAPI dependencies ────────────────────────────────────────────────────────

_bearer = HTTPBearer(auto_error=False)


async def get_auth_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> AuthContext:
    """
    FastAPI dependency to extract and normalize JWT claims into AuthContext.
    
    This replaces the legacy get_current_user which returned a raw dict.
    All new routes should use this dependency instead.
    
    Raises:
        HTTPException 401: If token is missing, invalid, expired, or revoked
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode token
    try:
        claims = decode_token(credentials.credentials)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    # Validate issuer and audience if present
    _validate_issuer_and_audience(claims)

    # Check token type
    token_type = claims.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token cannot be used here",
        )

    # Check revocation by JTI
    jti = claims.get("jti")
    if jti and await is_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check user-level revocation
    user_id = claims.get("sub")
    if user_id and await is_user_revoked(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User tokens have been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert to AuthContext
    return _claims_to_auth_context(claims)


async def require_auth_context(
    current_user: dict[str, Any] = Depends(get_current_user_payload),
) -> AuthContext:
    """Canonical dependency alias for routes that require authenticated context.

    This intentionally builds on the legacy dict payload dependency so router
    tests that override `get_current_user` keep working during the migration.
    """
    _validate_issuer_and_audience(current_user)
    return _claims_to_auth_context(current_user)


async def get_auth_context_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> AuthContext | None:
    """
    Optional version of get_auth_context.
    
    Returns None if no authorization header is present.
    """
    if credentials is None:
        return None
    return await get_auth_context(credentials)


# ── Backward compatibility layer ───────────────────────────────────────────────────

async def get_current_user_compat(
    auth: AuthContext = Depends(get_auth_context),
) -> dict[str, Any]:
    """
    Backward compatibility wrapper for existing code expecting dict.
    
    This allows gradual migration from dict-based auth to AuthContext.
    New code should use get_auth_context directly.
    
    Deprecated: Use get_auth_context instead.
    """
    return auth.raw_claims


# ── Role-based dependencies ───────────────────────────────────────────────────────

def require_roles(*roles: UserRole):
    """
    Dependency factory: enforce that the caller has one of the specified roles.
    
    Usage:
        @router.get("/admin")
        async def admin_endpoint(auth: AuthContext = Depends(require_roles(UserRole.ADMIN))):
            ...
    """

    def _inner(auth: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if not any(role in auth.roles for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {[r.value for r in roles]}",
            )
        return auth

    return _inner


# Convenience role dependencies
require_admin = require_roles(UserRole.ADMIN)
require_parent_or_admin = require_roles(UserRole.PARENT, UserRole.ADMIN)
require_teacher_or_admin = require_roles(UserRole.TEACHER, UserRole.ADMIN)
require_student_or_admin = require_roles(UserRole.STUDENT, UserRole.ADMIN)


__all__ = [
    "AuthContext",
    "TokenType",
    "get_auth_context",
    "get_auth_context_optional",
    "get_current_user_compat",
    "require_auth_context",
    "require_roles",
    "require_admin",
    "require_parent_or_admin",
    "require_teacher_or_admin",
    "require_student_or_admin",
]
