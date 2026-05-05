"""
EduBoost V2 — Executive Service (Pillar 2)
Fully async LLM inference via Anthropic + Groq with:
  - Redis-backed semantic caching
  - Per-user daily quota enforcement
  - Pydantic-enforced structured output (JSON mode)
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

import anthropic
from groq import AsyncGroq
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.core.config import settings
from app.core.judiciary import ConstitutionalViolation, LessonPayload
from app.core.logging import get_logger
from app.core.metrics import record_llm_tokens
from app.core.rate_limiter import AIQuotaExceeded, check_ai_quota
from app.core.redis import cache_get, cache_set
from app.services.judiciary import JudiciaryService
from app.services.caps_validator import CAPSAlignmentValidator

log = get_logger(__name__)

# ── Clients (instantiated once per worker) ────────────────────────────────────
_groq_client: AsyncGroq | None = None
_anthropic_client: anthropic.AsyncAnthropic | None = None


def _get_groq() -> AsyncGroq:
    global _groq_client
    if _groq_client is None:
        _groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    return _groq_client


def _get_anthropic() -> anthropic.AsyncAnthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client


# ── Quota enforcement ─────────────────────────────────────────────────────────

class QuotaExceededError(Exception):
    pass


async def check_and_consume_quota(user_id: str, tier: str) -> int:
    """Atomically increment and check daily request counter. Returns current count."""
    try:
        decision = await check_ai_quota(user_id, tier)
    except AIQuotaExceeded as exc:
        raise QuotaExceededError(str(exc.detail)) from exc
    return decision.used


# ── Semantic cache ────────────────────────────────────────────────────────────

def _cache_key(grade: int, subject: str, topic: str, language: str, archetype: str | None) -> str:
    raw = f"{grade}:{subject}:{topic}:{language}:{archetype}"
    return f"lesson_cache:{hashlib.sha256(raw.encode()).hexdigest()}"


# ── Lesson generation ─────────────────────────────────────────────────────────

_LESSON_SYSTEM_PROMPT = """
You are EduBoost, an expert South African educator. Generate a CAPS-aligned lesson.
Respond ONLY with a valid JSON object matching this exact schema (no markdown, no preamble):
{
  "title": "string",
  "introduction": "string",
  "main_content": "string",
  "worked_example": "string",
  "practice_question": "string",
  "answer": "string",
  "cultural_hook": "string — must include authentic SA context (ubuntu, rands, local fauna, braai, etc.)"
}
"""


class ExecutiveService:
    """Constitutional Pillar 2: The Executive. Orchestrates AI inference."""

    def __init__(self) -> None:
        self._judiciary = JudiciaryService()
        self._caps_validator = CAPSAlignmentValidator()

    async def generate_lesson(
        self,
        pseudonym_id: str,
        grade: int,
        subject: str,
        topic: str,
        language: str,
        archetype: str | None,
        user_id: str,
        tier: str,
        learner_context: dict[str, Any] | None = None,
    ) -> tuple[LessonPayload, bool]:
        """
        Returns (lesson_payload, served_from_cache).
        Raises QuotaExceededError if daily limit hit.
        """
        cache_k = _cache_key(grade, subject, topic, language, archetype)
        cached = await cache_get(cache_k)
        if cached:
            log.info("lesson_cache_hit", pseudonym=pseudonym_id, key=cache_k)
            payload = self._judiciary.stamp_lesson(cached)
            return payload, True

        await check_and_consume_quota(user_id, tier)

        if not settings.GROQ_API_KEY and not settings.ANTHROPIC_API_KEY and not settings.is_production():
            payload = _fallback_lesson_payload(grade, subject, topic, language)
            raw = payload.model_dump_json()
            await cache_set(cache_k, raw, ttl=settings.SEMANTIC_CACHE_TTL_SECONDS)
            log.info("lesson_generated_offline_fallback", pseudonym=pseudonym_id, subject=subject, topic=topic)
            return payload, False

        requested_topic = topic
        validation = self._caps_validator.validate(grade, subject, topic)
        if not validation.caps_aligned and validation.canonical_topic:
            topic = validation.canonical_topic

        user_prompt = self._build_lesson_prompt(
            grade,
            subject,
            topic,
            language,
            archetype,
            requested_topic,
            learner_context=learner_context,
        )

        try:
            raw = await self._call_with_fallback(user_prompt, operation="lesson_generation")
        except Exception as exc:
            if settings.is_production():
                raise
            payload = _fallback_lesson_payload(grade, subject, topic, language)
            raw = payload.model_dump_json()
            await cache_set(cache_k, raw, ttl=settings.SEMANTIC_CACHE_TTL_SECONDS)
            log.warning(
                "lesson_generated_offline_fallback_after_provider_failure",
                error=str(exc),
                pseudonym=pseudonym_id,
                subject=subject,
                topic=topic,
            )
            return payload, False
        payload = self._judiciary.stamp_lesson(raw)
        if not self._caps_validator.validate_generated_content(
            grade, subject, topic, f"{payload.introduction} {payload.main_content} {payload.worked_example}"
        ).caps_aligned:
            correction_prompt = (
                f"{user_prompt}\n\nCorrection: keep the lesson inside CAPS scope for Grade {grade} "
                f"{subject} and focus on {topic}."
            )
            raw = await self._call_with_fallback(correction_prompt, operation="lesson_generation_retry")
            payload = self._judiciary.stamp_lesson(raw)
            final_validation = self._caps_validator.validate_generated_content(
                grade, subject, topic, f"{payload.introduction} {payload.main_content} {payload.worked_example}"
            )
            if not final_validation.caps_aligned:
                raise ConstitutionalViolation(final_validation.reason)

        await cache_set(cache_k, raw, ttl=settings.SEMANTIC_CACHE_TTL_SECONDS)
        log.info("lesson_generated", pseudonym=pseudonym_id, provider="groq")
        return payload, False

    def _build_lesson_prompt(
        self,
        grade: int,
        subject: str,
        topic: str,
        language: str,
        archetype: str | None,
        requested_topic: str,
        learner_context: dict[str, Any] | None = None,
    ) -> str:
        prompt = (
            f"Grade {grade} | Subject: {subject} | Topic: {topic} | "
            f"Language: {language} | Learner archetype: {archetype or 'general'}"
        )
        if requested_topic != topic:
            prompt += f" | Requested topic adjusted from '{requested_topic}' to CAPS-aligned topic '{topic}'."
        if learner_context:
            prompt += f"\nLearner context: {json.dumps(learner_context, sort_keys=True)}"
        return prompt

    async def _call_with_fallback(self, user_prompt: str, *, operation: str) -> str:
        try:
            return await self._call_groq(user_prompt, operation=operation)
        except Exception as exc:
            log.warning("groq_lesson_generation_failed", error=str(exc))
            return await self._call_anthropic(user_prompt, operation=operation)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),  # Better to be more specific in production
        reraise=True,
    )
    async def _call_groq(self, user_prompt: str, *, operation: str) -> str:
        client = _get_groq()
        response = await client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": _LESSON_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=1200,
            temperature=0.7,
        )
        usage = response.usage
        if usage is not None:
            record_llm_tokens(
                provider="groq",
                model="llama3-70b-8192",
                operation=operation,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
            )
        return response.choices[0].message.content or "{}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def _call_anthropic(self, user_prompt: str, *, operation: str) -> str:
        """Fallback to Claude when Groq is unavailable."""
        client = _get_anthropic()
        response = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=1200,
            system=_LESSON_SYSTEM_PROMPT,
            tools=[
                {
                    "name": "submit_lesson",
                    "description": "Return a CAPS-aligned structured lesson payload.",
                    "input_schema": LessonPayload.model_json_schema(),
                }
            ],
            tool_choice={"type": "tool", "name": "submit_lesson"},
            messages=[{"role": "user", "content": user_prompt}],
        )
        record_llm_tokens(
            provider="anthropic",
            model=settings.ANTHROPIC_MODEL,
            operation=operation,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
        for block in response.content:
            if getattr(block, "type", "") == "tool_use" and getattr(block, "name", "") == "submit_lesson":
                return json.dumps(block.input)
        return response.content[0].text if response.content else "{}"

    async def generate_progress_summary(self, pseudonym_id: str, gaps: list[str], lessons_done: int) -> str:
        """Generate a parent-facing AI progress summary (no PII in prompt)."""
        prompt = (
            f"Summarise progress for a learner (pseudonym {pseudonym_id}). "
            f"Lessons completed: {lessons_done}. Active gaps: {', '.join(gaps) or 'none'}. "
            f"Write 2–3 sentences in plain English for a parent."
        )
        client = _get_groq()
        response = await client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.5,
        )
        usage = response.usage
        if usage is not None:
            record_llm_tokens(
                provider="groq",
                model="llama3-70b-8192",
                operation="parent_progress_summary",
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
            )
        return response.choices[0].message.content or "Progress data is being processed."


def _fallback_lesson_payload(grade: int, subject: str, topic: str, language: str) -> LessonPayload:
    lesson_language = {"zu": "isiZulu", "af": "Afrikaans", "xh": "isiXhosa"}.get(language, "English")
    return LessonPayload(
        title=f"{subject.title()} - {topic}",
        introduction=(
            f"Welcome to your Grade {grade} {subject.title()} lesson on {topic}. "
            f"This offline-friendly version keeps your learning moving while local AI providers are unavailable."
        ),
        main_content=(
            f"In this lesson, we focus on the key idea behind {topic}. "
            f"Read each section slowly, talk through the examples, and explain the idea back in {lesson_language} if that helps."
        ),
        worked_example=(
            f"Example: identify one simple fact about {topic}, then explain why it matters in your schoolwork."
        ),
        practice_question=f"Practice: write or say one thing you learned about {topic} and one question you still have.",
        answer=(
            "A strong answer names a correct idea from the lesson and adds a short explanation in the learner's own words."
        ),
        cultural_hook=(
            f"Think about how {topic} could show up in everyday South African life, like shopping in rands, sport, community, or the classroom."
        ),
    )
