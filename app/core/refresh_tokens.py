"""Single-use refresh-token rotation backed by Redis.

Refresh tokens are stored hashed at rest, bound to a token family, and rotated
on every use. Reusing an already-consumed token revokes the whole family.
"""
from __future__ import annotations

import hashlib
import hmac
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.redis import cache_delete, cache_delete_pattern, cache_get, cache_set, get_redis
from app.core.security import decode_token

_REFRESH_PREFIX = "refresh"
_REFRESH_FAMILY_PREFIX = "refresh_family"
_REFRESH_USER_PREFIX = "refresh_user"
_REFRESH_FAMILY_REVOKED_PREFIX = "refresh_family_revoked"


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _refresh_key(jti: str) -> str:
    return f"{_REFRESH_PREFIX}:{jti}"


def _family_key(family_id: str, jti: str) -> str:
    return f"{_REFRESH_FAMILY_PREFIX}:{family_id}:{jti}"


def _user_session_key(subject: str, jti: str) -> str:
    return f"{_REFRESH_USER_PREFIX}:{subject}:{jti}"


def _family_revoked_key(family_id: str) -> str:
    return f"{_REFRESH_FAMILY_REVOKED_PREFIX}:{family_id}"


def _ttl_from_payload(payload: dict[str, Any]) -> int:
    exp = payload.get("exp")
    if isinstance(exp, (int, float)):
        return max(int(exp - datetime.now(UTC).timestamp()), 1)
    return settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600


def _require_refresh_payload(token: str) -> dict[str, Any]:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a refresh token")
    if not payload.get("jti") or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed refresh token")
    return payload


async def store_refresh_token(token: str) -> None:
    payload = _require_refresh_payload(token)
    jti = str(payload["jti"])
    subject = str(payload["sub"])
    family_id = str(payload.get("family") or jti)
    ttl = _ttl_from_payload(payload)
    hashed = token_hash(token)

    await cache_set(_refresh_key(jti), hashed, ttl=ttl)
    await cache_set(_family_key(family_id, jti), subject, ttl=ttl)
    await cache_set(_user_session_key(subject, jti), family_id, ttl=ttl)


async def consume_refresh_token(token: str) -> dict[str, Any]:
    payload = _require_refresh_payload(token)
    jti = str(payload["jti"])
    family_id = str(payload.get("family") or jti)

    if await is_refresh_family_revoked(family_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token family revoked")

    stored_hash = await cache_get(_refresh_key(jti))
    if stored_hash is None or not hmac.compare_digest(stored_hash, token_hash(token)):
        await revoke_refresh_family(family_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token already used or revoked; token family revoked",
        )

    await cache_delete(_refresh_key(jti))
    await cache_delete(_family_key(family_id, jti))
    await cache_delete(_user_session_key(str(payload["sub"]), jti))
    return payload


async def revoke_refresh_token(token: str) -> None:
    payload = _require_refresh_payload(token)
    jti = payload.get("jti")
    if jti:
        await revoke_refresh_token_jti(str(jti), str(payload.get("sub")) if payload.get("sub") else None, str(payload.get("family")) if payload.get("family") else None)


async def revoke_refresh_token_jti(jti: str | None, subject: str | None = None, family_id: str | None = None) -> None:
    if not jti:
        return
    await cache_delete(_refresh_key(jti))
    if family_id:
        await cache_delete(_family_key(family_id, jti))
    if subject:
        await cache_delete(_user_session_key(subject, jti))


async def revoke_refresh_family(family_id: str | None) -> None:
    if not family_id:
        return
    ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
    await cache_set(_family_revoked_key(family_id), "1", ttl=ttl)
    await cache_delete_pattern(f"{_REFRESH_FAMILY_PREFIX}:{family_id}:*")


async def is_refresh_family_revoked(family_id: str | None) -> bool:
    if not family_id:
        return False
    return await cache_get(_family_revoked_key(family_id)) is not None


async def revoke_all_refresh_tokens_for_user(subject: str) -> int:
    return await cache_delete_pattern(f"{_REFRESH_USER_PREFIX}:{subject}:*")


async def list_user_refresh_sessions(subject: str) -> list[dict[str, Any]]:
    redis = get_redis()
    sessions: list[dict[str, Any]] = []
    async for key in redis.scan_iter(match=f"{_REFRESH_USER_PREFIX}:{subject}:*"):
        jti = str(key).rsplit(":", 1)[-1]
        family_id = await cache_get(str(key))
        ttl = await redis.ttl(str(key))
        sessions.append({"jti": jti, "family_id": family_id, "ttl_seconds": ttl})
    return sorted(sessions, key=lambda item: item["jti"])


__all__ = [
    "consume_refresh_token",
    "is_refresh_family_revoked",
    "list_user_refresh_sessions",
    "revoke_all_refresh_tokens_for_user",
    "revoke_refresh_family",
    "revoke_refresh_token",
    "revoke_refresh_token_jti",
    "store_refresh_token",
    "token_hash",
]
