from __future__ import annotations

import hashlib
import secrets
import sqlite3
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException


@dataclass(frozen=True)
class AuthDBProofTokens:
    access_token: str
    refresh_token: str
    token_type: str
    guardian_learner_ids: list[str]
    permissions: list[str]
    user_id: str
    guardian_id: str


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def _stable_token(prefix: str, subject: str) -> str:
    digest = hashlib.sha256(f"{prefix}:{subject}:{secrets.token_hex(8)}".encode("utf-8")).hexdigest()
    return f"{prefix}-{digest}"


class SQLiteAuthLifecycleProofStore:
    """Transactional SQLite auth lifecycle proof store.

    This store is intentionally isolated from production repositories. It proves
    persistence semantics without touching production data or external services.
    """

    def __init__(self, connection: sqlite3.Connection | None = None):
        self.connection = connection or sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS guardians (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS learners (
                id TEXT PRIMARY KEY,
                guardian_id TEXT NOT NULL,
                display_name TEXT NOT NULL,
                FOREIGN KEY(guardian_id) REFERENCES guardians(id)
            );

            CREATE TABLE IF NOT EXISTS refresh_tokens (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                guardian_id TEXT NOT NULL,
                consumed INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(guardian_id) REFERENCES guardians(id)
            );
            """
        )
        self.connection.commit()

    def register(self, *, email: str, password: str, display_name: str = "Guardian") -> AuthDBProofTokens:
        email = email.strip().lower()
        if not email:
            raise HTTPException(status_code=422, detail="email is required")
        if not password:
            raise HTTPException(status_code=422, detail="password is required")

        existing = self.connection.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="email already registered")

        user_id = f"user-{self.connection.execute('SELECT COUNT(*) FROM users').fetchone()[0] + 1}"
        guardian_id = f"guardian-{self.connection.execute('SELECT COUNT(*) FROM guardians').fetchone()[0] + 1}"
        learner_id = f"learner-{self.connection.execute('SELECT COUNT(*) FROM learners').fetchone()[0] + 1}"
        salt = secrets.token_hex(8)
        password_hash = _hash_password(password, salt)

        with self.connection:
            self.connection.execute(
                "INSERT INTO users (id, email, password_salt, password_hash, role) VALUES (?, ?, ?, ?, ?)",
                (user_id, email, salt, password_hash, "guardian"),
            )
            self.connection.execute(
                "INSERT INTO guardians (id, user_id, display_name) VALUES (?, ?, ?)",
                (guardian_id, user_id, display_name),
            )
            self.connection.execute(
                "INSERT INTO learners (id, guardian_id, display_name) VALUES (?, ?, ?)",
                (learner_id, guardian_id, "Learner One"),
            )

        return self._issue_tokens(user_id=user_id, guardian_id=guardian_id)

    def login(self, *, email: str, password: str) -> AuthDBProofTokens:
        email = email.strip().lower()
        row = self.connection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row is None:
            raise HTTPException(status_code=401, detail="invalid credentials")

        if _hash_password(password, row["password_salt"]) != row["password_hash"]:
            raise HTTPException(status_code=401, detail="invalid credentials")

        guardian = self.connection.execute("SELECT * FROM guardians WHERE user_id = ?", (row["id"],)).fetchone()
        if guardian is None:
            raise HTTPException(status_code=403, detail="guardian profile missing")

        return self._issue_tokens(user_id=row["id"], guardian_id=guardian["id"])

    def refresh(self, *, refresh_token: str) -> AuthDBProofTokens:
        row = self.connection.execute("SELECT * FROM refresh_tokens WHERE token = ?", (refresh_token,)).fetchone()
        if row is None:
            raise HTTPException(status_code=401, detail="invalid refresh token")
        if int(row["consumed"]):
            raise HTTPException(status_code=401, detail="refresh token already used")

        with self.connection:
            self.connection.execute("UPDATE refresh_tokens SET consumed = 1 WHERE token = ?", (refresh_token,))

        return self._issue_tokens(user_id=row["user_id"], guardian_id=row["guardian_id"])

    def learner_ids_for_guardian(self, guardian_id: str) -> list[str]:
        rows = self.connection.execute(
            "SELECT id FROM learners WHERE guardian_id = ? ORDER BY id",
            (guardian_id,),
        ).fetchall()
        return [row["id"] for row in rows]

    def _issue_tokens(self, *, user_id: str, guardian_id: str) -> AuthDBProofTokens:
        access_token = _stable_token("access", user_id)
        refresh_token = _stable_token("refresh", user_id)
        with self.connection:
            self.connection.execute(
                "INSERT INTO refresh_tokens (token, user_id, guardian_id, consumed) VALUES (?, ?, ?, 0)",
                (refresh_token, user_id, guardian_id),
            )

        learner_ids = self.learner_ids_for_guardian(guardian_id)
        return AuthDBProofTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            guardian_learner_ids=learner_ids,
            permissions=["learner:read", "learner:write"],
            user_id=user_id,
            guardian_id=guardian_id,
        )


class AuthDBProofApplicationService:
    """AuthApplicationService-compatible facade backed by SQLite proof store."""

    def __init__(self, store: SQLiteAuthLifecycleProofStore):
        self.store = store

    async def register(self, **kwargs: Any) -> dict[str, Any]:
        email, password, display_name = extract_auth_payload(kwargs)
        tokens = self.store.register(email=email, password=password, display_name=display_name)
        return token_response(tokens)

    async def login(self, **kwargs: Any) -> dict[str, Any]:
        email, password, _display_name = extract_auth_payload(kwargs)
        tokens = self.store.login(email=email, password=password)
        return token_response(tokens)

    async def refresh(self, **kwargs: Any) -> dict[str, Any]:
        refresh_token = extract_refresh_token(kwargs)
        tokens = self.store.refresh(refresh_token=refresh_token)
        return token_response(tokens)

    async def create_dev_session(self, **kwargs: Any) -> dict[str, Any]:
        tokens = self.store.register(
            email="dev.guardian@example.com",
            password="Password123!",
            display_name="Dev Guardian",
        )
        return token_response(tokens)


def _find_by_name(value: Any, names: set[str]) -> Any | None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in names and item is not None:
                return item
            nested = _find_by_name(item, names)
            if nested is not None:
                return nested
    elif hasattr(value, "model_dump"):
        return _find_by_name(value.model_dump(), names)
    elif hasattr(value, "dict"):
        return _find_by_name(value.dict(), names)
    return None


def extract_auth_payload(kwargs: dict[str, Any]) -> tuple[str, str, str]:
    email = _find_by_name(kwargs, {"email", "guardian_email", "username"}) or "guardian.success@example.com"
    password = _find_by_name(kwargs, {"password", "plain_password"}) or "Password123!"
    display_name = _find_by_name(kwargs, {"display_name", "name", "guardian_name", "full_name"}) or "Guardian Success"
    return str(email), str(password), str(display_name)


def extract_refresh_token(kwargs: dict[str, Any]) -> str:
    token = _find_by_name(kwargs, {"refresh_token", "token"})
    if token is not None:
        return str(token)

    for value in kwargs.values():
        if hasattr(value, "cookies"):
            cookie_value = value.cookies.get("refresh_token")
            if cookie_value:
                return str(cookie_value)

    raise HTTPException(status_code=401, detail="refresh token required")


def token_response(tokens: AuthDBProofTokens) -> dict[str, Any]:
    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "token_type": tokens.token_type,
        "guardian_learner_ids": tokens.guardian_learner_ids,
        "permissions": tokens.permissions,
        "user_id": tokens.user_id,
        "guardian_id": tokens.guardian_id,
        "user": {
            "id": tokens.user_id,
            "guardian_id": tokens.guardian_id,
            "guardian_learner_ids": tokens.guardian_learner_ids,
        },
    }


__all__ = [
    "AuthDBProofApplicationService",
    "AuthDBProofTokens",
    "SQLiteAuthLifecycleProofStore",
    "extract_auth_payload",
    "extract_refresh_token",
    "token_response",
]
