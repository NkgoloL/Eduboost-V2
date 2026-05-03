from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core import security as security_module
from app.core import token_revocation as token_revocation_module
from app.models import UserRole


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, tuple[int, str]] = {}

    async def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        self.values[key] = (ttl_seconds, value)

    async def get(self, key: str) -> str | None:
        entry = self.values.get(key)
        if entry is None:
            return None
        return entry[1]


@pytest.mark.asyncio
async def test_revoke_token_stores_jti_with_remaining_ttl(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_redis = FakeRedis()
    monkeypatch.setattr(token_revocation_module, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(
        token_revocation_module,
        "datetime",
        SimpleNamespace(now=lambda _: SimpleNamespace(timestamp=lambda: 100.0)),
    )

    await token_revocation_module.revoke_token("jti-123", 250)

    ttl, value = fake_redis.values["revoked_jti:jti-123"]
    assert ttl == 150
    assert value == "1"


@pytest.mark.asyncio
async def test_is_token_revoked_returns_true_when_present(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_redis = FakeRedis()
    fake_redis.values["revoked_jti:jti-123"] = (60, "1")
    monkeypatch.setattr(token_revocation_module, "get_redis", lambda: fake_redis)

    assert await token_revocation_module.is_token_revoked("jti-123") is True
    assert await token_revocation_module.is_token_revoked("jti-missing") is False


@pytest.mark.asyncio
async def test_revoke_user_tokens_marks_user_as_revoked(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_redis = FakeRedis()
    monkeypatch.setattr(token_revocation_module, "get_redis", lambda: fake_redis)

    await token_revocation_module.revoke_user_tokens("guardian-1")

    ttl, value = fake_redis.values["revoked_user:guardian-1"]
    assert ttl == 30 * 24 * 3600
    assert value == "1"
    assert await token_revocation_module.is_user_revoked("guardian-1") is True


def test_create_access_token_includes_jti() -> None:
    token = security_module.create_access_token("guardian-1", UserRole.PARENT)
    payload = security_module.decode_token(token)

    assert payload["type"] == "access"
    assert payload["jti"]


@pytest.mark.asyncio
async def test_get_current_user_rejects_revoked_jti(monkeypatch: pytest.MonkeyPatch) -> None:
    token = security_module.create_access_token("guardian-1", UserRole.PARENT)
    monkeypatch.setattr(security_module, "is_token_revoked", lambda jti: _async_true())
    monkeypatch.setattr(security_module, "is_user_revoked", lambda user_id: _async_false())

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with pytest.raises(HTTPException, match="Token has been revoked"):
        await security_module.get_current_user(credentials)


async def _async_true() -> bool:
    return True


async def _async_false() -> bool:
    return False
