"""Redis-backed quota and cost-control service for EduBoost V2."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import redis.asyncio as redis_async

from app.core.config import get_v2_settings


class QuotaExceededError(RuntimeError):
    pass


class QuotaService:
    def __init__(self) -> None:
        settings = get_v2_settings()
        self.redis = redis_async.from_url(settings.redis_url, decode_responses=True)
        self.daily_limit = 200
        self.cache_ttl_seconds = 86400

    def _quota_key(self, subject: str) -> str:
        return f"v2:quota:{subject}"

    def _cache_key(self, namespace: str, payload: dict[str, Any]) -> str:
        body = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(body.encode()).hexdigest()
        return f"v2:cache:{namespace}:{digest}"

    async def assert_within_quota(self, subject: str) -> int:
        key = self._quota_key(subject)
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, self.cache_ttl_seconds)
        if count > self.daily_limit:
            raise QuotaExceededError(f"Daily quota exceeded for {subject}")
        return count

    async def get_cached(self, namespace: str, payload: dict[str, Any]) -> Any | None:
        key = self._cache_key(namespace, payload)
        raw = await self.redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set_cached(self, namespace: str, payload: dict[str, Any], value: Any) -> None:
        key = self._cache_key(namespace, payload)
        await self.redis.set(key, json.dumps(value, default=str), ex=self.cache_ttl_seconds)
