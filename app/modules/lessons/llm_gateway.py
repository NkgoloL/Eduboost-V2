"""Provider-agnostic LLM gateway with automatic fallback.

Abstraction layer over Groq (primary) and Anthropic Claude (fallback)
for all AI lesson-generation calls in EduBoost.  Real learner UUIDs are
**never** passed to external providers — always use ``pseudonym_id``.

All calls are instrumented with Prometheus metrics via
:mod:`app.core.metrics` for latency, token usage, and error tracking.

Example:
    Generate a lesson completion::

        from app.modules.lessons.llm_gateway import LLMGateway

        gateway = LLMGateway()
        response = await gateway.generate(
            prompt="Explain fractions for Grade 4",
            system="You are a CAPS-aligned tutor.",
        )
        print(response.content[:200])
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from app.core.config import get_settings
from app.core.exceptions import LLMError
from app.core.metrics import llm_latency_seconds, llm_requests_total, record_llm_tokens

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Value object returned by the LLM gateway after a completion call."""

    content: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    model: str


class LLMGateway:
    """Async gateway for all LLM calls in EduBoost.

    Groq is the primary provider (fast, cost-effective).  Anthropic Claude
    is the automatic fallback.  Provider coupling is fully isolated here —
    service modules never call LLM APIs directly.

    The gateway instruments every call with :data:`~app.core.metrics.llm_latency_seconds`
    and :data:`~app.core.metrics.llm_requests_total` for observability.

    Example:
        ::

            gateway = LLMGateway()
            resp = await gateway.generate("Explain place value for Grade 3.")
            assert resp.provider in ("groq", "anthropic")
    """

    async def generate(
        self,
        prompt: str,
        *,
        system: str = "",
        language: str = "en",
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Generate an LLM completion with automatic provider fallback.

        Attempts Groq first; on any failure, transparently retries against
        Anthropic Claude.  Both attempts are recorded in Prometheus
        counters.

        Args:
            prompt: The user-facing prompt text to send to the model.
            system: Optional system prompt providing behavioural context
                (e.g. ``"You are a CAPS-aligned tutor."``).
            language: ISO 639-1 language code for the response
                (default ``"en"``).
            max_tokens: Maximum tokens to generate (default ``1024``).

        Returns:
            LLMResponse: Generated text with provider metadata and
            token counts.

        Raises:
            LLMError: When both Groq and Anthropic fail to produce a
                response.

        Example:
            ::

                resp = await LLMGateway().generate(
                    prompt="List the 9 provinces of South Africa.",
                    system="You are a helpful SA geography tutor.",
                    max_tokens=512,
                )
                assert resp.content
        """
        try:
            response = await self._call_groq(prompt, system=system, max_tokens=max_tokens)
            llm_requests_total.labels(provider="groq", status="success").inc()
            return response
        except Exception as groq_exc:
            logger.warning("Groq call failed (%s), falling back to Anthropic", groq_exc)
            llm_requests_total.labels(provider="groq", status="fallback").inc()

        try:
            response = await self._call_anthropic(prompt, system=system, max_tokens=max_tokens)
            llm_requests_total.labels(provider="anthropic", status="success").inc()
            return response
        except Exception as anthropic_exc:
            logger.error("Anthropic fallback also failed: %s", anthropic_exc)
            llm_requests_total.labels(provider="anthropic", status="error").inc()
            raise LLMError(
                "Lesson generation is temporarily unavailable. Please try again shortly."
            ) from anthropic_exc

    async def _call_groq(self, prompt: str, *, system: str, max_tokens: int) -> LLMResponse:
        """Call the Groq inference API (primary provider).

        Args:
            prompt: User prompt text.
            system: System prompt for behavioural context.
            max_tokens: Maximum tokens to generate.

        Returns:
            LLMResponse: Completion result with ``provider="groq"``.

        Raises:
            LLMError: If the Groq API key is not configured.
        """
        cfg = get_settings()
        if not cfg.groq_api_key:
            raise LLMError("Groq API key not configured")

        from groq import AsyncGroq  # type: ignore[import-untyped]

        client = AsyncGroq(api_key=cfg.groq_api_key)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        start = time.perf_counter()
        completion = await client.chat.completions.create(
            model=cfg.groq_model,
            messages=messages,
            max_tokens=max_tokens,
            timeout=cfg.llm_timeout_seconds,
        )
        duration = time.perf_counter() - start

        llm_latency_seconds.labels(provider="groq").observe(duration)
        usage = completion.usage
        if usage:
            record_llm_tokens(
                provider="groq",
                model=cfg.groq_model,
                operation="lesson_generation",
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
            )

        return LLMResponse(
            content=completion.choices[0].message.content or "",
            provider="groq",
            model=cfg.groq_model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
        )

    async def _call_anthropic(self, prompt: str, *, system: str, max_tokens: int) -> LLMResponse:
        """Call the Anthropic Claude API (fallback provider).

        Args:
            prompt: User prompt text.
            system: System prompt for behavioural context.
            max_tokens: Maximum tokens to generate.

        Returns:
            LLMResponse: Completion result with ``provider="anthropic"``.

        Raises:
            LLMError: If the Anthropic API key is not configured.
        """
        cfg = get_settings()
        if not cfg.anthropic_api_key:
            raise LLMError("Anthropic API key not configured")

        import anthropic

        client = anthropic.AsyncAnthropic(api_key=cfg.anthropic_api_key)

        start = time.perf_counter()
        message = await client.messages.create(
            model=cfg.anthropic_model,
            max_tokens=max_tokens,
            system=system or "You are a helpful South African educational assistant.",
            messages=[{"role": "user", "content": prompt}],
        )
        duration = time.perf_counter() - start

        llm_latency_seconds.labels(provider="anthropic").observe(duration)
        record_llm_tokens(
            provider="anthropic",
            model=cfg.anthropic_model,
            operation="lesson_generation",
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )

        return LLMResponse(
            content=message.content[0].text if message.content else "",
            provider="anthropic",
            model=cfg.anthropic_model,
            prompt_tokens=message.usage.input_tokens,
            completion_tokens=message.usage.output_tokens,
        )
