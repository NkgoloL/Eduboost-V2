"""Single-use refresh token rotation backed by Redis."""
from __future__ import annotations

import hashlib
import hmac

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.redis import cache_delete, cache_get, cache_set
from app.core.security import decode_token


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def store_refresh_token(token: str) -> None:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a refresh token")
    key = f"refresh:{payload['jti']}"
    ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
    await cache_set(key, token_hash(token), ttl=ttl)


async def consume_refresh_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a refresh token")

    key = f"refresh:{payload['jti']}"
    stored_hash = await cache_get(key)
    if stored_hash is None or not hmac.compare_digest(stored_hash, token_hash(token)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token already used or revoked")

    await cache_delete(key)
    return payload


async def revoke_refresh_token(token: str) -> None:
    payload = decode_token(token)
    if payload.get("jti"):
        await cache_delete(f"refresh:{payload['jti']}")


async def revoke_refresh_token_jti(jti: str | None) -> None:
    if jti:
        await cache_delete(f"refresh:{jti}")
