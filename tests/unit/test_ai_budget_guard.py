"""Unit tests for AI Generation Budget Guard & Cost Kill-Switch (TSR-11.11)."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.services.ai_budget_guard import AIBudgetGuard, AIBudgetExceededError


@pytest.mark.unit
def test_valid_request_reserves_budget_successfully():
    guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=10000)
    guard.reset_usage()
    usage = guard.check_and_reserve(500)
    assert usage == 500

    usage = guard.check_and_reserve(300)
    assert usage == 800


@pytest.mark.unit
def test_oversized_single_request_triggers_killswitch():
    guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=10000)
    guard.reset_usage()

    with pytest.raises(HTTPException) as exc:
        guard.check_and_reserve(1500)

    assert exc.value.status_code == 429
    assert "exceed maximum single-request limit" in exc.value.detail
    assert exc.value.headers.get("X-AI-Budget-Status") == "EXCEEDED"


@pytest.mark.unit
def test_daily_budget_exhaustion_triggers_killswitch():
    guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=2000)
    guard.reset_usage()
    guard.check_and_reserve(1000)
    guard.check_and_reserve(800)

    # Next 500 tokens will breach the 2000 total budget
    with pytest.raises(HTTPException) as exc:
        guard.check_and_reserve(500)

    assert exc.value.status_code == 429
    assert "Daily AI budget exhausted" in exc.value.detail


@pytest.mark.unit
def test_multi_process_shared_budget_tracking():
    """Verify separate worker instances coordinate against shared day-keyed budget."""
    worker_1 = AIBudgetGuard(max_tokens_per_request=2000, daily_budget=3000)
    worker_1.reset_usage()

    worker_2 = AIBudgetGuard(max_tokens_per_request=2000, daily_budget=3000)

    # Worker 1 reserves 1500 tokens
    worker_1.check_and_reserve(1500)

    # Worker 2 attempts 1800 tokens -> breaches 3000 total budget
    with pytest.raises(HTTPException) as exc:
        worker_2.check_and_reserve(1800)

    assert exc.value.status_code == 429
    assert "Daily AI budget exhausted" in exc.value.detail

