"""
Unit tests for app.services.ai_operations module.
Covers AIBudgetExceededError, BudgetLimits, estimate_cost, and helper fns.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.services.ai_operations import (
    AIBudgetExceededError,
    BudgetLimits,
    estimate_cost,
    _day_key,
    _month_key,
)


class TestAIBudgetExceededError:
    def test_message_format(self):
        err = AIBudgetExceededError(
            scope="user:u1", used=40_000, reserved=8_000, requested=5_000, limit=50_000
        )
        assert "user:u1" in str(err)
        assert err.scope == "user:u1"
        assert err.used == 40_000
        assert err.reserved == 8_000
        assert err.requested == 5_000
        assert err.limit == 50_000

    def test_is_runtime_error(self):
        err = AIBudgetExceededError("scope", 0, 0, 100, 50)
        assert isinstance(err, RuntimeError)


class TestBudgetLimits:
    def test_from_settings_returns_budget_limits(self):
        limits = BudgetLimits.from_settings()
        assert isinstance(limits.user_daily_tokens, int)
        assert isinstance(limits.tenant_monthly_tokens, int)
        assert isinstance(limits.alert_threshold, float)
        assert isinstance(limits.reservation_ttl_seconds, int)
        assert limits.user_daily_tokens > 0

    def test_direct_init(self):
        limits = BudgetLimits(
            user_daily_tokens=100_000,
            tenant_monthly_tokens=5_000_000,
            alert_threshold=0.75,
            reservation_ttl_seconds=600,
        )
        assert limits.user_daily_tokens == 100_000
        assert limits.alert_threshold == 0.75


class TestEstimateCost:
    def test_known_provider(self):
        cost = estimate_cost("anthropic", prompt_tokens=1_000, completion_tokens=500)
        assert isinstance(cost, Decimal)
        assert cost > Decimal("0")

    def test_deterministic_provider_is_zero(self):
        cost = estimate_cost("deterministic", prompt_tokens=9_999, completion_tokens=9_999)
        assert cost == Decimal("0")

    def test_unknown_provider_returns_zero(self):
        cost = estimate_cost("unknown-provider", prompt_tokens=1_000, completion_tokens=1_000)
        assert cost == Decimal("0")

    def test_azure_openai(self):
        cost = estimate_cost("azure_openai", prompt_tokens=10_000, completion_tokens=5_000)
        assert cost > Decimal("0")

    def test_groq(self):
        cost = estimate_cost("groq", prompt_tokens=10_000, completion_tokens=5_000)
        assert cost > Decimal("0")

    def test_precision_returned(self):
        cost = estimate_cost("anthropic", prompt_tokens=1, completion_tokens=1)
        # Result should have 8 decimal places (quantized to 0.00000001)
        sign, digits, exponent = cost.as_tuple()
        assert exponent >= -8


class TestKeyHelpers:
    def test_day_key_format(self):
        dt = datetime(2026, 8, 2, 10, 30, tzinfo=timezone.utc)
        assert _day_key(dt) == "2026-08-02"

    def test_month_key_format(self):
        dt = datetime(2026, 8, 2, 10, 30, tzinfo=timezone.utc)
        assert _month_key(dt) == "2026-08"

    def test_day_key_different_dates_differ(self):
        dt1 = datetime(2026, 8, 1, tzinfo=timezone.utc)
        dt2 = datetime(2026, 8, 2, tzinfo=timezone.utc)
        assert _day_key(dt1) != _day_key(dt2)
