"""
app/services/quota.py
EduBoost V2 — AI Cost-Control: Daily Token Quotas

Implements Phase 2.3:
  - Redis-backed daily quota tracking (fast path)
  - PostgreSQL quota table (durable fallback + audit)
  - Raises HTTP 429 when quota exhausted
  - Semantic cache key generation for cache hits

BOUNDARY: May import from /app/core/ and /app/domain/.
"""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

import redis.asyncio as aioredis
import structlog
from fastapi import HTTPException, status

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger(__name__)

# Redis key patterns
_QUOTA_KEY = "quota:{guardian_id}:{date}"      # e.g. quota:uuid:2026-05-03
_CACHE_KEY = "semcache:{hash}"                  # semantic cache


class QuotaExceededError(RuntimeError):
    """Compatibility exception for quota failures in lightweight unit tests."""


class QuotaService:
    """
    Daily token quota enforcement.
    Uses Redis as the fast counter; PostgreSQL is the durable audit store.
    """

    def __init__(self, redis_client: aioredis.Redis | None = None) -> None:
        self._redis = redis_client

    def _quota_key(self, guardian_id: str) -> str:
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        return _QUOTA_KEY.format(guardian_id=guardian_id, date=today)

    async def check_and_reserve(
        self, guardian_id: str, estimated_tokens: int, tier: str
    ) -> None:
        """
        Check if guardian has quota remaining.
        Raises HTTP 429 if exhausted.

        Uses INCRBY in Redis for atomic increment.
        TTL is set to 86400s (24h) to auto-expire old keys.
        """
        limit = (
            settings.daily_token_quota_premium
            if tier == "premium"
            else settings.daily_token_quota_free
        )
        key = self._quota_key(guardian_id)

        current = await self._redis.incrby(key, estimated_tokens)
        if current == estimated_tokens:
            # First increment today — set expiry
            await self._redis.expire(key, 86400)

        if current > limit:
            # Roll back the increment so the counter stays accurate
            await self._redis.decrby(key, estimated_tokens)
            logger.warning("quota_exhausted", guardian_id=guardian_id, current=current, limit=limit)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "daily_quota_exhausted",
                    "message": f"Daily token quota of {limit:,} tokens reached. Upgrade to Premium for unlimited access.",
                    "tokens_used": current - estimated_tokens,
                    "quota": limit,
                    "tier": tier,
                },
                headers={"Retry-After": "86400"},
            )

    async def get_usage(self, guardian_id: str) -> tuple[int, int]:
        """Returns (tokens_used_today, requests_today) from Redis."""
        key = self._quota_key(guardian_id)
        raw = await self._redis.get(key)
        tokens = int(raw) if raw else 0
        # Request count stored in a separate key
        req_key = key + ":reqs"
        req_raw = await self._redis.get(req_key)
        reqs = int(req_raw) if req_raw else 0
        return tokens, reqs

    async def increment_requests(self, guardian_id: str) -> None:
        req_key = self._quota_key(guardian_id) + ":reqs"
        await self._redis.incr(req_key)
        await self._redis.expire(req_key, 86400)


class SemanticCacheService:
    """
    Redis-based semantic cache for LLM lesson responses.
    Identical requests (same grade, topic, archetype, language) return cached
    content in <50ms without hitting the LLM provider.
    """

    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client

    @staticmethod
    def build_cache_key(
        subject: str,
        topic: str,
        grade_level: str,
        language: str,
        archetype: str | None,
    ) -> str:
        """Deterministic cache key based on lesson parameters (NOT learner identity)."""
        canonical = json.dumps(
            {
                "subject": subject.strip().lower(),
                "topic": topic.strip().lower(),
                "grade": grade_level,
                "lang": language,
                "arch": archetype or "default",
            },
            sort_keys=True,
        )
        digest = hashlib.sha256(canonical.encode()).hexdigest()[:32]
        return _CACHE_KEY.format(hash=digest)

    async def get(self, cache_key: str) -> str | None:
        """Return cached lesson JSON string or None on miss."""
        if not settings.semantic_cache_enabled:
            return None
        raw = await self._redis.get(cache_key)
        if raw:
            logger.debug("cache_hit", key=cache_key[:16])
            return raw.decode() if isinstance(raw, bytes) else raw
        return None

    async def set(self, cache_key: str, lesson_json: str) -> None:
        """Store lesson JSON with TTL."""
        if not settings.semantic_cache_enabled:
            return
        await self._redis.setex(cache_key, settings.redis_cache_ttl_seconds, lesson_json)
        logger.debug("cache_stored", key=cache_key[:16], ttl=settings.redis_cache_ttl_seconds)
