from __future__ import annotations

import hashlib
import json
from datetime import date
from typing import Any

from app.core.config import settings
from app.core.redis import cache_get, cache_set, increment_counter


class QuotaExceededError(Exception):
    """Raised when a user has exhausted their daily AI quota."""


class QuotaService:
    def cache_key(self, *parts: object) -> str:
        raw = ":".join(str(p) for p in parts)
        return f"semantic:{hashlib.sha256(raw.encode()).hexdigest()}"

    async def get_cached(self, key: str) -> Any | None:
        cached = await cache_get(key)
        if cached is None:
            return None
        if isinstance(cached, (dict, list)):
            return cached
        try:
            return json.loads(cached)
        except (TypeError, json.JSONDecodeError):
            return cached

    async def set_cached(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        payload = json.dumps(value, default=str)
        await cache_set(key, payload, ttl=ttl_seconds or 7 * 24 * 3600)

    async def assert_within_quota(self, user_id: str, tier: str = "free") -> int:
        if tier == "premium":
            return 0
        limit = settings.FREE_DAILY_REQUEST_QUOTA
        key = f"ai_quota:{user_id}:{date.today().isoformat()}"
        count = await increment_counter(key, ttl_seconds=24 * 3600)
        if count > limit:
            raise QuotaExceededError("Daily AI quota exceeded")
        return count
