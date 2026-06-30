"""
EduBoost SA — Phase 2 (L2-04)
LLM Gateway V2 — Provider Fallback, Circuit Breaker & Timeout

Extends the existing gateway with:
  • Groq (primary) → Anthropic (fallback) → static/cached fallback
  • Per-provider circuit breaker (opens after 3 consecutive failures)
  • 30-second call timeout
  • Exponential back-off retry (3 attempts per provider)
  • Structured response envelope used by all callers

Public API
----------
    gateway = LLMGatewayV2.from_settings(settings)
    response = await gateway.complete(prompt="…", system="…", **kwargs)

The returned dict always has the shape:
    {
        "content": str,
        "provider": "groq" | "anthropic" | "static",
        "model": str,
        "used_fallback": bool,
        "prompt_tokens": int,
        "completion_tokens": int,
        "total_tokens": int,
        "latency_ms": int,
    }
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Circuit-breaker state
# ---------------------------------------------------------------------------

class CircuitState(Enum):
    CLOSED = "closed"       # normal operation
    OPEN = "open"           # failing — reject calls immediately
    HALF_OPEN = "half_open" # probe — allow one call through


@dataclass
class CircuitBreaker:
    """Per-provider circuit breaker.

    Opens after ``failure_threshold`` consecutive failures.
    Transitions to HALF_OPEN after ``recovery_timeout_s`` seconds.
    """

    name: str
    failure_threshold: int = 3
    recovery_timeout_s: float = 60.0

    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _consecutive_failures: int = field(default=0, init=False)
    _opened_at: float | None = field(default=None, init=False)

    @property
    def state(self) -> CircuitState:
        if self._state is CircuitState.OPEN:
            if self._opened_at and (time.monotonic() - self._opened_at) >= self.recovery_timeout_s:
                self._state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker '%s' → HALF_OPEN (probing).", self.name)
        return self._state

    def record_success(self) -> None:
        self._consecutive_failures = 0
        if self._state is not CircuitState.CLOSED:
            logger.info("Circuit breaker '%s' → CLOSED (recovered).", self.name)
        self._state = CircuitState.CLOSED
        self._opened_at = None

    def record_failure(self) -> None:
        self._consecutive_failures += 1
        if self._state is CircuitState.HALF_OPEN or self._consecutive_failures >= self.failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = time.monotonic()
            logger.warning(
                "Circuit breaker '%s' → OPEN after %d failure(s).",
                self.name,
                self._consecutive_failures,
            )

    def is_available(self) -> bool:
        return self.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class LLMGatewayError(Exception):
    """Raised when all providers fail."""


class ProviderUnavailableError(LLMGatewayError):
    """Raised when a specific provider's circuit breaker is open."""


# ---------------------------------------------------------------------------
# Static / cached fallback
# ---------------------------------------------------------------------------

_STATIC_FALLBACK_RESPONSE = {
    "content": (
        "⚠️ Our lesson generation service is temporarily unavailable. "
        "Please try again in a few minutes. Your progress has been saved."
    ),
    "provider": "static",
    "model": "static_fallback_v1",
    "used_fallback": True,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "latency_ms": 0,
}


# ---------------------------------------------------------------------------
# Provider adapters
# ---------------------------------------------------------------------------

class GroqAdapter:
    """Thin async wrapper around the Groq client."""

    PROVIDER_NAME = "groq"
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    TIMEOUT_S = 30.0

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        self._api_key = api_key
        self.model = model

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **_: Any,
    ) -> dict[str, Any]:
        try:
            from groq import AsyncGroq  # type: ignore[import]
        except ImportError as exc:
            raise LLMGatewayError("groq package not installed") from exc

        client = AsyncGroq(api_key=self._api_key)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            resp = await asyncio.wait_for(
                client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                ),
                timeout=self.TIMEOUT_S,
            )
        except asyncio.TimeoutError as exc:
            raise LLMGatewayError(f"Groq call timed out after {self.TIMEOUT_S}s") from exc

        choice = resp.choices[0]
        usage = resp.usage or {}
        return {
            "content": choice.message.content or "",
            "provider": self.PROVIDER_NAME,
            "model": resp.model,
            "used_fallback": False,
            "prompt_tokens": getattr(usage, "prompt_tokens", 0),
            "completion_tokens": getattr(usage, "completion_tokens", 0),
            "total_tokens": getattr(usage, "total_tokens", 0),
        }


class AnthropicAdapter:
    """Thin async wrapper around the Anthropic client."""

    PROVIDER_NAME = "anthropic"
    DEFAULT_MODEL = "claude-sonnet-4-20250514"
    TIMEOUT_S = 30.0

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        self._api_key = api_key
        self.model = model

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **_: Any,
    ) -> dict[str, Any]:
        try:
            import anthropic as ac  # type: ignore[import]
        except ImportError as exc:
            raise LLMGatewayError("anthropic package not installed") from exc

        client = ac.AsyncAnthropic(api_key=self._api_key)
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        try:
            resp = await asyncio.wait_for(
                client.messages.create(**kwargs),
                timeout=self.TIMEOUT_S,
            )
        except asyncio.TimeoutError as exc:
            raise LLMGatewayError(f"Anthropic call timed out after {self.TIMEOUT_S}s") from exc

        content = "".join(
            block.text for block in resp.content if hasattr(block, "text")
        )
        usage = resp.usage or {}
        return {
            "content": content,
            "provider": self.PROVIDER_NAME,
            "model": resp.model,
            "used_fallback": True,  # it's the fallback provider
            "prompt_tokens": getattr(usage, "input_tokens", 0),
            "completion_tokens": getattr(usage, "output_tokens", 0),
            "total_tokens": getattr(usage, "input_tokens", 0) + getattr(usage, "output_tokens", 0),
        }


# ---------------------------------------------------------------------------
# Main gateway
# ---------------------------------------------------------------------------

class LLMGatewayV2:
    """Resilient LLM gateway with provider fallback and circuit breakers.

    Provider chain: Groq → Anthropic → static fallback.
    Each provider is guarded by an independent circuit breaker.
    Each call is retried up to ``max_retries`` times before falling through
    to the next provider.
    """

    MAX_RETRIES = 3
    RETRY_BASE_DELAY_S = 1.0

    def __init__(
        self,
        groq_adapter: GroqAdapter | None = None,
        anthropic_adapter: AnthropicAdapter | None = None,
    ) -> None:
        self._providers: list[tuple[str, Any, CircuitBreaker]] = []

        if groq_adapter:
            self._providers.append((
                "groq",
                groq_adapter,
                CircuitBreaker(name="groq"),
            ))
        if anthropic_adapter:
            self._providers.append((
                "anthropic",
                anthropic_adapter,
                CircuitBreaker(name="anthropic"),
            ))

        # Token-usage rolling window (for budget guardrails in L2-05)
        self._token_log: deque[dict[str, Any]] = deque(maxlen=10_000)

    @classmethod
    def from_settings(cls, settings: Any) -> "LLMGatewayV2":
        """Construct from a settings object (Pydantic BaseSettings or similar)."""
        groq = GroqAdapter(api_key=settings.GROQ_API_KEY) if getattr(settings, "GROQ_API_KEY", None) else None
        anth = AnthropicAdapter(api_key=settings.ANTHROPIC_API_KEY) if getattr(settings, "ANTHROPIC_API_KEY", None) else None
        return cls(groq_adapter=groq, anthropic_adapter=anth)

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Call LLM with automatic provider fallback.

        Parameters
        ----------
        prompt:
            User-facing prompt text.
        system:
            Optional system instruction.
        temperature:
            Sampling temperature (0.0 for deterministic).
        max_tokens:
            Maximum completion tokens.
        metadata:
            Arbitrary metadata dict logged with token usage (no prompt content).

        Returns
        -------
        dict
            Standard response envelope (see module docstring).
        """
        t0 = time.monotonic()

        for provider_name, adapter, breaker in self._providers:
            if not breaker.is_available():
                logger.warning("Provider '%s' circuit breaker is OPEN — skipping.", provider_name)
                continue

            for attempt in range(1, self.MAX_RETRIES + 1):
                try:
                    logger.debug("Calling provider '%s' (attempt %d/%d).", provider_name, attempt, self.MAX_RETRIES)
                    response = await adapter.complete(
                        prompt=prompt,
                        system=system,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs,
                    )
                    breaker.record_success()
                    response["latency_ms"] = int((time.monotonic() - t0) * 1000)
                    self._log_token_usage(response, metadata)
                    return response

                except LLMGatewayError as exc:
                    logger.warning(
                        "Provider '%s' attempt %d failed: %s",
                        provider_name,
                        attempt,
                        exc,
                    )
                    if attempt < self.MAX_RETRIES:
                        delay = self.RETRY_BASE_DELAY_S * (2 ** (attempt - 1))
                        await asyncio.sleep(delay)
                    else:
                        breaker.record_failure()

                except Exception as exc:  # pragma: no cover
                    logger.error("Unexpected error from provider '%s': %s", provider_name, exc)
                    breaker.record_failure()
                    break

        # All providers exhausted — return static fallback
        logger.error("All LLM providers exhausted — returning static fallback.")
        static = dict(_STATIC_FALLBACK_RESPONSE)
        static["latency_ms"] = int((time.monotonic() - t0) * 1000)
        return static

    # ------------------------------------------------------------------
    # Token usage logging (no prompt content — POPIA compliant)
    # ------------------------------------------------------------------

    def _log_token_usage(
        self,
        response: dict[str, Any],
        metadata: dict[str, Any] | None,
    ) -> None:
        """Log token usage for budget tracking without logging prompt content."""
        entry: dict[str, Any] = {
            "ts": time.time(),
            "provider": response.get("provider"),
            "model": response.get("model"),
            "prompt_tokens": response.get("prompt_tokens", 0),
            "completion_tokens": response.get("completion_tokens", 0),
            "total_tokens": response.get("total_tokens", 0),
            "latency_ms": response.get("latency_ms", 0),
        }
        # Attach safe metadata (caller provides — must not include prompt text)
        if metadata:
            safe_meta = {k: v for k, v in metadata.items() if k not in {"prompt", "system", "content"}}
            entry["meta"] = safe_meta

        self._token_log.append(entry)
        logger.info(
            "LLM usage | provider=%s model=%s tokens=%d latency=%dms",
            entry["provider"],
            entry["model"],
            entry["total_tokens"],
            entry["latency_ms"],
        )

    def circuit_breaker_states(self) -> dict[str, str]:
        """Return current state of all circuit breakers (for health checks)."""
        return {name: str(breaker.state.value) for name, _, breaker in self._providers}
