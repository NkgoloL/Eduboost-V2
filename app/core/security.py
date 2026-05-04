"""
EduBoost V2 — Security Helpers
JWT creation/verification, bcrypt password hashing, RBAC role enforcement.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.core.token_revocation import is_token_revoked, is_user_revoked
from app.models import UserRole

Role = UserRole
TokenPayload = dict[str, Any]

# ── Password hashing ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    secret = plain.encode("utf-8")
    return bcrypt.hashpw(secret, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def hash_email(email: str) -> str:
    """Deterministic SHA-256 hash of an email for lookup (POPIA-safe)."""
    return hashlib.sha256(email.lower().strip().encode()).hexdigest()


# ── Token schemas ─────────────────────────────────────────────────────────────
def create_access_token(subject: str, role: UserRole, extra: dict[str, Any] | None = None) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": datetime.now(UTC),
        "jti": str(uuid.uuid4()),
        "type": "access",
        **(extra or {}),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str, role: UserRole) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": datetime.now(UTC),
        "jti": str(uuid.uuid4()),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ── FastAPI dependency helpers ────────────────────────────────────────────────
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(credentials.credentials)
    
    # Check if token type is correct
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token cannot be used here")
    
    # Check if token has been revoked (by JTI)
    jti = payload.get("jti")
    if jti and await is_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user's all tokens have been revoked
    user_id = payload.get("sub")
    if user_id and await is_user_revoked(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User tokens have been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def require_roles(*roles: UserRole):
    """Dependency factory: enforce that the caller has one of the specified roles."""

    def _inner(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {[r.value for r in roles]}",
            )
        return current_user

    return _inner


require_role = require_roles
require_admin = require_roles(UserRole.ADMIN)
require_parent_or_admin = require_roles(UserRole.PARENT, UserRole.ADMIN)
require_teacher_or_admin = require_roles(UserRole.TEACHER, UserRole.ADMIN)

__all__ = [
    "Role",
    "TokenPayload",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "get_current_user",
    "hash_email",
    "hash_password",
    "require_admin",
    "require_parent_or_admin",
    "require_role",
    "require_roles",
    "require_teacher_or_admin",
    "verify_password",
]
