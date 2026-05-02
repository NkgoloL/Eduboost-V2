from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt

from app.core.security import hash_password, verify_password


def get_v2_settings():
    from app.core.config import settings

    class _Compat:
        jwt_secret = settings.JWT_SECRET
        jwt_algorithm = settings.JWT_ALGORITHM

    return _Compat()


@dataclass(slots=True)
class SessionTokens:
    access_token: str
    refresh_token: str


class AuthService:
    def __init__(self) -> None:
        self.settings = get_v2_settings()

    def create_session(self, user_id: str, role: str) -> SessionTokens:
        return SessionTokens(
            access_token=self._token(user_id, role, "access", minutes=15),
            refresh_token=self._token(user_id, role, "refresh", days=7),
        )

    def rotate_refresh_token(self, refresh_token: str) -> SessionTokens:
        payload = self.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Refresh token required")
        return self.create_session(payload["sub"], payload.get("role", "Student"))

    def decode_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, self.settings.jwt_secret, algorithms=[self.settings.jwt_algorithm])

    def hash_password(self, password: str) -> str:
        return hash_password(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        return verify_password(password, hashed)

    def _token(self, user_id: str, role: str, token_type: str, minutes: int = 0, days: int = 0) -> str:
        exp = datetime.now(UTC) + timedelta(minutes=minutes, days=days)
        return jwt.encode(
            {"sub": user_id, "role": role, "type": token_type, "exp": exp},
            self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
        )
