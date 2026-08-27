"""Unit tests for AI Generation Budget Guard & Cost Kill-Switch (TSR-11.11)."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.services.ai_budget_guard import AIBudgetGuard, AIBudgetExceededError


@pytest.mark.unit
def test_valid_request_reserves_budget_successfully():
    guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=10000)
    usage = guard.check_and_reserve(500)
    assert usage == 500

    usage = guard.check_and_reserve(300)
    assert usage == 800


@pytest.mark.unit
def test_oversized_single_request_triggers_killswitch():
    guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=10000)

    with pytest.raises(HTTPException) as exc:
        guard.check_and_reserve(1500)

    assert exc.value.status_code == 429
    assert "exceed maximum single-request limit" in exc.value.detail
    assert exc.value.headers.get("X-AI-Budget-Status") == "EXCEEDED"


@pytest.mark.unit
def test_daily_budget_exhaustion_triggers_killswitch():
    guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=2000)
    guard.check_and_reserve(1000)
    guard.check_and_reserve(800)

    # Next 500 tokens will breach the 2000 total budget
    with pytest.raises(HTTPException) as exc:
        guard.check_and_reserve(500)

    assert exc.value.status_code == 429
    assert "Daily AI budget exhausted" in exc.value.detail
