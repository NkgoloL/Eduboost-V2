"""Comprehensive unit tests for AI operations cost estimation and RuntimeKGRepository."""
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock
import pytest

from app.services.ai_operations import (
    estimate_cost,
    BudgetLimits,
    AIBudgetExceededError,
    _day_key,
    _month_key,
)
from app.services.runtime_kg.repository import RuntimeKGRepository


class TestAIOperationsCostAndBudget:
    def test_estimate_cost_providers(self):
        # Azure OpenAI
        c_azure = estimate_cost("azure_openai", 1000, 500)
        assert isinstance(c_azure, Decimal)
        assert c_azure > Decimal("0")

        # Anthropic
        c_anthropic = estimate_cost("anthropic", 1000, 500)
        assert isinstance(c_anthropic, Decimal)
        assert c_anthropic > c_azure

        # Deterministic / Free
        c_det = estimate_cost("deterministic", 1000, 500)
        assert c_det == Decimal("0")

        # Unknown fallback
        c_fallback = estimate_cost("unknown_provider", 1000, 500)
        assert c_fallback == Decimal("0")

    def test_budget_limits_from_settings(self):
        limits = BudgetLimits.from_settings()
        assert limits.user_daily_tokens > 0
        assert limits.tenant_monthly_tokens > 0
        assert 0.0 < limits.alert_threshold <= 1.0

    def test_day_and_month_key(self):
        dt = datetime(2026, 8, 28, 10, 0, 0, tzinfo=UTC)
        assert _day_key(dt) == "2026-08-28"
        assert _month_key(dt) == "2026-08"

    def test_ai_budget_exceeded_error(self):
        err = AIBudgetExceededError("user:123", used=45000, reserved=5000, requested=1000, limit=50000)
        assert "AI budget exceeded" in str(err)
        assert err.scope == "user:123"


class TestRuntimeKGRepository:
    def test_repository_init(self):
        mock_db = AsyncMock()
        repo = RuntimeKGRepository(mock_db)
        assert repo.db == mock_db
        assert repo.loader is not None
