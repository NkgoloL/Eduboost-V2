"""tests/unit/test_llm_gateway.py
Unit tests for app.services.llm.gateway without any network calls.
"""
from __future__ import annotations


import pytest

from app.services.llm.gateway import (
    CanonicalLLMGateway,
    DeterministicMockProvider,
    DISABLE_LESSON_GENERATION_ENV,
    LLMGatewayRequest,
    LLMGatewayResponse,
    ProviderHealth,
    ProviderPolicy,
    ProviderResult,
    TokenUsage,
)


class _RaisingOnceProvider:
    provider_name = "raising_once"
    model_version = "v1"

    def __init__(self) -> None:
        self._raised = False

    def health(self) -> ProviderHealth:
        return ProviderHealth(self.provider_name, True, "ok")

    def complete(self, request: LLMGatewayRequest, timeout_seconds: float) -> ProviderResult:
        if not self._raised:
            self._raised = True
            raise RuntimeError("transient failure")
        return ProviderResult(
            content="{\"ok\":true}",
            provider_name=self.provider_name,
            model_version=self.model_version,
            token_usage=TokenUsage(prompt_tokens=3, completion_tokens=5),
            safety_status="safe",
        )


class _UnhealthyProvider:
    provider_name = "unhealthy"
    model_version = "v1"

    def health(self) -> ProviderHealth:
        return ProviderHealth(self.provider_name, False, "down")

    def complete(self, request: LLMGatewayRequest, timeout_seconds: float) -> ProviderResult:  # pragma: no cover
        raise AssertionError("should not be called when unhealthy")


@pytest.mark.unit
def test_token_usage_total_tokens():
    usage = TokenUsage(prompt_tokens=7, completion_tokens=11)
    assert usage.total_tokens == 18


@pytest.mark.unit
def test_provider_policy_defaults():
    policy = ProviderPolicy()
    assert policy.timeout_seconds == 20.0
    assert policy.max_retries == 1
    assert policy.circuit_breaker_failures == 3
    assert policy.daily_budget_tokens == 50_000


@pytest.mark.unit
def test_provider_health_fields():
    ph = ProviderHealth("x", True, "ok")
    assert ph.provider_name == "x"
    assert ph.healthy is True
    assert ph.reason == "ok"


@pytest.mark.unit
def test_llm_gateway_request_fields():
    req = LLMGatewayRequest(
        prompt="Say hi",
        pseudonym_id="pid-1",
        prompt_template_version="v1",
        input_schema="in",
        output_schema="out",
        safety_status="pending",
        metadata={"k": "v"},
    )
    assert req.prompt == "Say hi"
    assert req.metadata["k"] == "v"


@pytest.mark.unit
def test_canonical_llm_gateway_uses_primary_provider():
    provider = DeterministicMockProvider(content="hello world", healthy=True)
    gw = CanonicalLLMGateway([provider])
    req = LLMGatewayRequest(
        prompt="one two three",
        pseudonym_id="pid",
        prompt_template_version="p1",
        input_schema="i",
        output_schema="o",
    )
    resp = gw.complete(req)
    assert isinstance(resp, LLMGatewayResponse)
    assert resp.content == "hello world"
    assert resp.metadata.fallback_status in {"primary", "recovered_after_retry"}
    assert resp.metadata.provider_name == provider.provider_name
    assert resp.metadata.token_usage["total_tokens"] >= 2


@pytest.mark.unit
def test_canonical_llm_gateway_retries_then_succeeds():
    provider = _RaisingOnceProvider()
    gw = CanonicalLLMGateway([provider], policy=ProviderPolicy(max_retries=2))
    req = LLMGatewayRequest(
        prompt="short prompt",
        pseudonym_id="pid",
        prompt_template_version="p1",
        input_schema="i",
        output_schema="o",
    )
    resp = gw.complete(req)
    assert resp.metadata.retry_count >= 1
    assert resp.metadata.fallback_status in {"primary", "recovered_after_retry"}


@pytest.mark.unit
def test_canonical_llm_gateway_falls_back_when_no_providers():
    gw = CanonicalLLMGateway([], policy=ProviderPolicy())
    req = LLMGatewayRequest(
        prompt="x",
        pseudonym_id="pid",
        prompt_template_version="p1",
        input_schema="i",
        output_schema="o",
    )
    resp = gw.complete(req)
    assert resp.metadata.fallback_status == "development_fallback"


@pytest.mark.unit
def test_canonical_llm_gateway_skips_unhealthy_and_falls_back():
    gw = CanonicalLLMGateway([_UnhealthyProvider()])
    req = LLMGatewayRequest(
        prompt="x",
        pseudonym_id="pid",
        prompt_template_version="p1",
        input_schema="i",
        output_schema="o",
    )
    resp = gw.complete(req)
    assert resp.metadata.fallback_status == "development_fallback"


@pytest.mark.unit
def test_canonical_llm_gateway_respects_disable_env(monkeypatch):
    monkeypatch.setenv(DISABLE_LESSON_GENERATION_ENV, "true")
    gw = CanonicalLLMGateway([DeterministicMockProvider()])
    req = LLMGatewayRequest(
        prompt="x",
        pseudonym_id="pid",
        prompt_template_version="p1",
        input_schema="i",
        output_schema="o",
    )
    with pytest.raises(RuntimeError, match="lesson generation disabled"):
        gw.complete(req)
    monkeypatch.delenv(DISABLE_LESSON_GENERATION_ENV)
