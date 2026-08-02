"""
Unit tests for app.services.llm_provider module.
Covers TokenUsage, GenerationResult telemetry, exceptions,
AnthropicProvider error paths/initialization, and helper cost functions.
"""
from __future__ import annotations

import pytest

from app.services.llm_provider import (
    AllProvidersFailedError,
    AnthropicProvider,
    CircuitBreaker,
    DeterministicProvider,
    GenerationResult,
    ProviderContentPolicyError,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    TokenUsage,
    _anthropic_cost,
)


class TestDataStructures:
    def test_token_usage_init(self):
        u = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30, estimated_cost_usd=0.001)
        assert u.prompt_tokens == 10
        assert u.completion_tokens == 20
        assert u.total_tokens == 30
        assert u.estimated_cost_usd == 0.001

    def test_generation_result_telemetry(self):
        u = TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10, estimated_cost_usd=0.0005)
        res = GenerationResult(
            text="Hello world",
            provider="test-provider",
            model="test-model",
            usage=u,
            latency_ms=12.345,
            request_id="req-123",
        )
        telemetry = res.to_telemetry_dict()
        assert telemetry["provider"] == "test-provider"
        assert telemetry["model"] == "test-model"
        assert telemetry["prompt_tokens"] == 5
        assert telemetry["completion_tokens"] == 5
        assert telemetry["total_tokens"] == 10
        assert telemetry["estimated_cost_usd"] == 0.0005
        assert telemetry["latency_ms"] == 12.3
        assert telemetry["request_id"] == "req-123"
        # Ensure raw text is not in telemetry
        assert "text" not in telemetry


class TestExceptions:
    def test_provider_error_defaults(self):
        err = ProviderError("fail", provider="test_p")
        assert str(err) == "fail"
        assert err.provider == "test_p"
        assert err.retryable is True

    def test_provider_content_policy_error(self):
        err = ProviderContentPolicyError("unsafe", provider="test_p")
        assert err.retryable is False
        assert isinstance(err, ProviderError)

    def test_provider_timeout_error(self):
        err = ProviderTimeoutError("timeout", provider="test_p")
        assert isinstance(err, ProviderError)

    def test_provider_rate_limit_error(self):
        err = ProviderRateLimitError("rate limit", provider="test_p")
        assert isinstance(err, ProviderError)

    def test_all_providers_failed_error(self):
        err = AllProvidersFailedError("All failed")
        assert str(err) == "All failed"


class TestAnthropicProvider:
    def test_init_raises_without_api_key(self):
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is required"):
            AnthropicProvider(api_key="", model="claude-3")

    def test_init_valid(self):
        p = AnthropicProvider(api_key="sk-test", model="claude-3-5-sonnet")
        assert p.name == "anthropic"
        assert p._model == "claude-3-5-sonnet"


class TestCostHelper:
    def test_anthropic_cost_calculation(self):
        cost = _anthropic_cost("claude-sonnet-4-20250101", prompt_tokens=1000, completion_tokens=1000)
        assert isinstance(cost, float)
        assert cost > 0.0

    def test_anthropic_cost_unknown_model_returns_zero(self):
        assert _anthropic_cost("unknown-model", prompt_tokens=1000, completion_tokens=1000) == 0.0


class TestDeterministicProvider:
    @pytest.mark.asyncio
    async def test_generate_with_fixture(self):
        p = DeterministicProvider()
        p.register("sys", "user", "fixed answer")
        res = await p.generate(system="sys", user="user")
        assert res.text == "fixed answer"
        assert res.provider == "deterministic"

    @pytest.mark.asyncio
    async def test_generate_default(self):
        p = DeterministicProvider()
        p.register_default("default answer")
        res = await p.generate(system="any", user="any")
        assert res.text == "default answer"

    @pytest.mark.asyncio
    async def test_generate_missing_fixture_raises(self):
        p = DeterministicProvider()
        with pytest.raises(ProviderError, match="No fixture registered"):
            await p.generate(system="unregistered", user="unregistered")

    @pytest.mark.asyncio
    async def test_health_check(self):
        p = DeterministicProvider()
        assert await p.health_check() is True


class TestCircuitBreaker:
    def test_initial_state_closed(self):
        cb = CircuitBreaker("p1", failure_threshold=2)
        assert cb.state.value == "closed"
        assert cb.is_available() is True

    def test_opens_after_failures(self):
        cb = CircuitBreaker("p1", failure_threshold=2)
        cb.record_failure()
        assert cb.state.value == "closed"
        cb.record_failure()
        assert cb.state.value == "open"
        assert cb.is_available() is False

    def test_record_success_resets_failures(self):
        cb = CircuitBreaker("p1", failure_threshold=2)
        cb.record_failure()
        cb.record_success()
        assert cb.state.value == "closed"
        assert cb._failures == 0


class TestProviderRouter:
    def test_init_validation(self):
        with pytest.raises(ValueError, match="at least one provider"):
            from app.services.llm_provider import ProviderRouter
            ProviderRouter([])

        with pytest.raises(ValueError, match="names must be unique"):
            from app.services.llm_provider import ProviderRouter
            p1 = DeterministicProvider()
            p2 = DeterministicProvider()
            ProviderRouter([p1, p2])

    @pytest.mark.asyncio
    async def test_successful_route(self):
        from app.services.llm_provider import ProviderRouter
        p = DeterministicProvider()
        p.register_default("ok")
        router = ProviderRouter([p])
        res = await router.generate(system="s", user="u")
        assert res.text == "ok"
