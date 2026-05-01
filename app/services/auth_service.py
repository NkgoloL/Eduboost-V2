"""V2 authentication and RBAC service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal
import uuid

import jwt

from app.core.config import get_v2_settings
from app.core.security import hash_password, verify_password
from app.repositories.auth_repository import AuthRepository


Role = Literal["Student", "Parent", "Teacher", "Admin"]


@dataclass(slots=True)
class AuthSession:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthService:
    def __init__(self, repository: AuthRepository | None = None) -> None:
        self.settings = get_v2_settings()
        self.repository = repository or AuthRepository()

    def create_session(self, subject: str, role: Role) -> AuthSession:
        now = datetime.now(timezone.utc)
        access_payload = {
            "sub": subject,
            "role": role,
            "type": "access",
            "jti": str(uuid.uuid4()),
            "exp": now + timedelta(minutes=60),
        }
        refresh_payload = {
            "sub": subject,
            "role": role,
            "type": "refresh",
            "jti": str(uuid.uuid4()),
            "exp": now + timedelta(days=30),
        }
        return AuthSession(
            access_token=jwt.encode(access_payload, self.settings.jwt_secret, algorithm=self.settings.jwt_algorithm),
            refresh_token=jwt.encode(refresh_payload, self.settings.jwt_secret, algorithm=self.settings.jwt_algorithm),
        )

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, self.settings.jwt_secret, algorithms=[self.settings.jwt_algorithm])

    async def rotate_refresh_token(self, refresh_token: str) -> AuthSession:
        payload = self.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Expected a refresh token")
        
        # Check if JTI is revoked
        if await self.repository.is_jti_revoked(payload["jti"]):
            raise ValueError("Token has been revoked")

        return self.create_session(subject=payload["sub"], role=payload["role"])

    def hash_password(self, password: str) -> str:
        return hash_password(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        return verify_password(password, password_hash)
