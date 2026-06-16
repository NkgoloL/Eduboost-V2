"""Phase 6 durable budget authority and AI usage accounting."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.metrics import (
    ai_budget_blocks_total,
    ai_budget_reserved_tokens,
    ai_budget_usage_ratio,
    ai_usage_cost_usd_total,
    ai_usage_tokens_total,
)
from app.models.ai_operations import AIBudgetCounter, AIUsageEvent, AIUsageReservation


class AIBudgetExceededError(RuntimeError):
    def __init__(self, scope: str, used: int, reserved: int, requested: int, limit: int) -> None:
        self.scope = scope
        self.used = used
        self.reserved = reserved
        self.requested = requested
        self.limit = limit
        super().__init__(f"AI budget exceeded for {scope}: {used}+{reserved}+{requested}>{limit}")


@dataclass(frozen=True)
class BudgetLimits:
    user_daily_tokens: int
    tenant_monthly_tokens: int
    alert_threshold: float
    reservation_ttl_seconds: int

    @classmethod
    def from_settings(cls) -> "BudgetLimits":
        return cls(
            user_daily_tokens=int(getattr(settings, "USER_DAILY_TOKEN_LIMIT", 50_000)),
            tenant_monthly_tokens=int(getattr(settings, "TENANT_MONTHLY_TOKEN_LIMIT", 10_000_000)),
            alert_threshold=float(getattr(settings, "TENANT_BUDGET_ALERT_PCT", 0.80)),
            reservation_ttl_seconds=int(getattr(settings, "AI_USAGE_RESERVATION_TTL_SECONDS", 300)),
        )


_PRICING: dict[str, tuple[Decimal, Decimal]] = {
    "azure_openai": (Decimal("0.00000015"), Decimal("0.00000060")),
    "anthropic": (Decimal("0.00000300"), Decimal("0.00001500")),
    "groq": (Decimal("0.00000059"), Decimal("0.00000079")),
    "deterministic": (Decimal("0"), Decimal("0")),
    "fallback": (Decimal("0"), Decimal("0")),
}


def estimate_cost(provider: str, prompt_tokens: int, completion_tokens: int) -> Decimal:
    input_price, output_price = _PRICING.get(provider, (Decimal("0"), Decimal("0")))
    value = input_price * prompt_tokens + output_price * completion_tokens
    return value.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)


def _day_key(now: datetime) -> str:
    return now.astimezone(UTC).strftime("%Y-%m-%d")


def _month_key(now: datetime) -> str:
    return now.astimezone(UTC).strftime("%Y-%m")


class AIOperationsService:
    """PostgreSQL-backed source of truth for reservations and actual usage."""

    def __init__(self, db: AsyncSession, *, limits: BudgetLimits | None = None) -> None:
        self.db = db
        self.limits = limits or BudgetLimits.from_settings()

    async def _ensure_counter(self, scope_type: str, scope_id: str, period_key: str) -> None:
        if self.db.bind and self.db.bind.dialect.name == "postgresql":
            stmt = pg_insert(AIBudgetCounter).values(
                scope_type=scope_type,
                scope_id=scope_id,
                period_key=period_key,
                used_tokens=0,
                reserved_tokens=0,
                used_cost_usd=Decimal("0"),
            ).on_conflict_do_nothing(
                index_elements=["scope_type", "scope_id", "period_key"]
            )
            await self.db.execute(stmt)
            return
        existing = await self.db.get(AIBudgetCounter, (scope_type, scope_id, period_key))
        if existing is None:
            self.db.add(AIBudgetCounter(scope_type=scope_type, scope_id=scope_id, period_key=period_key))
            await self.db.flush()

    async def _locked_counter(self, scope_type: str, scope_id: str, period_key: str) -> AIBudgetCounter:
        await self._ensure_counter(scope_type, scope_id, period_key)
        counter = await self.db.scalar(
            select(AIBudgetCounter)
            .where(
                AIBudgetCounter.scope_type == scope_type,
                AIBudgetCounter.scope_id == scope_id,
                AIBudgetCounter.period_key == period_key,
            )
            .with_for_update()
        )
        if counter is None:  # pragma: no cover - defensive database invariant
            raise RuntimeError("AI budget counter could not be created")
        return counter

    async def reserve(
        self,
        *,
        operation_id: str,
        user_id: str,
        tenant_id: str,
        purpose: str,
        estimated_tokens: int,
        metadata: dict[str, Any] | None = None,
        now: datetime | None = None,
    ) -> AIUsageReservation:
        if estimated_tokens <= 0:
            raise ValueError("estimated_tokens must be positive")
        now = now or datetime.now(UTC)
        prior = await self.db.scalar(
            select(AIUsageReservation).where(AIUsageReservation.operation_id == operation_id).with_for_update()
        )
        if prior is not None:
            return prior

        user_counter = await self._locked_counter("user", user_id, _day_key(now))
        tenant_counter = await self._locked_counter("tenant", tenant_id, _month_key(now))
        checks = (
            (f"user:{user_id}:daily", user_counter, self.limits.user_daily_tokens),
            (f"tenant:{tenant_id}:monthly", tenant_counter, self.limits.tenant_monthly_tokens),
        )
        for scope, counter, limit in checks:
            if counter.used_tokens + counter.reserved_tokens + estimated_tokens > limit:
                ai_budget_blocks_total.labels(scope=counter.scope_type, purpose=purpose).inc()
                raise AIBudgetExceededError(
                    scope,
                    counter.used_tokens,
                    counter.reserved_tokens,
                    estimated_tokens,
                    limit,
                )

        user_counter.reserved_tokens += estimated_tokens
        tenant_counter.reserved_tokens += estimated_tokens
        reservation = AIUsageReservation(
            operation_id=operation_id,
            user_id=user_id,
            tenant_id=tenant_id,
            purpose=purpose,
            estimated_tokens=estimated_tokens,
            metadata_json=metadata or {},
            expires_at=now + timedelta(seconds=self.limits.reservation_ttl_seconds),
        )
        self.db.add(reservation)
        await self.db.flush()
        ai_budget_reserved_tokens.labels(scope="user", purpose=purpose).inc(estimated_tokens)
        ai_budget_reserved_tokens.labels(scope="tenant", purpose=purpose).inc(estimated_tokens)
        return reservation

    async def finalize(
        self,
        *,
        operation_id: str,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        outcome: str = "success",
        metadata: dict[str, Any] | None = None,
        now: datetime | None = None,
    ) -> AIUsageEvent:
        now = now or datetime.now(UTC)
        reservation = await self.db.scalar(
            select(AIUsageReservation)
            .where(AIUsageReservation.operation_id == operation_id)
            .with_for_update()
        )
        if reservation is None:
            raise LookupError(f"No AI usage reservation for {operation_id}")
        existing = await self.db.scalar(select(AIUsageEvent).where(AIUsageEvent.operation_id == operation_id))
        if existing is not None:
            return existing
        if reservation.status != "pending":
            raise RuntimeError(f"Reservation {operation_id} is {reservation.status}")

        total_tokens = max(0, int(prompt_tokens)) + max(0, int(completion_tokens))
        cost = estimate_cost(provider, prompt_tokens, completion_tokens)
        user_counter = await self._locked_counter("user", reservation.user_id, _day_key(reservation.reserved_at))
        tenant_counter = await self._locked_counter("tenant", reservation.tenant_id, _month_key(reservation.reserved_at))
        overages: list[dict[str, Any]] = []
        for counter, limit in (
            (user_counter, self.limits.user_daily_tokens),
            (tenant_counter, self.limits.tenant_monthly_tokens),
        ):
            counter.reserved_tokens = max(0, counter.reserved_tokens - reservation.estimated_tokens)
            projected_used = counter.used_tokens + total_tokens
            if projected_used > limit:
                overages.append(
                    {
                        "scope_type": counter.scope_type,
                        "scope_id": counter.scope_id,
                        "limit": limit,
                        "used_before": counter.used_tokens,
                        "actual_tokens": total_tokens,
                        "overage_tokens": projected_used - limit,
                    }
                )
                ai_budget_blocks_total.labels(scope=counter.scope_type, purpose=reservation.purpose).inc()
            # Actual provider usage is always accounted, even when the estimate was low.
            # A counter over its limit causes subsequent reservations to fail closed.
            counter.used_tokens = projected_used
            counter.used_cost_usd += cost
            ratio = counter.used_tokens / max(1, limit)
            ai_budget_usage_ratio.labels(scope=counter.scope_type).set(ratio)

        event_metadata = dict(metadata or {})
        if overages:
            event_metadata["budget_overage"] = overages
            event_metadata["estimated_tokens"] = reservation.estimated_tokens
            outcome = "blocked"
            reservation.failure_reason = "actual_usage_exceeded_budget"

        event = AIUsageEvent(
            reservation_id=reservation.reservation_id,
            operation_id=operation_id,
            user_id=reservation.user_id,
            tenant_id=reservation.tenant_id,
            purpose=reservation.purpose,
            provider=provider,
            model=model,
            prompt_tokens=max(0, int(prompt_tokens)),
            completion_tokens=max(0, int(completion_tokens)),
            total_tokens=total_tokens,
            estimated_cost_usd=cost,
            outcome=outcome,
            metadata_json=event_metadata,
        )
        self.db.add(event)
        reservation.status = "finalized"
        reservation.finalized_at = now
        await self.db.flush()
        ai_usage_tokens_total.labels(provider=provider, model=model, purpose=reservation.purpose, outcome=outcome).inc(total_tokens)
        ai_usage_cost_usd_total.labels(provider=provider, model=model, purpose=reservation.purpose).inc(float(cost))
        return event

    async def cancel(self, operation_id: str, reason: str = "cancelled") -> AIUsageReservation | None:
        reservation = await self.db.scalar(
            select(AIUsageReservation).where(AIUsageReservation.operation_id == operation_id).with_for_update()
        )
        if reservation is None or reservation.status != "pending":
            return reservation
        user_counter = await self._locked_counter("user", reservation.user_id, _day_key(reservation.reserved_at))
        tenant_counter = await self._locked_counter("tenant", reservation.tenant_id, _month_key(reservation.reserved_at))
        user_counter.reserved_tokens = max(0, user_counter.reserved_tokens - reservation.estimated_tokens)
        tenant_counter.reserved_tokens = max(0, tenant_counter.reserved_tokens - reservation.estimated_tokens)
        reservation.status = "cancelled"
        reservation.failure_reason = reason[:96]
        reservation.finalized_at = datetime.now(UTC)
        return reservation

    async def expire_stale(self, *, now: datetime | None = None, limit: int = 500) -> int:
        now = now or datetime.now(UTC)
        reservations = list(
            (
                await self.db.scalars(
                    select(AIUsageReservation)
                    .where(AIUsageReservation.status == "pending", AIUsageReservation.expires_at <= now)
                    .order_by(AIUsageReservation.expires_at)
                    .limit(limit)
                    .with_for_update(skip_locked=True)
                )
            ).all()
        )
        for reservation in reservations:
            await self.cancel(reservation.operation_id, "expired")
            reservation.status = "expired"
        return len(reservations)

    async def counter_view(self, *, scope_type: str, scope_id: str, now: datetime | None = None) -> dict[str, Any]:
        now = now or datetime.now(UTC)
        period_key = _day_key(now) if scope_type == "user" else _month_key(now)
        limit = self.limits.user_daily_tokens if scope_type == "user" else self.limits.tenant_monthly_tokens
        await self._ensure_counter(scope_type, scope_id, period_key)
        counter = await self.db.get(AIBudgetCounter, (scope_type, scope_id, period_key))
        if counter is None:
            raise RuntimeError("Budget counter unavailable")
        consumed = counter.used_tokens + counter.reserved_tokens
        return {
            "scope_type": scope_type,
            "scope_id": scope_id,
            "period_key": period_key,
            "used_tokens": counter.used_tokens,
            "reserved_tokens": counter.reserved_tokens,
            "token_limit": limit,
            "remaining_tokens": max(0, limit - consumed),
            "used_cost_usd": counter.used_cost_usd,
            "alert_threshold_reached": consumed >= int(limit * self.limits.alert_threshold),
            "updated_at": counter.updated_at,
        }

    async def provider_health(self, *, since: datetime | None = None) -> list[dict[str, Any]]:
        since = since or (datetime.now(UTC) - timedelta(hours=24))
        rows = (
            await self.db.execute(
                select(
                    AIUsageEvent.provider,
                    func.count(AIUsageEvent.event_id),
                    func.count(AIUsageEvent.event_id).filter(AIUsageEvent.outcome == "error"),
                    func.count(AIUsageEvent.event_id).filter(AIUsageEvent.outcome == "fallback"),
                )
                .where(AIUsageEvent.created_at >= since)
                .group_by(AIUsageEvent.provider)
            )
        ).all()
        result = []
        for provider, calls, errors, fallbacks in rows:
            error_rate = float(errors or 0) / max(1, int(calls or 0))
            status = "unavailable" if error_rate >= 0.5 else ("degraded" if error_rate >= 0.1 else "healthy")
            result.append({
                "provider": provider,
                "calls_24h": int(calls or 0),
                "errors_24h": int(errors or 0),
                "fallback_24h": int(fallbacks or 0),
                "error_rate": error_rate,
                "status": status,
            })
        return result
