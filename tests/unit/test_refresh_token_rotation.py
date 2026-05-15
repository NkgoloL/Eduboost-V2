from __future__ import annotations

import fnmatch
from typing import Any, AsyncIterator

import pytest
from fastapi import HTTPException

from app.core import refresh_tokens
from app.core.security import create_refresh_token, decode_token
from app.models import UserRole


class FakeRedis:

    async def setex(self, key, ttl, value):
        """Compatibility method for Redis SETEX used by token revocation."""
        if hasattr(self, "set"):
            result = self.set(key, value)
            if hasattr(result, "__await__"):
                await result
        elif hasattr(self, "_data"):
            self._data[key] = value
        elif hasattr(self, "store"):
            self.store[key] = value
        else:
            setattr(self, str(key), value)
        return True

    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttls: dict[str, int] = {}

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.values[key] = value
        if ex is not None:
            self.ttls[key] = ex

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def delete(self, *keys: str) -> int:
        deleted = 0
        for key in keys:
            deleted += int(key in self.values)
            self.values.pop(key, None)
            self.ttls.pop(key, None)
        return deleted

    async def scan_iter(self, match: str) -> AsyncIterator[str]:
        for key in list(self.values):
            if fnmatch.fnmatch(key, match):
                yield key

    async def ttl(self, key: str) -> int:
        return self.ttls.get(key, -1)


@pytest.fixture()
def fake_redis(monkeypatch: pytest.MonkeyPatch) -> FakeRedis:
    redis = FakeRedis()

    async def cache_set(key: str, value: str, ttl: int) -> None:
        await redis.set(key, value, ex=ttl)

    async def cache_get(key: str) -> str | None:
        return await redis.get(key)

    async def cache_delete(key: str) -> None:
        await redis.delete(key)

    async def cache_delete_pattern(pattern: str) -> int:
        keys = [key async for key in redis.scan_iter(match=pattern)]
        return await redis.delete(*keys) if keys else 0

    monkeypatch.setattr(refresh_tokens, "cache_set", cache_set)
    monkeypatch.setattr(refresh_tokens, "cache_get", cache_get)
    monkeypatch.setattr(refresh_tokens, "cache_delete", cache_delete)
    monkeypatch.setattr(refresh_tokens, "cache_delete_pattern", cache_delete_pattern)
    monkeypatch.setattr(refresh_tokens, "get_redis", lambda: redis)
    return redis


@pytest.mark.asyncio
async def test_refresh_token_is_hashed_and_bound_to_family(fake_redis: FakeRedis) -> None:
    token = create_refresh_token("guardian-1", UserRole.PARENT)
    payload = decode_token(token)

    await refresh_tokens.store_refresh_token(token)

    assert fake_redis.values[f"refresh:{payload['jti']}"] == refresh_tokens.token_hash(token)
    assert fake_redis.values[f"refresh_family:{payload['family']}:{payload['jti']}"] == "guardian-1"
    assert fake_redis.values[f"refresh_user:guardian-1:{payload['jti']}"] == payload["family"]
    assert token not in fake_redis.values.values()


@pytest.mark.asyncio
async def test_consumed_refresh_token_cannot_be_reused_and_revokes_family(fake_redis: FakeRedis) -> None:
    token = create_refresh_token("guardian-1", UserRole.PARENT)
    payload = decode_token(token)
    await refresh_tokens.store_refresh_token(token)

    consumed = await refresh_tokens.consume_refresh_token(token)
    assert consumed["jti"] == payload["jti"]

    with pytest.raises(HTTPException):
        await refresh_tokens.consume_refresh_token(token)

    assert await refresh_tokens.is_refresh_family_revoked(payload["family"]) is True


@pytest.mark.asyncio
async def test_list_user_refresh_sessions_exposes_only_metadata(fake_redis: FakeRedis) -> None:
    token = create_refresh_token("guardian-1", UserRole.PARENT)
    payload = decode_token(token)
    await refresh_tokens.store_refresh_token(token)

    sessions = await refresh_tokens.list_user_refresh_sessions("guardian-1")

    assert sessions[0]["jti"] == payload["jti"]
    assert sessions[0]["family_id"] == payload["family"]
    assert sessions[0]["ttl_seconds"] == pytest.approx(7 * 24 * 3600, abs=5)
