"""V2 RBAC and security dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth_service import AuthService, Role

bearer = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]
) -> dict:
    """Dependency to decode and validate a JWT."""
    try:
        # Note: In a full production app, we would check the denylist (AuthRepository) here
        payload = AuthService().decode_token(credentials.credentials)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


class RequireRole:
    """Dependency factory for role-based access control."""

    def __init__(self, roles: list[Role]) -> None:
        self.allowed_roles = set(roles)

    def __call__(self, user: Annotated[dict, Depends(get_current_user)]) -> dict:
        if user.get("role") not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user
