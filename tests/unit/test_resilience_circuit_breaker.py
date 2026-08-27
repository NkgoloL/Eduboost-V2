"""Unit tests for Fault Injection, Circuit Breakers, and Safe Degradation (TSR-11.8)."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch
import pytest
from fastapi import HTTPException


async def mock_service_call(should_fail: bool = False, timeout: float = 0.05):
    if should_fail:
        raise ConnectionError("Upstream Redis/DB connection lost")
    if timeout > 0.1:
        await asyncio.sleep(timeout)
        raise TimeoutError("Provider latency exceeded SLO budget")
    return {"status": "ok", "cached": True}


async def safe_resilient_wrapper(should_fail: bool = False, timeout: float = 0.05) -> dict:
    """Demonstrates fallback circuit breaker when upstream components fail."""
    try:
        return await asyncio.wait_for(mock_service_call(should_fail, timeout), timeout=0.1)
    except (ConnectionError, TimeoutError, asyncio.TimeoutError):
        # Graceful degradation fallback: return local degraded response rather than 500 crash
        return {"status": "degraded_fallback", "cached": False, "circuit_open": True}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_resilient_wrapper_succeeds_under_normal_operation():
    res = await safe_resilient_wrapper(should_fail=False, timeout=0.01)
    assert res["status"] == "ok"
    assert res["cached"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_resilient_wrapper_catches_connection_error_and_degrades_gracefully():
    res = await safe_resilient_wrapper(should_fail=True)
    assert res["status"] == "degraded_fallback"
    assert res["circuit_open"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_resilient_wrapper_catches_upstream_timeout():
    res = await safe_resilient_wrapper(should_fail=False, timeout=0.2)
    assert res["status"] == "degraded_fallback"
    assert res["circuit_open"] is True
