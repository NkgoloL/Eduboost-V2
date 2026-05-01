"""Auth routes for EduBoost V2."""

from fastapi import APIRouter

from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v2/auth", tags=["V2 Auth"])


@router.post("/session")
async def create_session(subject: str, role: str):
    """V2 Session creation (Login). In production, this would verify credentials via AuthRepository."""
    return AuthService().create_session(subject=subject, role=role)


@router.post("/refresh")
async def refresh_session(refresh_token: str):
    """Rotate a refresh token for a new access token."""
    return await AuthService().rotate_refresh_token(refresh_token)


@router.post("/revoke")
async def revoke_token(jti: str, expires_at: str):
    """Revoke a token's JTI (Admin only or via session)."""
    from datetime import datetime
    from app.repositories.auth_repository import AuthRepository
    await AuthRepository().revoke_jti(jti, datetime.fromisoformat(expires_at))
    return {"status": "revoked", "jti": jti}
