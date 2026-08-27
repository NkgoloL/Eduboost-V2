"""Comprehensive unit tests for AI Operations, LLM Core Engine, and IRT Quality Fitting."""
from __future__ import annotations

import math
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.ai_operations import (
    AIBudgetExceededError,
    BudgetLimits,
    estimate_cost,
    _day_key,
    _month_key,
)
from app.services.irt_quality_service import (
    _sigmoid,
    fit_two_parameter_logistic,
    IRTQualityError,
    IRTQualityConflict,
)
from app.domain.irt_quality_schemas import (
    IRTCalibrationObservation,
)
from app.core.llm import (
    _resolve_project_path,
)


# ---------------------------------------------------------------------------
# AI Operations & Budget Accounting Tests
# ---------------------------------------------------------------------------

class TestAIOperations:
    def test_estimate_cost_azure_openai(self):
        cost = estimate_cost("azure_openai", prompt_tokens=1000, completion_tokens=500)
        assert isinstance(cost, Decimal)
        assert cost > Decimal("0")

    def test_estimate_cost_deterministic_free(self):
        cost = estimate_cost("deterministic", prompt_tokens=5000, completion_tokens=2000)
        assert cost == Decimal("0")

    def test_budget_exceeded_error_message(self):
        err = AIBudgetExceededError(
            scope="user:123",
            used=45000,
            reserved=5000,
            requested=2000,
            limit=50000,
        )
        assert "AI budget exceeded" in str(err)
        assert err.scope == "user:123"
        assert err.limit == 50000

    def test_budget_limits_dataclass(self):
        limits = BudgetLimits(
            user_daily_tokens=50000,
            tenant_monthly_tokens=10000000,
            alert_threshold=0.80,
            reservation_ttl_seconds=300,
        )
        assert limits.user_daily_tokens == 50000
        assert limits.alert_threshold == 0.80

    def test_date_key_formatters(self):
        dt = datetime(2026, 8, 27, 12, 0, 0, tzinfo=timezone.utc)
        assert _day_key(dt) == "2026-08-27"
        assert _month_key(dt) == "2026-08"


# ---------------------------------------------------------------------------
# IRT Quality Logistic Fitting & Error Tests
# ---------------------------------------------------------------------------

class TestIRTQualityFitting:
    def test_sigmoid_values(self):
        assert _sigmoid(0.0) == 0.5
        assert _sigmoid(100.0) > 0.999
        assert _sigmoid(-100.0) < 0.001

    def test_fit_empty_observations(self):
        a, b, loss, converged = fit_two_parameter_logistic([])
        assert a == 1.0
        assert b == 0.0
        assert converged is False

    def test_fit_simple_observations(self):
        lid = uuid.uuid4()
        sid = uuid.uuid4()
        obs = [
            IRTCalibrationObservation(learner_id=lid, session_id=sid, ability_proxy=1.0, is_correct=True),
            IRTCalibrationObservation(learner_id=lid, session_id=sid, ability_proxy=-1.0, is_correct=False),
            IRTCalibrationObservation(learner_id=lid, session_id=sid, ability_proxy=0.0, is_correct=True),
        ]
        a, b, loss, converged = fit_two_parameter_logistic(obs, iterations=10)
        assert isinstance(a, float)
        assert isinstance(b, float)
        assert isinstance(loss, float)

    def test_irt_quality_error_classes(self):
        err = IRTQualityError("Quality calibration failure")
        assert isinstance(err, RuntimeError)
        conflict = IRTQualityConflict("Concurrent override conflict")
        assert isinstance(conflict, IRTQualityError)


# ---------------------------------------------------------------------------
# LLM Core Helper Tests
# ---------------------------------------------------------------------------

class TestLLMCoreHelpers:
    def test_resolve_project_path_relative(self):
        resolved = _resolve_project_path("data/caps")
        assert resolved.is_absolute()

    def test_resolve_project_path_absolute(self):
        resolved = _resolve_project_path("/tmp/test_file.txt")
        assert str(resolved) == "/tmp/test_file.txt"
