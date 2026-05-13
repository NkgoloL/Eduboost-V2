"""Canonical, dependency-light LLM gateway contract.

This module deliberately avoids network SDK imports. Production adapters can wrap
external providers, while tests and development use ``DeterministicMockProvider``.
The gateway records the metadata required by the production-readiness backlog:
provider, model/version, prompt template, input/output schemas, latency, token
usage, safety status, fallback status, retry/timeout policy, health, and budget.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

DISABLE_LESSON_GENERATION_ENV = "DISABLE_LESSON_GENERATION"


@dataclass(frozen=True, slots=True)
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass(frozen=True, slots=True)
class ProviderPolicy:
    timeout_seconds: float = 20.0
    max_retries: int = 1
    circuit_breaker_failures: int = 3
    daily_budget_tokens: int = 50_000


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    provider_name: str
    healthy: bool
    reason: str = "ok"


@dataclass(frozen=True, slots=True)
class LLMGatewayRequest:
    prompt: str
    pseudonym_id: str
    prompt_template_version: str
    input_schema: str
    output_schema: str
    safety_status: str = "pending"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProviderResult:
    content: str
    provider_name: str
    model_version: str
    token_usage: TokenUsage
    safety_status: str = "safe"


@dataclass(frozen=True, slots=True)
class LLMGatewayMetadata:
    provider_name: str
    model_version: str
    prompt_template_version: str
    input_schema: str
    output_schema: str
    latency_ms: int
    token_usage: dict[str, int]
    safety_status: str
    fallback_status: str
    timeout_seconds: float
    retry_count: int
    circuit_breaker_status: str
    budget_status: str


@dataclass(frozen=True, slots=True)
class LLMGatewayResponse:
    content: str
    metadata: LLMGatewayMetadata


class LLMProvider(Protocol):
    provider_name: str
    model_version: str

    def health(self) -> ProviderHealth: ...

    def complete(self, request: LLMGatewayRequest, timeout_seconds: float) -> ProviderResult: ...


class DeterministicMockProvider:
    """Offline provider for deterministic development and CI tests."""

    provider_name = "deterministic_mock"
    model_version = "mock-lesson-v1"

    def __init__(self, content: str | None = None, healthy: bool = True) -> None:
        self._content = content or '{"topic":"Fractions","safety_classification":"safe"}'
        self._healthy = healthy

    def health(self) -> ProviderHealth:
        return ProviderHealth(self.provider_name, self._healthy, "ok" if self._healthy else "forced unhealthy")

    def complete(self, request: LLMGatewayRequest, timeout_seconds: float) -> ProviderResult:
        if not self._healthy:
            raise RuntimeError("deterministic provider unavailable")
        prompt_tokens = max(1, len(request.prompt.split()))
        completion_tokens = max(1, len(self._content.split()))
        return ProviderResult(
            content=self._content,
            provider_name=self.provider_name,
            model_version=self.model_version,
            token_usage=TokenUsage(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens),
            safety_status="safe",
        )


class CanonicalLLMGateway:
    """Provider-agnostic gateway with fallback, timeout, retry, and budget metadata."""

    def __init__(
        self,
        providers: list[LLMProvider],
        *,
        policy: ProviderPolicy | None = None,
        development_fallback: LLMProvider | None = None,
    ) -> None:
        self.providers = providers
        self.policy = policy or ProviderPolicy()
        self.development_fallback = development_fallback or DeterministicMockProvider()

    def health_checks(self) -> list[ProviderHealth]:
        return [provider.health() for provider in self.providers]

    def complete(self, request: LLMGatewayRequest) -> LLMGatewayResponse:
        if os.getenv(DISABLE_LESSON_GENERATION_ENV, "").lower() in {"1", "true", "yes", "on"}:
            raise RuntimeError("lesson generation disabled by DISABLE_LESSON_GENERATION")

        started = time.perf_counter()
        providers: list[tuple[LLMProvider, str]] = [(provider, "primary") for provider in self.providers]
        if not providers:
            providers.append((self.development_fallback, "development_fallback"))

        failures: list[str] = []
        retry_count = 0
        for index, (provider, fallback_status) in enumerate(providers):
            health = provider.health()
            if not health.healthy:
                failures.append(f"{provider.provider_name}:{health.reason}")
                continue
            for _attempt in range(self.policy.max_retries + 1):
                try:
                    result = provider.complete(request, timeout_seconds=self.policy.timeout_seconds)
                    latency_ms = int((time.perf_counter() - started) * 1000)
                    fallback = fallback_status if index == 0 else "provider_fallback"
                    if failures and fallback == "primary":
                        fallback = "recovered_after_retry"
                    return LLMGatewayResponse(
                        content=result.content,
                        metadata=LLMGatewayMetadata(
                            provider_name=result.provider_name,
                            model_version=result.model_version,
                            prompt_template_version=request.prompt_template_version,
                            input_schema=request.input_schema,
                            output_schema=request.output_schema,
                            latency_ms=latency_ms,
                            token_usage={
                                "prompt_tokens": result.token_usage.prompt_tokens,
                                "completion_tokens": result.token_usage.completion_tokens,
                                "total_tokens": result.token_usage.total_tokens,
                            },
                            safety_status=result.safety_status,
                            fallback_status=fallback,
                            timeout_seconds=self.policy.timeout_seconds,
                            retry_count=retry_count,
                            circuit_breaker_status="closed",
                            budget_status="within_budget" if result.token_usage.total_tokens <= self.policy.daily_budget_tokens else "over_budget",
                        ),
                    )
                except Exception as exc:  # pragma: no cover - specific adapters vary
                    failures.append(f"{provider.provider_name}:{exc}")
                    retry_count += 1
                    continue

        fallback = self.development_fallback.complete(request, timeout_seconds=self.policy.timeout_seconds)
        latency_ms = int((time.perf_counter() - started) * 1000)
        return LLMGatewayResponse(
            content=fallback.content,
            metadata=LLMGatewayMetadata(
                provider_name=fallback.provider_name,
                model_version=fallback.model_version,
                prompt_template_version=request.prompt_template_version,
                input_schema=request.input_schema,
                output_schema=request.output_schema,
                latency_ms=latency_ms,
                token_usage={
                    "prompt_tokens": fallback.token_usage.prompt_tokens,
                    "completion_tokens": fallback.token_usage.completion_tokens,
                    "total_tokens": fallback.token_usage.total_tokens,
                },
                safety_status=fallback.safety_status,
                fallback_status="development_fallback",
                timeout_seconds=self.policy.timeout_seconds,
                retry_count=retry_count,
                circuit_breaker_status="open" if failures else "closed",
                budget_status="within_budget",
            ),
        )
