"""
EduBoost SA — Auth Router (V2)
Thin HTTP layer — delegates all logic to AuthService.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
_auth_service = AuthService()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)) -> dict:
    guardian = await _auth_service.register_guardian(
        db,
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        phone=body.phone,
    )
    return {"id": str(guardian.id), "message": "Registration successful. Please verify your email."}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    ip = request.client.host if request.client else None
    access, refresh = await _auth_service.authenticate(
        db, email=body.email, password=body.password, ip_address=ip
    )
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.get("/verify-email/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)) -> dict:
    await _auth_service.verify_email(token, db)
    return {"message": "Email verified successfully"}


@router.get("/me")
async def get_profile(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _auth_service.get_guardian_profile(user_id, db)
