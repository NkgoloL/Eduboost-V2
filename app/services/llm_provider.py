"""
EduBoost Phase 1 — LLM Provider Abstraction
============================================
Canonical provider interface, concrete implementations, circuit breaker,
and ProviderRouter.  All generation goes through this module.

Phase 1 exit criteria addressed here:
  - Provider fallback and timeout behaviour (EC-04)
  - Deterministic CI provider for reproducible test runs (EC-07)
  - Cost and token telemetry without personal-data leakage (EC-06)
  - Fail-closed on provider error; no silent fallback to unsafe state (GP-06)
"""
from __future__ import annotations

import asyncio
import enum
import hashlib
import structlog
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Result and error types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float | None = None


@dataclass(frozen=True)
class GenerationResult:
    text: str
    provider: str
    model: str
    usage: TokenUsage
    latency_ms: float
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_telemetry_dict(self) -> dict[str, Any]:
        """Return a telemetry-safe dict — no personal data, no raw content."""
        return {
            "provider": self.provider,
            "model": self.model,
            "prompt_tokens": self.usage.prompt_tokens,
            "completion_tokens": self.usage.completion_tokens,
            "total_tokens": self.usage.total_tokens,
            "estimated_cost_usd": self.usage.estimated_cost_usd,
            "latency_ms": round(self.latency_ms, 1),
            "request_id": self.request_id,
        }


class ProviderError(Exception):
    """Base for all provider errors."""

    def __init__(self, message: str, provider: str, retryable: bool = True):
        super().__init__(message)
        self.provider = provider
        self.retryable = retryable


class ProviderTimeoutError(ProviderError):
    pass


class ProviderRateLimitError(ProviderError):
    pass


class ProviderContentPolicyError(ProviderError):
    """Raised when the provider refuses generation on policy grounds."""

    def __init__(self, message: str, provider: str):
        super().__init__(message, provider, retryable=False)


class AllProvidersFailedError(Exception):
    """Raised by ProviderRouter when every provider in the chain has failed."""


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------


class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def generate(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        """Generate a completion.  Raises ProviderError on failure."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Returns True when the provider is reachable."""


# ---------------------------------------------------------------------------
# Anthropic implementation
# ---------------------------------------------------------------------------


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str, model: str, timeout_seconds: float = 60.0):
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for AnthropicProvider")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout_seconds

    async def generate(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        try:
            import anthropic as sdk
        except ImportError as exc:
            raise ProviderError(
                "anthropic SDK not installed", self.name, retryable=False
            ) from exc

        client = sdk.AsyncAnthropic(api_key=self._api_key)
        t0 = time.monotonic()
        try:
            async with asyncio.timeout(self._timeout):
                msg = await client.messages.create(
                    model=self._model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
        except TimeoutError as exc:
            raise ProviderTimeoutError(
                f"Anthropic timed out after {self._timeout}s", self.name
            ) from exc
        except sdk.APIStatusError as exc:
            if exc.status_code == 429:
                raise ProviderRateLimitError(str(exc), self.name) from exc
            if exc.status_code == 400 and "content policy" in str(exc).lower():
                raise ProviderContentPolicyError(str(exc), self.name) from exc
            raise ProviderError(str(exc), self.name) from exc
        except Exception as exc:
            raise ProviderError(f"Anthropic request failed: {exc}", self.name) from exc

        latency_ms = (time.monotonic() - t0) * 1000
        text = msg.content[0].text if msg.content else ""
        usage = TokenUsage(
            prompt_tokens=msg.usage.input_tokens,
            completion_tokens=msg.usage.output_tokens,
            total_tokens=msg.usage.input_tokens + msg.usage.output_tokens,
            estimated_cost_usd=_anthropic_cost(
                self._model, msg.usage.input_tokens, msg.usage.output_tokens
            ),
        )
        return GenerationResult(
            text=text,
            provider=self.name,
            model=self._model,
            usage=usage,
            latency_ms=latency_ms,
        )

    async def health_check(self) -> bool:
        try:
            result = await self.generate(
                system="You are a health-check probe.",
                user="Reply with the single word OK.",
                max_tokens=10,
            )
            return "ok" in result.text.lower()
        except ProviderError:
            return False


def _anthropic_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Approximate cost in USD.  Rates as of 2025-Q3; update as pricing changes."""
    rates: dict[str, tuple[float, float]] = {
        "claude-opus-4": (15.0 / 1e6, 75.0 / 1e6),
        "claude-sonnet-4": (3.0 / 1e6, 15.0 / 1e6),
        "claude-haiku-4": (0.25 / 1e6, 1.25 / 1e6),
    }
    for prefix, (in_rate, out_rate) in rates.items():
        if model.startswith(prefix):
            return prompt_tokens * in_rate + completion_tokens * out_rate
    return 0.0


# ---------------------------------------------------------------------------
# Groq implementation
# ---------------------------------------------------------------------------


class GroqProvider(LLMProvider):
    name = "groq"

    def __init__(self, api_key: str, model: str, timeout_seconds: float = 45.0):
        if not api_key:
            raise ValueError("GROQ_API_KEY is required for GroqProvider")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout_seconds

    async def generate(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        try:
            from groq import AsyncGroq, APIStatusError
        except ImportError as exc:
            raise ProviderError(
                "groq SDK not installed", self.name, retryable=False
            ) from exc

        client = AsyncGroq(api_key=self._api_key)
        t0 = time.monotonic()
        try:
            async with asyncio.timeout(self._timeout):
                completion = await client.chat.completions.create(
                    model=self._model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
        except TimeoutError as exc:
            raise ProviderTimeoutError(
                f"Groq timed out after {self._timeout}s", self.name
            ) from exc
        except APIStatusError as exc:
            if exc.status_code == 429:
                raise ProviderRateLimitError(str(exc), self.name) from exc
            raise ProviderError(str(exc), self.name) from exc
        except Exception as exc:
            raise ProviderError(f"Groq request failed: {exc}", self.name) from exc

        latency_ms = (time.monotonic() - t0) * 1000
        choice = completion.choices[0]
        text = choice.message.content or ""
        total = completion.usage.total_tokens if completion.usage else 0
        prompt_t = completion.usage.prompt_tokens if completion.usage else 0
        comp_t = completion.usage.completion_tokens if completion.usage else 0
        usage = TokenUsage(
            prompt_tokens=prompt_t,
            completion_tokens=comp_t,
            total_tokens=total,
            estimated_cost_usd=None,  # Groq pricing varies
        )
        return GenerationResult(
            text=text,
            provider=self.name,
            model=self._model,
            usage=usage,
            latency_ms=latency_ms,
        )

    async def health_check(self) -> bool:
        try:
            result = await self.generate(
                system="Health check.", user="Reply OK.", max_tokens=5
            )
            return bool(result.text)
        except ProviderError:
            return False


# ---------------------------------------------------------------------------
# Deterministic provider (CI / tests only)
# ---------------------------------------------------------------------------


class DeterministicProvider(LLMProvider):
    """
    Returns pre-registered fixture responses keyed by prompt hash.
    Must NEVER be enabled in production (enforced by ProviderRouter factory).
    """

    name = "deterministic"

    def __init__(self, fixtures: dict[str, str] | None = None):
        self._fixtures: dict[str, str] = fixtures or {}

    def register(self, system: str, user: str, response: str) -> str:
        key = self._key(system, user)
        self._fixtures[key] = response
        return key

    def register_default(self, response: str) -> None:
        """Response returned when no specific fixture matches."""
        self._fixtures["__default__"] = response

    @staticmethod
    def _key(system: str, user: str) -> str:
        h = hashlib.sha256((system + "\x00" + user).encode()).hexdigest()[:16]
        return h

    async def generate(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        key = self._key(system, user)
        text = self._fixtures.get(key) or self._fixtures.get("__default__") or ""
        if not text:
            raise ProviderError(
                f"No fixture registered for key {key}", self.name, retryable=False
            )
        tokens = len(text.split())
        return GenerationResult(
            text=text,
            provider=self.name,
            model="deterministic-v1",
            usage=TokenUsage(
                prompt_tokens=0,
                completion_tokens=tokens,
                total_tokens=tokens,
                estimated_cost_usd=0.0,
            ),
            latency_ms=0.0,
        )

    async def health_check(self) -> bool:
        return True


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------


class CircuitState(enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Simple in-process circuit breaker per provider.
    State resets after recovery_timeout_seconds.
    """

    def __init__(
        self,
        provider_name: str,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 300.0,
    ):
        self._name = provider_name
        self._threshold = failure_threshold
        self._timeout = recovery_timeout_seconds
        self._failures = 0
        self._state = CircuitState.CLOSED
        self._opened_at: float | None = None

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN and self._opened_at is not None:
            elapsed = time.monotonic() - self._opened_at
            if elapsed >= self._timeout:
                self._state = CircuitState.HALF_OPEN
                log.info(
                    "circuit_breaker_half_open",
                    provider=self._name,
                    elapsed_s=round(elapsed, 1),
                )
        return self._state

    def is_available(self) -> bool:
        return self.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)

    def record_success(self) -> None:
        if self._state != CircuitState.CLOSED:
            log.info("circuit_breaker_closed", provider=self._name)
        self._failures = 0
        self._state = CircuitState.CLOSED
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self._threshold and self._state == CircuitState.CLOSED:
            self._state = CircuitState.OPEN
            self._opened_at = time.monotonic()
            log.warning(
                "circuit_breaker_opened",
                provider=self._name,
                failures=self._failures,
            )


# ---------------------------------------------------------------------------
# Provider router
# ---------------------------------------------------------------------------


class ProviderRouter:
    """Route requests through an ordered provider chain with bounded retries.

    Provider-specific exceptions and unexpected SDK/network exceptions are
    normalized so a failed primary can safely fall back. Content-policy
    refusals always fail closed and are never sent to another provider.
    """

    def __init__(
        self,
        providers: list[LLMProvider],
        max_retries_per_provider: int = 2,
        cb_failure_threshold: int = 5,
        cb_recovery_timeout_s: float = 300.0,
        request_timeout_seconds: float = 60.0,
    ):
        if not providers:
            raise ValueError("ProviderRouter requires at least one provider")
        if len({provider.name for provider in providers}) != len(providers):
            raise ValueError("Provider names must be unique within a ProviderRouter")
        self._providers = providers
        self._max_retries = max(1, max_retries_per_provider)
        self._request_timeout = max(0.01, request_timeout_seconds)
        self._breakers = {
            provider.name: CircuitBreaker(
                provider.name, cb_failure_threshold, cb_recovery_timeout_s
            )
            for provider in providers
        }

    async def generate(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        errors: list[str] = []
        for provider in self._providers:
            breaker = self._breakers[provider.name]
            if not breaker.is_available():
                errors.append(f"{provider.name}: circuit open (state={breaker.state.value})")
                log.warning("provider_skipped_circuit_open", provider=provider.name)
                continue

            for attempt in range(1, self._max_retries + 1):
                try:
                    async with asyncio.timeout(self._request_timeout):
                        result = await provider.generate(
                            system=system,
                            user=user,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                    breaker.record_success()
                    log.info(
                        "generation_success",
                        **result.to_telemetry_dict(),
                        attempt=attempt,
                    )
                    return result
                except ProviderContentPolicyError:
                    breaker.record_failure()
                    raise
                except TimeoutError:
                    error = ProviderTimeoutError(
                        f"{provider.name} timed out after {self._request_timeout}s",
                        provider.name,
                    )
                    breaker.record_failure()
                    errors.append(f"{provider.name}[{attempt}]: {error}")
                    log.warning(
                        "provider_attempt_failed",
                        provider=provider.name,
                        attempt=attempt,
                        error=str(error),
                        retryable=True,
                    )
                except ProviderError as exc:
                    breaker.record_failure()
                    errors.append(f"{provider.name}[{attempt}]: {exc}")
                    log.warning(
                        "provider_attempt_failed",
                        provider=provider.name,
                        attempt=attempt,
                        error=str(exc),
                        retryable=exc.retryable,
                    )
                    if not exc.retryable:
                        break
                except Exception as exc:
                    # Last-resort normalization for provider adapters supplied by
                    # plugins or tests. Raw exceptions must not bypass fallback.
                    error = ProviderError(
                        f"Unexpected {provider.name} failure: {exc}",
                        provider.name,
                    )
                    breaker.record_failure()
                    errors.append(f"{provider.name}[{attempt}]: {error}")
                    log.warning(
                        "provider_attempt_failed",
                        provider=provider.name,
                        attempt=attempt,
                        error=str(error),
                        retryable=True,
                    )

                if attempt < self._max_retries:
                    await asyncio.sleep(2.0 ** (attempt - 1))

        raise AllProvidersFailedError(
            f"All providers exhausted. Errors: {'; '.join(errors)}"
        )

    def provider_states(self) -> dict[str, str]:
        return {name: breaker.state.value for name, breaker in self._breakers.items()}


def build_provider_router(settings: Any) -> ProviderRouter:
    """Build an ordered, fail-closed provider chain from application settings.
    
    Provider strategy (per accepted ADR):
    - Primary: Azure OpenAI
    - Fallback: Anthropic -> Groq
    """
    env = str(
        getattr(settings, "APP_ENV", None)
        or getattr(settings, "ENVIRONMENT", "development")
    ).lower()
    requested = (getattr(settings, "LLM_PROVIDER", "") or "").lower().strip()

    if requested == "deterministic" or env == "test":
        if env != "test":
            raise RuntimeError(
                "DeterministicProvider is restricted to APP_ENV/ENVIRONMENT=test"
            )
        provider = DeterministicProvider()
        provider.register_default("{}")
        return ProviderRouter(
            [provider],
            max_retries_per_provider=1,
            request_timeout_seconds=float(getattr(settings, "LLM_TIMEOUT_SECONDS", 30)),
        )

    configured: dict[str, LLMProvider] = {}
    anthropic_key = getattr(settings, "ANTHROPIC_API_KEY", "")
    groq_key = getattr(settings, "GROQ_API_KEY", "")
    azure_endpoint = getattr(settings, "AZURE_OPENAI_ENDPOINT", "")
    azure_key = getattr(settings, "AZURE_OPENAI_API_KEY", "")
    timeout = float(getattr(settings, "LLM_TIMEOUT_SECONDS", 30))

    # Azure OpenAI - primary provider per ADR
    if azure_endpoint and azure_key:
        configured["azure"] = AzureOpenAIProvider(
            endpoint=azure_endpoint,
            api_key=azure_key,
            model=getattr(settings, "AZURE_OPENAI_MODEL", "gpt-4o"),
            api_version=getattr(settings, "AZURE_OPENAI_API_VERSION", "2024-02-01"),
            timeout_seconds=timeout,
        )

    if anthropic_key:
        configured["anthropic"] = AnthropicProvider(
            api_key=anthropic_key,
            model=getattr(settings, "ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            timeout_seconds=timeout,
        )
    if groq_key:
        configured["groq"] = GroqProvider(
            api_key=groq_key,
            model=getattr(settings, "GROQ_MODEL", "llama3-70b-8192"),
            timeout_seconds=timeout,
        )

    # Validate requested provider
    valid_providers = {"azure", "anthropic", "groq", "deterministic"}
    if requested and requested not in valid_providers:
        raise RuntimeError(f"Unsupported LLM_PROVIDER: {requested!r}")
    if requested and requested not in configured:
        raise RuntimeError(f"LLM_PROVIDER={requested!r} is selected but its API key is missing")
    if not configured:
        raise RuntimeError(
            "No LLM provider configured. Set AZURE_OPENAI_ENDPOINT+AZURE_OPENAI_API_KEY, "
            "ANTHROPIC_API_KEY, or GROQ_API_KEY; deterministic mode is test-only."
        )

    # Build provider chain: Azure (primary) -> Anthropic -> Groq (fallbacks)
    if requested:
        # User-specified provider only
        order = [requested]
    else:
        # Default chain: Azure -> Anthropic -> Groq
        order = ["azure", "anthropic", "groq"]
    
    providers = [configured[name] for name in order if name in configured]
    return ProviderRouter(
        providers,
        max_retries_per_provider=int(getattr(settings, "LLM_MAX_RETRIES", 2)),
        request_timeout_seconds=timeout,
    )



# ---------------------------------------------------------------------------
# Azure OpenAI implementation
# ---------------------------------------------------------------------------


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI provider with structured output support."""
    
    name = "azure"

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        model: str,
        api_version: str = "2024-02-01",
        timeout_seconds: float = 60.0,
    ):
        if not endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is required for AzureOpenAIProvider")
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is required for AzureOpenAIProvider")
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._api_version = api_version
        self._timeout = timeout_seconds

    async def generate(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        try:
            from openai import AsyncAzureOpenAI
        except ImportError as exc:
            raise ProviderError(
                "openai SDK not installed", self.name, retryable=False
            ) from exc

        client = AsyncAzureOpenAI(
            api_key=self._api_key,
            azure_endpoint=self._endpoint,
            api_version=self._api_version,
        )
        t0 = time.monotonic()
        try:
            async with asyncio.timeout(self._timeout):
                msg = await client.chat.completions.create(
                    model=self._model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
        except TimeoutError as exc:
            raise ProviderTimeoutError(
                f"Azure OpenAI timed out after {self._timeout}s", self.name
            ) from exc
        except Exception as exc:
            raise ProviderError(f"Azure OpenAI request failed: {exc}", self.name) from exc

        latency_ms = (time.monotonic() - t0) * 1000
        choice = msg.choices[0]
        text = choice.message.content or ""
        usage = msg.usage
        total = usage.total_tokens if usage else 0
        prompt_t = usage.prompt_tokens if usage else 0
        comp_t = usage.completion_tokens if usage else 0
        
        # Azure pricing varies; estimate based on model family
        estimated_cost = self._estimate_cost(prompt_t, comp_t)
        
        return GenerationResult(
            text=text,
            provider=self.name,
            model=self._model,
            usage=TokenUsage(
                prompt_tokens=prompt_t,
                completion_tokens=comp_t,
                total_tokens=total,
                estimated_cost_usd=estimated_cost,
            ),
            latency_ms=latency_ms,
        )

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost in USD. Azure pricing varies by deployment."""
        # Conservative estimate - actual costs depend on deployment
        rate_per_1k = 0.002  # Approximate for GPT-4o
        return (prompt_tokens + completion_tokens) / 1000 * rate_per_1k

    async def health_check(self) -> bool:
        try:
            result = await self.generate(
                system="You are a health-check probe.",
                user="Reply with the single word OK.",
                max_tokens=10,
            )
            return "ok" in result.text.lower()
        except ProviderError:
            return False
