"""
EduBoost SA — Phase 2 (L2-05)
Budget Guardrails — Per-User Daily Token Limit & Per-Tenant Monthly Budget

Responsibilities
----------------
• Track token usage per user (daily) and per tenant (monthly).
• Reject lesson generation requests that would exceed configured limits.
• Emit a cost alert when a tenant reaches 80% of its monthly budget.
• Log all usage without logging sensitive prompt content (POPIA compliant).

Storage
-------
Uses Redis for fast, TTL-based counters.  Falls back to in-process dict
when Redis is unavailable (development / test environments).

Usage
-----
    guardrails = BudgetGuardrails.from_settings(settings, redis_client)

    # Before calling the LLM gateway:
    await guardrails.assert_budget(user_id="u-123", tenant_id="t-abc", estimated_tokens=500)

    # After the LLM call:
    await guardrails.record_usage(
        user_id="u-123",
        tenant_id="t-abc",
        tokens_used=response["total_tokens"],
        provider=response["provider"],
        purpose="lesson_generation",
    )
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class BudgetExceededError(Exception):
    """Raised when a budget limit is reached before an LLM call."""

    def __init__(self, scope: str, used: int, limit: int) -> None:
        self.scope = scope
        self.used = used
        self.limit = limit
        super().__init__(
            f"Budget exceeded for {scope}: used {used}/{limit} tokens. "
            "Lesson generation is blocked until the budget period resets."
        )


# ---------------------------------------------------------------------------
# Budget configuration
# ---------------------------------------------------------------------------

@dataclass
class BudgetConfig:
    """Token budget configuration.

    All values are in tokens (prompt + completion combined).
    """

    # Per-user limits
    user_daily_token_limit: int = 50_000
    """Maximum tokens a single user may consume in a rolling 24-hour window."""

    # Per-tenant limits
    tenant_monthly_token_limit: int = 10_000_000
    """Maximum tokens a tenant may consume in a calendar month."""

    tenant_alert_threshold_pct: float = 0.80
    """Fraction of monthly budget at which a cost alert is emitted (default 80%)."""

    # Redis TTLs
    user_ttl_seconds: int = 86_400        # 24 hours
    tenant_ttl_seconds: int = 2_592_000   # 30 days


# ---------------------------------------------------------------------------
# Redis-backed counter helpers
# ---------------------------------------------------------------------------

class _RedisCounter:
    """INCR/GET with TTL in Redis."""

    def __init__(self, redis: Any) -> None:
        self._r = redis

    async def get(self, key: str) -> int:
        val = await self._r.get(key)
        return int(val) if val else 0

    async def add(self, key: str, amount: int, ttl: int) -> int:
        """Atomically add *amount* and set TTL if key is new. Returns new total."""
        pipe = self._r.pipeline()
        pipe.incrby(key, amount)
        pipe.expire(key, ttl)
        results = await pipe.execute()
        return int(results[0])


class _InProcessCounter:
    """Simple in-memory fallback counter (single-process only)."""

    def __init__(self) -> None:
        self._data: dict[str, tuple[int, float]] = {}  # key → (value, expires_at)

    async def get(self, key: str) -> int:
        entry = self._data.get(key)
        if entry is None or time.time() > entry[1]:
            return 0
        return entry[0]

    async def add(self, key: str, amount: int, ttl: int) -> int:
        existing, expires = self._data.get(key, (0, 0.0))
        if time.time() > expires:
            existing = 0
            expires = time.time() + ttl
        new_val = existing + amount
        self._data[key] = (new_val, expires)
        return new_val


# ---------------------------------------------------------------------------
# Alert dispatcher
# ---------------------------------------------------------------------------

def _emit_cost_alert(
    tenant_id: str,
    used_tokens: int,
    limit_tokens: int,
    pct: float,
) -> None:
    """Emit a cost alert.  Replace with SNS / PagerDuty / Slack integration."""
    logger.warning(
        "COST ALERT | tenant=%s | used=%d / limit=%d (%.0f%%) — "
        "approaching monthly token budget cap.",
        tenant_id,
        used_tokens,
        limit_tokens,
        pct * 100,
    )
    # TODO: integrate with alertmanager or Prometheus Alertmanager webhook


# ---------------------------------------------------------------------------
# Main guardrails class
# ---------------------------------------------------------------------------

class BudgetGuardrails:
    """Enforce token budgets before and after LLM calls.

    Parameters
    ----------
    config:
        Budget configuration.
    redis:
        Optional async Redis client (aioredis / redis-py >= 4).  If None,
        falls back to an in-process counter (not suitable for multi-worker
        production deployments).
    """

    def __init__(
        self,
        config: BudgetConfig | None = None,
        redis: Any = None,
    ) -> None:
        self._config = config or BudgetConfig()
        self._counter = _RedisCounter(redis) if redis else _InProcessCounter()

    @classmethod
    def from_settings(cls, settings: Any, redis: Any = None) -> "BudgetGuardrails":
        cfg = BudgetConfig(
            user_daily_token_limit=getattr(settings, "USER_DAILY_TOKEN_LIMIT", 50_000),
            tenant_monthly_token_limit=getattr(settings, "TENANT_MONTHLY_TOKEN_LIMIT", 10_000_000),
            tenant_alert_threshold_pct=getattr(settings, "TENANT_BUDGET_ALERT_PCT", 0.80),
        )
        return cls(config=cfg, redis=redis)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def assert_budget(
        self,
        user_id: str,
        tenant_id: str,
        estimated_tokens: int = 1_000,
    ) -> None:
        """Raise :class:`BudgetExceededError` if either limit would be breached.

        Call this BEFORE the LLM gateway call.  ``estimated_tokens`` can be a
        rough upper bound; actual usage is recorded with :meth:`record_usage`.
        """
        user_used = await self._get_user_usage(user_id)
        if user_used + estimated_tokens > self._config.user_daily_token_limit:
            raise BudgetExceededError(
                scope=f"user:{user_id} (daily)",
                used=user_used,
                limit=self._config.user_daily_token_limit,
            )

        tenant_used = await self._get_tenant_usage(tenant_id)
        if tenant_used + estimated_tokens > self._config.tenant_monthly_token_limit:
            raise BudgetExceededError(
                scope=f"tenant:{tenant_id} (monthly)",
                used=tenant_used,
                limit=self._config.tenant_monthly_token_limit,
            )

    async def record_usage(
        self,
        user_id: str,
        tenant_id: str,
        tokens_used: int,
        provider: str = "",
        purpose: str = "",
    ) -> None:
        """Record actual token usage after a completed LLM call.

        Logs usage metadata; does NOT log prompt or completion content.
        """
        if tokens_used <= 0:
            return

        user_key = self._user_key(user_id)
        tenant_key = self._tenant_key(tenant_id)

        new_user_total = await self._counter.add(
            user_key, tokens_used, self._config.user_ttl_seconds
        )
        new_tenant_total = await self._counter.add(
            tenant_key, tokens_used, self._config.tenant_ttl_seconds
        )

        logger.info(
            "Token usage recorded | user=%s user_daily=%d | "
            "tenant=%s tenant_monthly=%d | tokens=%d provider=%s purpose=%s",
            user_id,
            new_user_total,
            tenant_id,
            new_tenant_total,
            tokens_used,
            provider,
            purpose,
        )

        # Check if tenant alert threshold crossed
        alert_at = int(self._config.tenant_monthly_token_limit * self._config.tenant_alert_threshold_pct)
        if new_tenant_total >= alert_at:
            pct = new_tenant_total / self._config.tenant_monthly_token_limit
            _emit_cost_alert(tenant_id, new_tenant_total, self._config.tenant_monthly_token_limit, pct)

    async def get_usage_summary(
        self,
        user_id: str,
        tenant_id: str,
    ) -> dict[str, Any]:
        """Return current usage counters for health/status endpoints."""
        user_used = await self._get_user_usage(user_id)
        tenant_used = await self._get_tenant_usage(tenant_id)
        return {
            "user_id": user_id,
            "user_daily_used": user_used,
            "user_daily_limit": self._config.user_daily_token_limit,
            "user_daily_remaining": max(0, self._config.user_daily_token_limit - user_used),
            "tenant_id": tenant_id,
            "tenant_monthly_used": tenant_used,
            "tenant_monthly_limit": self._config.tenant_monthly_token_limit,
            "tenant_monthly_remaining": max(0, self._config.tenant_monthly_token_limit - tenant_used),
            "tenant_alert_threshold": self._config.tenant_alert_threshold_pct,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get_user_usage(self, user_id: str) -> int:
        return await self._counter.get(self._user_key(user_id))

    async def _get_tenant_usage(self, tenant_id: str) -> int:
        return await self._counter.get(self._tenant_key(tenant_id))

    @staticmethod
    def _user_key(user_id: str) -> str:
        return f"eduboost:budget:user:{user_id}:daily"

    @staticmethod
    def _tenant_key(tenant_id: str) -> str:
        from datetime import datetime
        ym = datetime.utcnow().strftime("%Y-%m")
        return f"eduboost:budget:tenant:{tenant_id}:monthly:{ym}"
