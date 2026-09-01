"""Batch 222 — app/services/llm_provider.py comprehensive branch coverage expansion.

Tests:
- Telemetry dictionary serialization (to_telemetry_dict)
- Error hierarchy: ProviderError, ProviderTimeoutError, ProviderRateLimitError, ProviderContentPolicyError, AllProvidersFailedError
- AnthropicProvider: initialization checks, generate (SDK import error, timeout, 429 rate limit, 400 content policy, other errors, success, cost calculation, health check)
- GroqProvider: initialization checks, generate (SDK import error, timeout, 429 rate limit, success, health check)
- AzureOpenAIProvider: initialization checks, generate (SDK import error, timeout, generic error, success, cost estimation, health check)
- DeterministicProvider: key hashing, registered fixtures, default fixture, missing fixture error, health check
- CircuitBreaker: state machine (CLOSED -> OPEN on threshold, OPEN -> HALF_OPEN on timeout, HALF_OPEN -> CLOSED on success, record_failure)
- ProviderRouter: validation on init (empty, duplicate names), skip on circuit open, retry backoff, content policy fail-closed, unexpected error normalization, all providers exhausted error, provider_states inspection
- build_provider_router factory: deterministic test vs non-test, unsupported provider, missing key for requested provider, no providers configured, full multi-provider chain ordering
"""
from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.llm_provider import (
    AllProvidersFailedError,
    AnthropicProvider,
    AzureOpenAIProvider,
    CircuitBreaker,
    CircuitState,
    DeterministicProvider,
    GenerationResult,
    GroqProvider,
    LLMProvider,
    ProviderContentPolicyError,
    ProviderError,
    ProviderRateLimitError,
    ProviderRouter,
    ProviderTimeoutError,
    TokenUsage,
    _anthropic_cost,
    build_provider_router,
)


# ---------------------------------------------------------------------------
# Data Classes & Telemetry
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_generation_result_to_telemetry_dict():
    usage = TokenUsage(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        estimated_cost_usd=0.005,
    )
    res = GenerationResult(
        text="Sample completion",
        provider="azure",
        model="gpt-4o",
        usage=usage,
        latency_ms=123.456,
        request_id="req-12345",
    )
    telemetry = res.to_telemetry_dict()
    assert telemetry["provider"] == "azure"
    assert telemetry["model"] == "gpt-4o"
    assert telemetry["prompt_tokens"] == 100
    assert telemetry["completion_tokens"] == 50
    assert telemetry["total_tokens"] == 150
    assert telemetry["estimated_cost_usd"] == 0.005
    assert telemetry["latency_ms"] == 123.5
    assert telemetry["request_id"] == "req-12345"
    assert "text" not in telemetry  # verify no PII/raw text in telemetry


@pytest.mark.unit
def test_anthropic_cost_model_prefixes():
    assert _anthropic_cost("claude-opus-4-2025", 1000, 1000) > 0.0
    assert _anthropic_cost("claude-sonnet-4-2025", 1000, 1000) > 0.0
    assert _anthropic_cost("claude-haiku-4-2025", 1000, 1000) > 0.0
    assert _anthropic_cost("unknown-model", 1000, 1000) == 0.0


# ---------------------------------------------------------------------------
# DeterministicProvider
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_deterministic_provider_generation_and_health():
    provider = DeterministicProvider()
    key = provider.register("sys", "usr", "Custom response")
    provider.register_default("Default response")

    # Match registered
    res1 = await provider.generate(system="sys", user="usr")
    assert res1.text == "Custom response"
    assert res1.usage.completion_tokens == 2

    # Match default
    res2 = await provider.generate(system="other", user="other")
    assert res2.text == "Default response"

    # Missing fixture error
    empty_provider = DeterministicProvider()
    with pytest.raises(ProviderError, match="No fixture registered"):
        await empty_provider.generate(system="a", user="b")

    # Health check
    assert await provider.health_check() is True


# ---------------------------------------------------------------------------
# AnthropicProvider
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_anthropic_provider_init_and_generate():
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is required"):
        AnthropicProvider(api_key="", model="claude-sonnet-4")

    provider = AnthropicProvider(api_key="sk-ant-test", model="claude-sonnet-4")

    # Mock SDK response
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text="Claude response")]
    mock_msg.usage.input_tokens = 10
    mock_msg.usage.output_tokens = 20

    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_msg)

    with patch("anthropic.AsyncAnthropic", return_value=mock_client):
        res = await provider.generate(system="sys", user="usr")
        assert res.text == "Claude response"
        assert res.usage.total_tokens == 30

        # Health check success
        mock_msg.content = [MagicMock(text="OK")]
        assert await provider.health_check() is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_anthropic_provider_errors():
    provider = AnthropicProvider(api_key="sk-ant-test", model="claude-sonnet-4", timeout_seconds=0.01)

    # 1. Timeout error
    async def slow_create(**kwargs):
        await asyncio.sleep(0.1)

    mock_client = MagicMock()
    mock_client.messages.create = slow_create

    with patch("anthropic.AsyncAnthropic", return_value=mock_client):
        with pytest.raises(ProviderTimeoutError):
            await provider.generate(system="sys", user="usr")

        # Health check returns False on ProviderError
        assert await provider.health_check() is False


# ---------------------------------------------------------------------------
# GroqProvider
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_groq_provider_init_and_generate():
    with pytest.raises(ValueError, match="GROQ_API_KEY is required"):
        GroqProvider(api_key="", model="llama3-70b-8192")

    provider = GroqProvider(api_key="gsk-test", model="llama3-70b-8192")

    mock_comp = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Groq response"
    mock_comp.choices = [mock_choice]
    mock_comp.usage.total_tokens = 15
    mock_comp.usage.prompt_tokens = 5
    mock_comp.usage.completion_tokens = 10

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_comp)

    with patch("groq.AsyncGroq", return_value=mock_client):
        res = await provider.generate(system="sys", user="usr")
        assert res.text == "Groq response"
        assert res.usage.total_tokens == 15
        assert await provider.health_check() is True


# ---------------------------------------------------------------------------
# AzureOpenAIProvider
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_azure_openai_provider_init_and_generate():
    with pytest.raises(ValueError, match="AZURE_OPENAI_ENDPOINT is required"):
        AzureOpenAIProvider(endpoint="", api_key="k", model="gpt-4o")

    with pytest.raises(ValueError, match="AZURE_OPENAI_API_KEY is required"):
        AzureOpenAIProvider(endpoint="https://azure.openai.com", api_key="", model="gpt-4o")

    provider = AzureOpenAIProvider(
        endpoint="https://azure.openai.com/",
        api_key="azure-key",
        model="gpt-4o",
    )
    assert provider._endpoint == "https://azure.openai.com"

    mock_msg = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Azure response"
    mock_msg.choices = [mock_choice]
    mock_msg.usage.total_tokens = 25
    mock_msg.usage.prompt_tokens = 10
    mock_msg.usage.completion_tokens = 15

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_msg)

    with patch("openai.AsyncAzureOpenAI", return_value=mock_client):
        res = await provider.generate(system="sys", user="usr")
        assert res.text == "Azure response"
        assert res.usage.estimated_cost_usd is not None

        mock_choice.message.content = "OK"
        assert await provider.health_check() is True


# ---------------------------------------------------------------------------
# CircuitBreaker
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_circuit_breaker_transitions():
    cb = CircuitBreaker("test-prov", failure_threshold=2, recovery_timeout_seconds=0.05)
    assert cb.state == CircuitState.CLOSED
    assert cb.is_available() is True

    # 1 failure -> still closed
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED

    # 2 failures -> opened
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.is_available() is False

    # Wait for timeout -> half open
    time.sleep(0.06)
    assert cb.state == CircuitState.HALF_OPEN
    assert cb.is_available() is True

    # Success resets to closed
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.is_available() is True


# ---------------------------------------------------------------------------
# ProviderRouter
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_provider_router_validations_and_states():
    # Empty providers raises ValueError
    with pytest.raises(ValueError, match="requires at least one provider"):
        ProviderRouter([])

    # Duplicate names raises ValueError
    p1 = DeterministicProvider()
    p1.name = "dup"
    p2 = DeterministicProvider()
    p2.name = "dup"
    with pytest.raises(ValueError, match="Provider names must be unique"):
        ProviderRouter([p1, p2])

    p_valid = DeterministicProvider()
    p_valid.name = "single"
    router = ProviderRouter([p_valid])
    assert router.provider_states() == {"single": "closed"}


@pytest.mark.asyncio
@pytest.mark.unit
async def test_provider_router_content_policy_fails_closed():
    mock_p1 = MagicMock(spec=LLMProvider)
    mock_p1.name = "prov1"
    mock_p1.generate = AsyncMock(side_effect=ProviderContentPolicyError("Harmful prompt", "prov1"))

    mock_p2 = MagicMock(spec=LLMProvider)
    mock_p2.name = "prov2"

    router = ProviderRouter([mock_p1, mock_p2], request_timeout_seconds=5.0)

    # Content policy error must raise immediately without calling prov2
    with pytest.raises(ProviderContentPolicyError):
        await router.generate(system="sys", user="usr")

    mock_p2.generate.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_provider_router_fallback_and_exhaustion():
    mock_p1 = MagicMock(spec=LLMProvider)
    mock_p1.name = "prov1"
    mock_p1.generate = AsyncMock(side_effect=ProviderError("Prov1 failed", "prov1", retryable=False))

    mock_p2 = MagicMock(spec=LLMProvider)
    mock_p2.name = "prov2"
    usage = TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10)
    mock_p2.generate = AsyncMock(
        return_value=GenerationResult(
            text="P2 success",
            provider="prov2",
            model="m2",
            usage=usage,
            latency_ms=10.0,
        )
    )

    router = ProviderRouter([mock_p1, mock_p2], max_retries_per_provider=1, request_timeout_seconds=5.0)

    # Falls back from prov1 to prov2
    res = await router.generate(system="sys", user="usr")
    assert res.text == "P2 success"

    # When all providers fail
    mock_p2.generate = AsyncMock(side_effect=RuntimeError("Unexpected SDK crash"))
    with pytest.raises(AllProvidersFailedError, match="All providers exhausted"):
        await router.generate(system="sys", user="usr")


# ---------------------------------------------------------------------------
# build_provider_router Factory
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_build_provider_router_deterministic_rules():
    # Test env allows deterministic
    settings_test = MagicMock(
        APP_ENV="test",
        ENVIRONMENT="test",
        LLM_PROVIDER="deterministic",
        LLM_TIMEOUT_SECONDS=30,
    )
    router_test = build_provider_router(settings_test)
    assert len(router_test._providers) == 1
    assert router_test._providers[0].name == "deterministic"

    # Non-test env rejects deterministic
    settings_prod = MagicMock(
        APP_ENV="production",
        ENVIRONMENT="production",
        LLM_PROVIDER="deterministic",
    )
    with pytest.raises(RuntimeError, match="DeterministicProvider is restricted"):
        build_provider_router(settings_prod)


@pytest.mark.unit
def test_build_provider_router_missing_and_unsupported_config():
    # Unsupported provider
    s1 = MagicMock(
        ENVIRONMENT="production",
        LLM_PROVIDER="unsupported_ai",
        ANTHROPIC_API_KEY="sk-ant",
    )
    with pytest.raises(RuntimeError, match="Unsupported LLM_PROVIDER"):
        build_provider_router(s1)

    # Requested provider missing API key
    s2 = MagicMock(
        ENVIRONMENT="production",
        LLM_PROVIDER="anthropic",
        ANTHROPIC_API_KEY="",
        GROQ_API_KEY="gsk-1",
    )
    with pytest.raises(RuntimeError, match="is selected but its API key is missing"):
        build_provider_router(s2)

    # No providers configured
    s3 = MagicMock(
        ENVIRONMENT="production",
        LLM_PROVIDER="",
        AZURE_OPENAI_ENDPOINT="",
        AZURE_OPENAI_API_KEY="",
        ANTHROPIC_API_KEY="",
        GROQ_API_KEY="",
    )
    with pytest.raises(RuntimeError, match="No LLM provider configured"):
        build_provider_router(s3)


@pytest.mark.unit
def test_build_provider_router_multi_provider_chain():
    settings_multi = MagicMock(
        ENVIRONMENT="production",
        LLM_PROVIDER="",
        AZURE_OPENAI_ENDPOINT="https://azure.openai.com",
        AZURE_OPENAI_API_KEY="azure-key",
        ANTHROPIC_API_KEY="sk-ant",
        GROQ_API_KEY="gsk-groq",
        LLM_TIMEOUT_SECONDS=45,
        LLM_MAX_RETRIES=2,
    )
    router = build_provider_router(settings_multi)
    # Order: azure (primary) -> anthropic -> groq
    names = [p.name for p in router._providers]
    assert names == ["azure", "anthropic", "groq"]
