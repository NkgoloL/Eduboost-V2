"""
EduBoost SA — LLM Gateway
Abstraction layer over Groq (primary) and Anthropic (fallback).
Real learner UUIDs are NEVER passed here — always use pseudonym_id.
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
    content: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    model: str


class LLMGateway:
    """
    Single interface for all LLM calls throughout EduBoost.
    Groq is the primary provider (fast, cheap). Anthropic is the fallback.
    Provider coupling is isolated here — service modules never call LLM APIs directly.
    """

    async def generate(
        self,
        prompt: str,
        *,
        system: str = "",
        language: str = "en",
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Generate a completion. Falls back to Anthropic if Groq fails."""
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
