"""Auth routes for EduBoost V2."""

from fastapi import APIRouter

from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v2/auth", tags=["V2 Auth"])


@router.post("/session")
async def create_session(subject: str, role: str):
    return AuthService().create_session(subject=subject, role=role)


@router.post("/refresh")
async def refresh_session(refresh_token: str):
    return AuthService().rotate_refresh_token(refresh_token)
