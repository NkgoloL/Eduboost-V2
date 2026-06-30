"""Unit tests for app.modules.lessons.llm_gateway_v2 (no network)."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.modules.lessons.llm_gateway_v2 import (
    CircuitBreaker,
    CircuitState,
    LLMGatewayError,
    LLMGatewayV2,
    ProviderUnavailableError,
    _STATIC_FALLBACK_RESPONSE,
)


@pytest.mark.unit
def test_circuit_breaker_opens_after_threshold():
    breaker = CircuitBreaker(name="test", failure_threshold=2, recovery_timeout_s=0.01)
    breaker.record_failure()
    assert breaker.state == CircuitState.CLOSED
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    assert breaker.is_available() is False


@pytest.mark.unit
def test_circuit_breaker_recovers_after_timeout():
    breaker = CircuitBreaker(name="test", failure_threshold=1, recovery_timeout_s=0.01)
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    # wait for recovery window to elapse before probing state
    import time
    time.sleep(0.02)
    assert breaker.state == CircuitState.HALF_OPEN
    breaker.record_success()
    assert breaker.state == CircuitState.CLOSED
    assert breaker.is_available() is True


@pytest.mark.unit
def test_llm_gateway_error_hierarchy():
    assert issubclass(ProviderUnavailableError, LLMGatewayError)
    assert issubclass(LLMGatewayError, Exception)


class _FakeAdapter:
    def __init__(self, responses: list[dict | Exception]) -> None:
        self._responses = list(responses)
        self.calls = 0

    async def complete(self, **kwargs):
        self.calls += 1
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return dict(item)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_gateway_returns_first_successful_provider():
    groq = _FakeAdapter([{"content": "ok", "provider": "groq", "model": "m", "used_fallback": False,
                           "prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3}])
    gateway = LLMGatewayV2(groq_adapter=groq, anthropic_adapter=None)
    result = await gateway.complete(prompt="hello")
    assert result["content"] == "ok"
    assert result["provider"] == "groq"
    assert "latency_ms" in result
    assert groq.calls == 1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_gateway_falls_through_to_second_provider():
    groq = _FakeAdapter([LLMGatewayError("groq down")] * 3)
    anth = _FakeAdapter([{"content": "fallback", "provider": "anthropic", "model": "c",
                          "used_fallback": True, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}])
    gateway = LLMGatewayV2(groq_adapter=groq, anthropic_adapter=anth)
    result = await gateway.complete(prompt="hello")
    assert result["content"] == "fallback"
    assert groq.calls == 3
    assert anth.calls == 1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_gateway_returns_static_when_all_providers_fail():
    groq = _FakeAdapter([LLMGatewayError("down")] * 3)
    anth = _FakeAdapter([LLMGatewayError("down")] * 3)
    gateway = LLMGatewayV2(groq_adapter=groq, anthropic_adapter=anth)
    result = await gateway.complete(prompt="hello")
    assert result["provider"] == _STATIC_FALLBACK_RESPONSE["provider"]
    assert result["used_fallback"] is True


@pytest.mark.unit
def test_from_settings_builds_adapters_when_keys_present():
    settings = MagicMock(GROQ_API_KEY="g", ANTHROPIC_API_KEY="a")
    gateway = LLMGatewayV2.from_settings(settings)
    assert len(gateway._providers) == 2
    assert gateway.circuit_breaker_states()["groq"] == "closed"


@pytest.mark.unit
def test_from_settings_skips_missing_keys():
    settings = MagicMock(GROQ_API_KEY=None, ANTHROPIC_API_KEY=None)
    gateway = LLMGatewayV2.from_settings(settings)
    assert gateway._providers == []


@pytest.mark.asyncio
@pytest.mark.unit
async def test_gateway_skips_open_circuit_provider():
    groq = _FakeAdapter([{"content": "x", "provider": "groq", "model": "m", "used_fallback": False,
                          "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}])
    gateway = LLMGatewayV2(groq_adapter=groq, anthropic_adapter=None)
    _, _, breaker = gateway._providers[0]
    for _ in range(3):
        breaker.record_failure()
    assert breaker.is_available() is False
    result = await gateway.complete(prompt="p")
    assert result["provider"] == "static"
    assert groq.calls == 0


@pytest.mark.unit
def test_log_token_usage_strips_prompt_fields():
    gateway = LLMGatewayV2(groq_adapter=None, anthropic_adapter=None)
    gateway._log_token_usage(
        {"provider": "groq", "model": "m", "prompt_tokens": 1, "completion_tokens": 2,
         "total_tokens": 3, "latency_ms": 10},
        metadata={"prompt": "secret", "learner_id": "l1"},
    )
    assert len(gateway._token_log) == 1
    assert "prompt" not in gateway._token_log[0].get("meta", {})
    assert gateway._token_log[0]["meta"]["learner_id"] == "l1"
