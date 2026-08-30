from datetime import datetime, timezone
from decimal import Decimal
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.ai_operations import (
    AIBudgetExceededError,
    BudgetLimits,
    estimate_cost,
    _day_key,
    _month_key,
    AIOperationsService,
)


def test_ai_budget_exceeded_error():
    err = AIBudgetExceededError("user:123", used=1000, reserved=500, requested=200, limit=1500)
    assert err.scope == "user:123"
    assert "1000+500+200>1500" in str(err)


def test_budget_limits_defaults():
    limits = BudgetLimits.from_settings()
    assert limits.user_daily_tokens > 0
    assert limits.tenant_monthly_tokens > 0
    assert limits.alert_threshold > 0


def test_estimate_cost():
    cost_groq = estimate_cost("groq", prompt_tokens=1000, completion_tokens=1000)
    assert cost_groq > Decimal("0")

    cost_fallback = estimate_cost("fallback", prompt_tokens=1000, completion_tokens=1000)
    assert cost_fallback == Decimal("0")


def test_date_keys():
    dt = datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc)
    assert _day_key(dt) == "2026-08-29"
    assert _month_key(dt) == "2026-08"


@pytest.mark.asyncio
async def test_ai_operations_service_init():
    db = AsyncMock()
    service = AIOperationsService(db)
    assert service.db == db
    assert service.limits.user_daily_tokens > 0
