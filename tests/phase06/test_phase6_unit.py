from decimal import Decimal

import pytest

from app.domain.ai_operations_schemas import ReservationCancelRequest
from app.services.ai_operations import BudgetLimits, estimate_cost


def test_estimate_cost_known_provider():
    assert estimate_cost("azure_openai", 1000, 1000) == Decimal("0.00075000")


def test_estimate_cost_unknown_provider_is_zero():
    assert estimate_cost("unknown", 999, 999) == Decimal("0E-8")


def test_budget_limits_from_settings_are_positive():
    limits = BudgetLimits.from_settings()
    assert limits.user_daily_tokens > 0
    assert limits.tenant_monthly_tokens > limits.user_daily_tokens
    assert 0 < limits.alert_threshold <= 1


def test_strict_cancel_schema_rejects_unknown_fields():
    with pytest.raises(Exception):
        ReservationCancelRequest(reason="manual correction", actor_id="spoof")
