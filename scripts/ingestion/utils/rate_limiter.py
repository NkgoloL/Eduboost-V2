"""Async token-bucket rate limiter — respects per-source RPS caps."""
from __future__ import annotations

import asyncio
import time
from collections import defaultdict


class RateLimiter:
    """
    Async token-bucket rate limiter.

    Usage::

        limiter = RateLimiter()
        await limiter.acquire("khan_academy")   # waits if over budget
    """

    def __init__(self) -> None:
        self._locks:    dict[str, asyncio.Lock]  = defaultdict(asyncio.Lock)
        self._tokens:   dict[str, float]         = defaultdict(float)
        self._last:     dict[str, float]         = defaultdict(float)
        self._rps:      dict[str, float]         = {}

    def set_rate(self, source_id: str, rps: float) -> None:
        self._rps[source_id] = rps

    async def acquire(self, source_id: str, rps: float | None = None) -> None:
        if rps is not None:
            self._rps[source_id] = rps
        rate = self._rps.get(source_id, 1.0)

        async with self._locks[source_id]:
            now  = time.monotonic()
            gap  = now - self._last[source_id]
            self._tokens[source_id] = min(1.0, self._tokens[source_id] + gap * rate)
            self._last[source_id]   = now

            if self._tokens[source_id] < 1.0:
                wait = (1.0 - self._tokens[source_id]) / rate
                await asyncio.sleep(wait)
                self._tokens[source_id] = 0.0
            else:
                self._tokens[source_id] -= 1.0


# Module-level singleton so all scrapers share one limiter
_global_limiter = RateLimiter()


async def throttle(source_id: str, rps: float) -> None:
    """Convenience wrapper around the global limiter."""
    await _global_limiter.acquire(source_id, rps)
