"""Comprehensive unit tests for LLM provider error handling and telemetry dictionary serialization."""
from __future__ import annotations

import pytest

from app.services.llm_provider import (
    TokenUsage,
    GenerationResult,
    ProviderError,
    ProviderTimeoutError,
    ProviderRateLimitError,
    ProviderContentPolicyError,
    AllProvidersFailedError,
)


class TestLLMProviderDataModels:
    def test_token_usage_model(self):
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            estimated_cost_usd=0.0001,
        )
        assert usage.total_tokens == 150
        assert usage.estimated_cost_usd == 0.0001

    def test_generation_result_to_telemetry_dict(self):
        usage = TokenUsage(
            prompt_tokens=120,
            completion_tokens=60,
            total_tokens=180,
            estimated_cost_usd=0.0002,
        )
        res = GenerationResult(
            text="Private generated content with PII: Jane Doe",
            provider="groq",
            model="llama-3.3-70b-versatile",
            usage=usage,
            latency_ms=250.4,
            request_id="req-12345",
        )
        telem = res.to_telemetry_dict()

        # Content must NOT be leaked into telemetry
        assert "text" not in telem
        assert "Jane Doe" not in str(telem)

        # Necessary telemetry fields must exist
        assert telem["provider"] == "groq"
        assert telem["model"] == "llama-3.3-70b-versatile"
        assert telem["prompt_tokens"] == 120
        assert telem["completion_tokens"] == 60
        assert telem["total_tokens"] == 180
        assert telem["latency_ms"] == 250.4
        assert telem["request_id"] == "req-12345"


class TestLLMProviderExceptions:
    def test_provider_error_attributes(self):
        err = ProviderError("Temporary failure", provider="anthropic", retryable=True)
        assert err.provider == "anthropic"
        assert err.retryable is True

    def test_provider_timeout_error(self):
        err = ProviderTimeoutError("Request timed out", provider="groq")
        assert err.provider == "groq"
        assert issubclass(ProviderTimeoutError, ProviderError)

    def test_provider_rate_limit_error(self):
        err = ProviderRateLimitError("Rate limit 429", provider="groq")
        assert err.provider == "groq"
        assert issubclass(ProviderRateLimitError, ProviderError)

    def test_provider_content_policy_error(self):
        err = ProviderContentPolicyError("Blocked by safety policy", provider="anthropic")
        assert err.provider == "anthropic"
        assert err.retryable is False
        assert issubclass(ProviderContentPolicyError, ProviderError)

    def test_all_providers_failed_error(self):
        err = AllProvidersFailedError("All providers in chain failed")
        assert "All providers" in str(err)
