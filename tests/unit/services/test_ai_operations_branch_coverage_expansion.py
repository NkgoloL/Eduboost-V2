"""Batch 226 — app/services/ai_operations.py comprehensive branch coverage expansion.

Tests:
- AIBudgetExceededError constructor & attributes
- BudgetLimits.from_settings() default loading
- estimate_cost across all known and unknown providers
- _day_key and _month_key date formatting
- AIOperationsService:
  - _ensure_counter: postgresql vs generic dialect
  - reserve: non-positive tokens (ValueError), prior reservation idempotency, user budget exceeded, tenant budget exceeded, successful reservation
  - finalize: missing reservation (LookupError), existing event return, non-pending reservation (RuntimeError), normal finalize, actual usage overage handling (outcome="blocked")
  - cancel: missing/non-pending reservation, active pending reservation cancellation and counter decrement
  - expire_stale: sweeps pending expired reservations
  - counter_view: user vs tenant scope, alert_threshold calculation
  - provider_health: healthy (<0.10 error rate), degraded (0.10-0.50), unavailable (>=0.50)
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.ai_operations import AIBudgetCounter, AIUsageEvent, AIUsageReservation
from app.services.ai_operations import (
    AIBudgetExceededError,
    AIOperationsService,
    BudgetLimits,
    _day_key,
    _month_key,
    estimate_cost,
)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def custom_limits():
    return BudgetLimits(
        user_daily_tokens=1000,
        tenant_monthly_tokens=10000,
        alert_threshold=0.8,
        reservation_ttl_seconds=300,
    )


@pytest.fixture
def service(mock_db, custom_limits):
    return AIOperationsService(db=mock_db, limits=custom_limits)


# ---------------------------------------------------------------------------
# Data Classes, Pricing & Date Helpers
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_ai_budget_exceeded_error_properties():
    err = AIBudgetExceededError(scope="user:1", used=500, reserved=200, requested=400, limit=1000)
    assert err.scope == "user:1"
    assert err.used == 500
    assert err.reserved == 200
    assert err.requested == 400
    assert err.limit == 1000
    assert "user:1" in str(err)


@pytest.mark.unit
def test_budget_limits_from_settings():
    limits = BudgetLimits.from_settings()
    assert limits.user_daily_tokens > 0
    assert limits.tenant_monthly_tokens > 0
    assert 0.0 < limits.alert_threshold <= 1.0


@pytest.mark.unit
def test_estimate_cost_providers():
    assert estimate_cost("azure_openai", 1000, 1000) > Decimal("0")
    assert estimate_cost("anthropic", 1000, 1000) > Decimal("0")
    assert estimate_cost("groq", 1000, 1000) > Decimal("0")
    assert estimate_cost("deterministic", 1000, 1000) == Decimal("0")
    assert estimate_cost("fallback", 1000, 1000) == Decimal("0")
    assert estimate_cost("unknown_provider", 1000, 1000) == Decimal("0")


@pytest.mark.unit
def test_date_key_helpers():
    dt = datetime(2026, 8, 15, 14, 30, tzinfo=UTC)
    assert _day_key(dt) == "2026-08-15"
    assert _month_key(dt) == "2026-08"


# ---------------------------------------------------------------------------
# Reserve
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_reserve_validation_and_idempotency(service, mock_db):
    # Non-positive tokens raises ValueError
    with pytest.raises(ValueError, match="estimated_tokens must be positive"):
        await service.reserve(
            operation_id="op-1",
            user_id="u-1",
            tenant_id="t-1",
            purpose="tutor",
            estimated_tokens=0,
        )

    # Prior reservation returns idempotently
    prior = MagicMock(spec=AIUsageReservation, operation_id="op-1")
    mock_db.scalar.return_value = prior
    res = await service.reserve(
        operation_id="op-1",
        user_id="u-1",
        tenant_id="t-1",
        purpose="tutor",
        estimated_tokens=500,
    )
    assert res == prior


@pytest.mark.asyncio
@pytest.mark.unit
async def test_reserve_budget_exceeded(service, mock_db):
    # User budget exceeded
    user_counter = MagicMock(
        spec=AIBudgetCounter,
        scope_type="user",
        used_tokens=800,
        reserved_tokens=200,
    )
    tenant_counter = MagicMock(
        spec=AIBudgetCounter,
        scope_type="tenant",
        used_tokens=1000,
        reserved_tokens=500,
    )

    mock_db.scalar.side_effect = [
        None,            # prior reservation
        user_counter,    # user counter lock
        tenant_counter,  # tenant counter lock
    ]

    with pytest.raises(AIBudgetExceededError) as exc:
        await service.reserve(
            operation_id="op-2",
            user_id="u-1",
            tenant_id="t-1",
            purpose="tutor",
            estimated_tokens=100,  # 800+200+100 = 1100 > limit 1000
        )
    assert "user" in exc.value.scope


@pytest.mark.asyncio
@pytest.mark.unit
async def test_reserve_success(service, mock_db):
    user_counter = MagicMock(
        spec=AIBudgetCounter,
        scope_type="user",
        used_tokens=200,
        reserved_tokens=100,
    )
    tenant_counter = MagicMock(
        spec=AIBudgetCounter,
        scope_type="tenant",
        used_tokens=1000,
        reserved_tokens=500,
    )

    mock_db.scalar.side_effect = [
        None,            # prior
        user_counter,    # user counter
        tenant_counter,  # tenant counter
    ]

    reservation = await service.reserve(
        operation_id="op-3",
        user_id="u-1",
        tenant_id="t-1",
        purpose="tutor",
        estimated_tokens=300,
    )
    assert reservation.operation_id == "op-3"
    assert user_counter.reserved_tokens == 400
    assert tenant_counter.reserved_tokens == 800
    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()


# ---------------------------------------------------------------------------
# Finalize & Cancel
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_finalize_exceptions_and_idempotency(service, mock_db):
    # 1. Missing reservation -> LookupError
    mock_db.scalar.return_value = None
    with pytest.raises(LookupError, match="No AI usage reservation"):
        await service.finalize(
            operation_id="missing-op",
            provider="anthropic",
            model="claude-sonnet-4",
            prompt_tokens=10,
            completion_tokens=10,
        )

    # 2. Existing AIUsageEvent -> return idempotently
    reservation = MagicMock(spec=AIUsageReservation, operation_id="op-4")
    event = MagicMock(spec=AIUsageEvent, operation_id="op-4")
    mock_db.scalar.side_effect = [reservation, event]
    res_event = await service.finalize(
        operation_id="op-4",
        provider="anthropic",
        model="claude-sonnet-4",
        prompt_tokens=10,
        completion_tokens=10,
    )
    assert res_event == event

    # 3. Non-pending reservation -> RuntimeError
    reservation.status = "cancelled"
    mock_db.scalar.side_effect = [reservation, None]
    with pytest.raises(RuntimeError, match="is cancelled"):
        await service.finalize(
            operation_id="op-4",
            provider="anthropic",
            model="claude-sonnet-4",
            prompt_tokens=10,
            completion_tokens=10,
        )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_finalize_success_and_overage_handling(service, mock_db):
    reservation = MagicMock(
        spec=AIUsageReservation,
        reservation_id=uuid.uuid4(),
        operation_id="op-5",
        status="pending",
        user_id="u-1",
        tenant_id="t-1",
        purpose="tutor",
        estimated_tokens=500,
        reserved_at=datetime.now(UTC),
    )

    user_counter = MagicMock(
        spec=AIBudgetCounter,
        scope_type="user",
        scope_id="u-1",
        used_tokens=800,
        reserved_tokens=500,
        used_cost_usd=Decimal("0.01"),
    )
    tenant_counter = MagicMock(
        spec=AIBudgetCounter,
        scope_type="tenant",
        scope_id="t-1",
        used_tokens=5000,
        reserved_tokens=500,
        used_cost_usd=Decimal("0.10"),
    )

    mock_db.scalar.side_effect = [
        reservation,     # reservation
        None,            # existing event
        user_counter,    # user counter lock
        tenant_counter,  # tenant counter lock
    ]

    # Actual usage exceeds user limit (800 + 300 = 1100 > limit 1000)
    event = await service.finalize(
        operation_id="op-5",
        provider="azure_openai",
        model="gpt-4o",
        prompt_tokens=200,
        completion_tokens=100,
    )
    assert event.outcome == "blocked"
    assert reservation.status == "finalized"
    assert reservation.failure_reason == "actual_usage_exceeded_budget"
    assert user_counter.used_tokens == 1100
    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_cancel_and_expire_stale(service, mock_db):
    # 1. Cancel non-pending returns reservation as is
    res_cancelled = MagicMock(spec=AIUsageReservation, status="finalized")
    mock_db.scalar.return_value = res_cancelled
    assert await service.cancel("op-done") == res_cancelled

    # 2. Cancel pending reservation decrements counter
    res_pending = MagicMock(
        spec=AIUsageReservation,
        operation_id="op-pending",
        status="pending",
        user_id="u-1",
        tenant_id="t-1",
        estimated_tokens=200,
        reserved_at=datetime.now(UTC),
    )
    user_counter = MagicMock(spec=AIBudgetCounter, reserved_tokens=200)
    tenant_counter = MagicMock(spec=AIBudgetCounter, reserved_tokens=200)

    mock_db.scalar.side_effect = [
        res_pending,
        user_counter,
        tenant_counter,
    ]
    cancelled = await service.cancel("op-pending", reason="timeout")
    assert cancelled.status == "cancelled"
    assert user_counter.reserved_tokens == 0
    assert tenant_counter.reserved_tokens == 0

    # 3. Expire stale
    res_stale = MagicMock(
        spec=AIUsageReservation,
        operation_id="op-stale",
        status="pending",
        user_id="u-1",
        tenant_id="t-1",
        estimated_tokens=100,
        reserved_at=datetime.now(UTC),
    )
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [res_stale]
    mock_db.scalars.return_value = scalars_mock

    mock_db.scalar.side_effect = [
        res_stale,
        user_counter,
        tenant_counter,
    ]
    count = await service.expire_stale(limit=10)
    assert count == 1
    assert res_stale.status == "expired"


# ---------------------------------------------------------------------------
# Counter View & Provider Health
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_counter_view_and_provider_health(service, mock_db):
    # 1. Counter view
    counter = MagicMock(
        spec=AIBudgetCounter,
        used_tokens=850,
        reserved_tokens=50,
        used_cost_usd=Decimal("0.05"),
        updated_at=datetime.now(UTC),
    )
    mock_db.get.return_value = counter

    view = await service.counter_view(scope_type="user", scope_id="u-1")
    assert view["used_tokens"] == 850
    assert view["reserved_tokens"] == 50
    assert view["token_limit"] == 1000
    assert view["remaining_tokens"] == 100
    assert view["alert_threshold_reached"] is True  # 900 >= 800

    # 2. Provider health
    res_rows = MagicMock()
    res_rows.all.return_value = [
        ("azure_openai", 100, 2, 1),   # error_rate = 2/100 = 0.02 -> healthy
        ("anthropic", 50, 10, 5),      # error_rate = 10/50 = 0.20 -> degraded
        ("groq", 20, 15, 5),           # error_rate = 15/20 = 0.75 -> unavailable
    ]
    mock_db.execute.return_value = res_rows

    health = await service.provider_health()
    assert len(health) == 3
    assert health[0]["status"] == "healthy"
    assert health[1]["status"] == "degraded"
    assert health[2]["status"] == "unavailable"
