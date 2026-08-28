"""Comprehensive unit tests for AI operations cost estimation, keys, and budget limits."""
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
import pytest

from app.services.ai_operations import (
    AIBudgetExceededError,
    BudgetLimits,
    estimate_cost,
    _day_key,
    _month_key,
)


class TestAIOperationsCostAndKeys:
    def test_estimate_cost_groq(self):
        cost = estimate_cost("groq", prompt_tokens=1000, completion_tokens=500)
        assert isinstance(cost, Decimal)
        assert cost > Decimal("0")

    def test_estimate_cost_deterministic_and_unknown(self):
        cost_det = estimate_cost("deterministic", prompt_tokens=1000, completion_tokens=500)
        assert cost_det == Decimal("0")

        cost_unknown = estimate_cost("unknown_provider", prompt_tokens=1000, completion_tokens=500)
        assert cost_unknown == Decimal("0")

    def test_day_and_month_key_formatting(self):
        dt = datetime(2026, 8, 28, 15, 30, 0, tzinfo=UTC)
        assert _day_key(dt) == "2026-08-28"
        assert _month_key(dt) == "2026-08"

    def test_budget_limits_from_settings(self):
        limits = BudgetLimits.from_settings()
        assert limits.user_daily_tokens > 0
        assert limits.tenant_monthly_tokens > 0
        assert 0.0 < limits.alert_threshold <= 1.0
        assert limits.reservation_ttl_seconds > 0

    def test_ai_budget_exceeded_error(self):
        err = AIBudgetExceededError(
            scope="user_123",
            used=45000,
            reserved=4000,
            requested=2000,
            limit=50000,
        )
        assert err.scope == "user_123"
        assert err.used == 45000
        assert err.reserved == 4000
        assert err.requested == 2000
        assert err.limit == 50000
        assert "45000+4000+2000>50000" in str(err)
