"""
Phase 1 — EC-04: Provider fallback and timeout behaviour tests.
"""
from __future__ import annotations


import pytest

from app.services.llm_provider import (
    AllProvidersFailedError,
    CircuitBreaker,
    CircuitState,
    DeterministicProvider,
    ProviderContentPolicyError,
    ProviderError,
    ProviderRouter,
    build_provider_router,
)


# ---------------------------------------------------------------------------
# DeterministicProvider
# ---------------------------------------------------------------------------


class TestDeterministicProvider:
    @pytest.mark.asyncio
    async def test_returns_registered_fixture(self):
        p = DeterministicProvider()
        p.register("sys", "usr", "hello world")
        result = await p.generate(system="sys", user="usr")
        assert result.text == "hello world"
        assert result.provider == "deterministic"

    @pytest.mark.asyncio
    async def test_default_fixture_used_when_no_match(self):
        p = DeterministicProvider()
        p.register_default("default response")
        result = await p.generate(system="any", user="thing")
        assert result.text == "default response"

    @pytest.mark.asyncio
    async def test_raises_when_no_fixture_and_no_default(self):
        p = DeterministicProvider()
        with pytest.raises(ProviderError, match="No fixture registered"):
            await p.generate(system="s", user="u")

    @pytest.mark.asyncio
    async def test_health_check_always_true(self):
        p = DeterministicProvider()
        assert await p.health_check() is True

    @pytest.mark.asyncio
    async def test_zero_cost(self):
        p = DeterministicProvider()
        p.register_default("result")
        result = await p.generate(system="s", user="u")
        assert result.usage.estimated_cost_usd == 0.0

    @pytest.mark.asyncio
    async def test_token_count_proportional_to_word_count(self):
        p = DeterministicProvider()
        p.register_default("one two three four five")
        result = await p.generate(system="s", user="u")
        assert result.usage.total_tokens == 5


# ---------------------------------------------------------------------------
# CircuitBreaker
# ---------------------------------------------------------------------------


class TestCircuitBreaker:
    def test_initially_closed(self):
        cb = CircuitBreaker("test", failure_threshold=3)
        assert cb.state == CircuitState.CLOSED
        assert cb.is_available() is True

    def test_opens_after_threshold(self):
        cb = CircuitBreaker("test", failure_threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.is_available() is False

    def test_closes_on_success(self):
        cb = CircuitBreaker("test", failure_threshold=2)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.is_available() is True

    def test_half_opens_after_recovery_timeout(self):
        cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout_seconds=0.001)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        import time
        time.sleep(0.002)
        assert cb.state == CircuitState.HALF_OPEN
        assert cb.is_available() is True

    def test_does_not_open_below_threshold(self):
        cb = CircuitBreaker("test", failure_threshold=5)
        for _ in range(4):
            cb.record_failure()
        assert cb.state == CircuitState.CLOSED

    def test_failure_count_resets_after_success(self):
        cb = CircuitBreaker("test", failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        # Should need 3 more failures to open again
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED


# ---------------------------------------------------------------------------
# ProviderRouter
# ---------------------------------------------------------------------------


class TestProviderRouter:
    @pytest.mark.asyncio
    async def test_primary_provider_used_on_success(self, det_provider):
        det_provider.register_default("primary response")
        router = ProviderRouter([det_provider])
        result = await router.generate(system="s", user="u")
        assert result.text == "primary response"
        assert result.provider == "deterministic"

    @pytest.mark.asyncio
    async def test_fallback_used_when_primary_fails(self):
        failing = DeterministicProvider()
        # No fixture → raises ProviderError
        fallback = DeterministicProvider()
        fallback.name = "deterministic_fallback"
        fallback.register_default("fallback response")

        router = ProviderRouter([failing, fallback], max_retries_per_provider=1)
        result = await router.generate(system="s", user="u")
        assert result.text == "fallback response"

    @pytest.mark.asyncio
    async def test_raises_all_providers_failed_when_both_fail(self):
        p1 = DeterministicProvider()
        p2 = DeterministicProvider()
        p2.name = "deterministic_fallback"
        router = ProviderRouter([p1, p2], max_retries_per_provider=1)
        with pytest.raises(AllProvidersFailedError):
            await router.generate(system="s", user="u")

    @pytest.mark.asyncio
    async def test_content_policy_error_not_retried(self):
        """ProviderContentPolicyError must propagate immediately without retrying."""
        call_count = 0

        class PolicyRefusingProvider(DeterministicProvider):
            async def generate(self, *, system, user, **kw):
                nonlocal call_count
                call_count += 1
                raise ProviderContentPolicyError("policy", provider="test")

        p = PolicyRefusingProvider()
        router = ProviderRouter([p], max_retries_per_provider=3)
        with pytest.raises(ProviderContentPolicyError):
            await router.generate(system="s", user="u")
        # Must not retry; exactly one call
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_skips_open_provider(self):
        """When circuit is open, provider must be skipped and fallback used."""
        p1 = DeterministicProvider()  # will have open circuit
        p2 = DeterministicProvider()
        p2.name = "deterministic_fallback"
        p2.register_default("from_fallback")

        router = ProviderRouter([p1, p2], max_retries_per_provider=1, cb_failure_threshold=1)
        router._breakers["deterministic"].record_failure()

        result = await router.generate(system="s", user="u")
        assert result.text == "from_fallback"

    def test_provider_states_returns_all_providers(self, det_provider):
        router = ProviderRouter([det_provider])
        states = router.provider_states()
        assert "deterministic" in states
        assert states["deterministic"] == "closed"

    def test_requires_at_least_one_provider(self):
        with pytest.raises(ValueError, match="at least one provider"):
            ProviderRouter([])


# ---------------------------------------------------------------------------
# build_provider_router
# ---------------------------------------------------------------------------


class TestBuildProviderRouter:
    def test_test_environment_returns_deterministic(self):
        class FakeSettings:
            ENVIRONMENT = "test"
            LLM_PROVIDER = ""
            ANTHROPIC_API_KEY = ""
            GROQ_API_KEY = ""

        router = build_provider_router(FakeSettings())
        assert any(p.name == "deterministic" for p in router._providers)

    def test_deterministic_provider_blocked_in_production(self):
        class FakeSettings:
            ENVIRONMENT = "production"
            LLM_PROVIDER = "deterministic"
            ANTHROPIC_API_KEY = ""
            GROQ_API_KEY = ""

        with pytest.raises(RuntimeError, match="restricted to.*test"):
            build_provider_router(FakeSettings())

    def test_no_key_in_development_fails_closed(self):
        class FakeSettings:
            ENVIRONMENT = "development"
            LLM_PROVIDER = ""
            ANTHROPIC_API_KEY = ""
            GROQ_API_KEY = ""
            ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
            GROQ_MODEL = "llama3-70b-8192"

        with pytest.raises(RuntimeError, match="No LLM provider configured"):
            build_provider_router(FakeSettings())

    def test_production_with_no_provider_raises(self):
        class FakeSettings:
            ENVIRONMENT = "production"
            LLM_PROVIDER = ""
            ANTHROPIC_API_KEY = ""
            GROQ_API_KEY = ""

        with pytest.raises(RuntimeError, match="No LLM provider configured"):
            build_provider_router(FakeSettings())
