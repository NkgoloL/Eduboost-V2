"""
EduBoost V2 — Executive Service (Pillar 2)
Fully async LLM inference via Anthropic + Groq with:
  - Redis-backed semantic caching
  - Per-user daily quota enforcement
  - Pydantic-enforced structured output (JSON mode)
"""
from __future__ import annotations

import hashlib
from typing import Any

import anthropic
from groq import AsyncGroq

from app.core.config import settings
from app.core.logging import get_logger
from app.core.rate_limiter import AIQuotaExceeded, check_ai_quota
from app.core.redis import cache_get, cache_set
from app.services.judiciary import JudiciaryService, LessonPayload

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

        user_prompt = (
            f"Grade {grade} | Subject: {subject} | Topic: {topic} | "
            f"Language: {language} | Learner archetype: {archetype or 'general'}"
        )

        raw = await self._call_with_fallback(user_prompt)
        payload = self._judiciary.stamp_lesson(raw)

        await cache_set(cache_k, raw, ttl=settings.SEMANTIC_CACHE_TTL_SECONDS)
        log.info("lesson_generated", pseudonym=pseudonym_id, provider="groq")
        return payload, False

    async def _call_with_fallback(self, user_prompt: str) -> str:
        try:
            return await self._call_groq(user_prompt)
        except Exception as exc:
            log.warning("groq_lesson_generation_failed", error=str(exc))
            return await self._call_anthropic(user_prompt)

    async def _call_groq(self, user_prompt: str) -> str:
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
        return response.choices[0].message.content or "{}"

    async def _call_anthropic(self, user_prompt: str) -> str:
        """Fallback to Claude when Groq is unavailable."""
        client = _get_anthropic()
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1200,
            system=_LESSON_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
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
        return response.choices[0].message.content or "Progress data is being processed."
