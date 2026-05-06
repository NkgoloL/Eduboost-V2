from __future__ import annotations

"""
EduBoost V2 — Redis Client
Thin async wrapper around redis-py used for caching and session storage ONLY.
No streams, no pub/sub, no Celery.
"""
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings

_pool: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _pool
    if _pool is None:
        _pool = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
    return _pool


async def cache_set(key: str, value: str, ttl: int = settings.REDIS_CACHE_TTL_SECONDS) -> None:
    await get_redis().set(key, value, ex=ttl)


async def cache_get(key: str) -> str | None:
    return await get_redis().get(key)


async def cache_delete(key: str) -> None:
    await get_redis().delete(key)


async def cache_delete_pattern(pattern: str) -> int:
    keys = [key async for key in get_redis().scan_iter(match=pattern)]
    if not keys:
        return 0
    return int(await get_redis().delete(*keys))


async def increment_counter(key: str, ttl_seconds: int = 86400) -> int:
    """Atomic increment — used for per-user daily quota tracking."""
    redis = get_redis()
    pipe = redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, ttl_seconds)
    results: list[Any] = await pipe.execute()
    return int(results[0])
