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


@pytest.mark.asyncio
async def test_check_and_reserve_async_with_redis():
    """Verify check_and_reserve_async coordinates atomically with Redis."""
    from unittest.mock import AsyncMock

    mock_redis = AsyncMock()
    mock_redis.incrby.return_value = 1500
    mock_redis.expire = AsyncMock()

    guard = AIBudgetGuard(max_tokens_per_request=2000, daily_budget=5000, redis_client=mock_redis)
    result = await guard.check_and_reserve_async(1500)

    assert result == 1500
    mock_redis.incrby.assert_awaited_once()
    mock_redis.expire.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_and_reserve_async_redis_exceeded_rolls_back():
    """Verify exceeding daily budget in Redis rolls back counter with decrby."""
    from unittest.mock import AsyncMock

    mock_redis = AsyncMock()
    mock_redis.incrby.return_value = 6000  # Exceeds 5000 daily budget
    mock_redis.decrby = AsyncMock()

    guard = AIBudgetGuard(max_tokens_per_request=2000, daily_budget=5000, redis_client=mock_redis)
    with pytest.raises(HTTPException) as exc:
        await guard.check_and_reserve_async(1500)

    assert exc.value.status_code == 429
    assert "Daily AI budget exhausted" in exc.value.detail
    mock_redis.decrby.assert_awaited_once()


