from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core import security
from app.models import UserRole


@pytest.fixture(autouse=True)
def _stub_settings(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        security,
        "settings",
        SimpleNamespace(
            PASSWORD_BCRYPT_ROUNDS=4,
            JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15,
            JWT_ALGORITHM="HS256",
            ENCRYPTION_KEY="encryption-key-32chars-minimum-value",
            ENCRYPTION_SALT="salt-value",
        ),
    )


def test_password_and_email_helpers_round_trip_and_normalize():
    hashed = security.hash_password("MyStrongPass123!")
    assert security.verify_password("MyStrongPass123!", hashed) is True
    assert security.verify_password("wrong", hashed) is False
    assert security.verify_password("plain", "not-a-bcrypt-hash") is False

    h1 = security.hash_email(" Guardian@Example.com ")
    h2 = security.hash_email("guardian@example.com")
    assert h1 == h2


def test_encrypt_decrypt_helpers_handle_empty_and_round_trip():
    assert security.encrypt_pii("") == ""
    assert security.decrypt_pii("") == ""

    cipher_hex = security.encrypt_pii("guardian@example.com")
    assert isinstance(cipher_hex, str)
    assert cipher_hex != "guardian@example.com"
    assert security.decrypt_pii(cipher_hex) == "guardian@example.com"


def test_create_and_decode_access_token(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(security, "current_jwt_signing_key", lambda: "secret")
    monkeypatch.setattr(security, "current_jwt_algorithm", lambda _default: "HS256")
    monkeypatch.setattr(security, "current_jwt_headers", lambda: {"kid": "k1"})
    monkeypatch.setattr(security, "decode_jwt_with_keyring", lambda token: security.jwt.decode(token, "secret", algorithms=["HS256"]))

    token = security.create_access_token("user-1", UserRole.PARENT, extra={"scope": "demo"})
    payload = security.decode_token(token)

    assert payload["sub"] == "user-1"
    assert payload["type"] == "access"
    assert payload["scope"] == "demo"


def test_create_refresh_token_contains_family(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(security, "current_jwt_signing_key", lambda: "secret")
    monkeypatch.setattr(security, "current_jwt_algorithm", lambda _default: "HS256")
    monkeypatch.setattr(security, "current_jwt_headers", lambda: {"kid": "k1"})
    monkeypatch.setattr(security, "decode_jwt_with_keyring", lambda token: security.jwt.decode(token, "secret", algorithms=["HS256"]))

    token = security.create_refresh_token("user-2", UserRole.PARENT, family_id="family-1")
    payload = security.decode_token(token)

    assert payload["sub"] == "user-2"
    assert payload["type"] == "refresh"
    assert payload["family"] == "family-1"


def test_decode_token_wraps_jwt_error(monkeypatch: pytest.MonkeyPatch):
    def _boom(_token: str, *, options=None):
        raise security.JWTError("invalid")

    monkeypatch.setattr(security, "decode_jwt_with_keyring", _boom)

    with pytest.raises(HTTPException) as exc_info:
        security.decode_token("bad-token")

    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_missing_credentials_rejected():
    with pytest.raises(HTTPException) as exc_info:
        await security.get_current_user(None)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_refresh_tokens(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        security,
        "decode_token",
        lambda _token: {"sub": "user-1", "type": "refresh", "jti": "j1"},
    )

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="x")
    with pytest.raises(HTTPException) as exc_info:
        await security.get_current_user(creds)

    assert exc_info.value.status_code == 401
    assert "Refresh token" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_rejects_revoked_jti(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        security,
        "decode_token",
        lambda _token: {"sub": "user-1", "type": "access", "jti": "j1"},
    )
    monkeypatch.setattr(security, "is_token_revoked", AsyncMock(return_value=True))
    monkeypatch.setattr(security, "is_user_revoked", AsyncMock(return_value=False))

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="x")
    with pytest.raises(HTTPException) as exc_info:
        await security.get_current_user(creds)

    assert exc_info.value.status_code == 401
    assert "revoked" in str(exc_info.value.detail).lower()


@pytest.mark.asyncio
async def test_get_current_user_rejects_revoked_user(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        security,
        "decode_token",
        lambda _token: {"sub": "user-1", "type": "access", "jti": "j1"},
    )
    monkeypatch.setattr(security, "is_token_revoked", AsyncMock(return_value=False))
    monkeypatch.setattr(security, "is_user_revoked", AsyncMock(return_value=True))

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="x")
    with pytest.raises(HTTPException) as exc_info:
        await security.get_current_user(creds)

    assert exc_info.value.status_code == 401
    assert "User tokens have been revoked" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_optional_none_and_success(monkeypatch: pytest.MonkeyPatch):
    assert await security.get_current_user_optional(None) is None

    monkeypatch.setattr(
        security,
        "decode_token",
        lambda _token: {"sub": "user-1", "type": "access", "jti": "j1", "role": "parent"},
    )
    monkeypatch.setattr(security, "is_token_revoked", AsyncMock(return_value=False))
    monkeypatch.setattr(security, "is_user_revoked", AsyncMock(return_value=False))

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="x")
    payload = await security.get_current_user_optional(creds)
    assert payload["sub"] == "user-1"


def test_require_roles_accepts_and_rejects():
    parent_only = security.require_roles(UserRole.PARENT)
    assert parent_only({"role": UserRole.PARENT})["role"] == UserRole.PARENT

    with pytest.raises(HTTPException) as exc_info:
        parent_only({"role": UserRole.ADMIN})

    assert exc_info.value.status_code == 403
