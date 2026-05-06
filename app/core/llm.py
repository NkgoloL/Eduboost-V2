"""
EduBoost V2 — Executive Service (Pillar 2)
Fully async LLM inference via Anthropic + Groq with:
  - Redis-backed semantic caching
  - Per-user daily quota enforcement
  - Pydantic-enforced structured output (JSON mode)
"""
from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
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
from app.core.policy import PolicyViolation, LessonPayload
from app.core.logging import get_logger
from app.core.metrics import record_llm_tokens
from app.core.rate_limiter import AIQuotaExceeded, check_ai_quota
from app.core.redis import cache_get, cache_set
from app.services.policy_service import PolicyService
from app.services.caps_validator import CAPSAlignmentValidator

log = get_logger(__name__)

# ── Clients (instantiated once per worker) ────────────────────────────────────
_groq_client: AsyncGroq | None = None
_anthropic_client: anthropic.AsyncAnthropic | None = None
_local_hf_runtime: dict[str, Any] | None = None
PROJECT_ROOT = Path(__file__).resolve().parents[2]


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


def _resolve_project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _local_hf_configured() -> bool:
    return (
        _resolve_project_path(settings.LOCAL_MERGED_MODEL_PATH).exists()
        or _resolve_project_path(settings.LOCAL_ADAPTER_PATH).exists()
    )


def _get_local_hf_runtime() -> dict[str, Any]:
    """Load the local focused CAPS model lazily for development/test inference."""
    global _local_hf_runtime
    if _local_hf_runtime is not None:
        return _local_hf_runtime

    try:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:  # pragma: no cover - depends on ML extras
        raise RuntimeError("Install ML dependencies before using LLM_PROVIDER=local_hf") from exc

    merged_path = _resolve_project_path(settings.LOCAL_MERGED_MODEL_PATH)
    adapter_path = _resolve_project_path(settings.LOCAL_ADAPTER_PATH)
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    if merged_path.exists() and (merged_path / "config.json").exists():
        model_source = str(merged_path)
        tokenizer_source = str(merged_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_source,
            torch_dtype=dtype,
            device_map="auto",
            trust_remote_code=True,
        )
    elif adapter_path.exists():
        model_source = settings.LOCAL_BASE_MODEL_ID
        tokenizer_source = str(adapter_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_source,
            torch_dtype=dtype,
            device_map="auto",
            trust_remote_code=True,
        )
        model = PeftModel.from_pretrained(model, str(adapter_path))
    else:
        raise RuntimeError(
            "No local model found. Set LOCAL_MERGED_MODEL_PATH or LOCAL_ADAPTER_PATH "
            "to a trained EduBoost adapter/model directory."
        )

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_source, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()
    _local_hf_runtime = {"model": model, "tokenizer": tokenizer, "model_source": model_source}
    return _local_hf_runtime


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

_LOCAL_HF_SYSTEM_PROMPT = (
    "You are EduBoost Brain, a South African CAPS-aligned teaching assistant. "
    "Respond with age-appropriate pedagogy, clear structure, and POPIA-safe language. "
    "When generating lessons, use these sections: Title, Grade, Subject, CAPS alignment, "
    "Lesson objective, Teaching activity, Worked example, Assessment evidence, and Support and extension."
)


class LessonGenerator:
    """AI Lesson Generation Engine. Orchestrates AI inference."""

    def __init__(self) -> None:
        self._judiciary = PolicyService()
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

        if (
            settings.LLM_PROVIDER != "local_hf"
            and not settings.GROQ_API_KEY
            and not settings.ANTHROPIC_API_KEY
            and not settings.is_production()
        ):
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
                raise PolicyViolation(final_validation.reason)

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
        if settings.LLM_PROVIDER == "local_hf":
            return await self._call_local_hf(user_prompt, operation=operation)
        if settings.LLM_PROVIDER == "anthropic":
            return await self._call_anthropic(user_prompt, operation=operation)
        try:
            return await self._call_groq(user_prompt, operation=operation)
        except Exception as exc:
            log.warning("groq_lesson_generation_failed", error=str(exc))
            return await self._call_anthropic(user_prompt, operation=operation)

    async def _call_local_hf(self, user_prompt: str, *, operation: str) -> str:
        return await asyncio.to_thread(self._call_local_hf_sync, user_prompt, operation=operation)

    def _call_local_hf_sync(self, user_prompt: str, *, operation: str) -> str:
        runtime = _get_local_hf_runtime()
        model = runtime["model"]
        tokenizer = runtime["tokenizer"]
        prompt = (
            "<|system|>\n"
            f"{_LOCAL_HF_SYSTEM_PROMPT}\n"
            "<|user|>\n"
            f"{user_prompt}\n"
            "Use these sections: Title, Grade, Subject, CAPS alignment, Lesson objective, "
            "Teaching activity, Worked example, Assessment evidence, and Support and extension.\n"
            "<|assistant|>\n"
        )
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        prompt_tokens = int(inputs["input_ids"].shape[-1])
        with __import__("torch").no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=settings.LOCAL_LLM_MAX_NEW_TOKENS,
                temperature=settings.LOCAL_LLM_TEMPERATURE,
                do_sample=settings.LOCAL_LLM_TEMPERATURE > 0,
                pad_token_id=tokenizer.eos_token_id,
            )
        completion_ids = output[0][prompt_tokens:]
        completion = tokenizer.decode(completion_ids, skip_special_tokens=True).strip()
        record_llm_tokens(
            provider="local_hf",
            model=str(runtime["model_source"]),
            operation=operation,
            input_tokens=prompt_tokens,
            output_tokens=int(completion_ids.shape[-1]),
        )
        return _coerce_lesson_json(completion)

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


def _extract_json_object(text: str) -> str:
    """Return the first JSON object from model text, or the original text if none is found."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return text
    return text[start : end + 1]


def _coerce_lesson_json(text: str) -> str:
    """Convert focused adapter section text into the app's lesson JSON schema."""
    text = _strip_generation_artifacts(text)
    candidate = _extract_json_object(text)
    try:
        parsed = json.loads(candidate)
        if _has_lesson_payload_fields(parsed):
            return candidate
        if isinstance(parsed, dict):
            text = _json_dict_to_section_text(parsed)
    except json.JSONDecodeError:
        pass

    sections = _extract_labelled_sections(text)
    title = sections.get("title") or "CAPS-aligned lesson"
    objective = sections.get("lesson objective") or sections.get("objective") or ""
    activity = sections.get("teaching activity") or ""
    assessment = sections.get("assessment evidence") or ""
    support = sections.get("support and extension") or ""
    payload = {
        "title": title,
        "introduction": " ".join(part for part in [sections.get("caps alignment", ""), objective] if part).strip()
        or text[:500],
        "main_content": activity or text[:900],
        "worked_example": sections.get("worked example") or "Work through one short example with the learner.",
        "practice_question": sections.get("practice question") or "What is one thing you learned, and how can you show it?",
        "answer": sections.get("answer") or assessment or "A strong answer explains the idea in the learner's own words.",
        "cultural_hook": support
        or "Connect the lesson to an everyday South African classroom, home, or community example.",
    }
    return json.dumps(payload)


def _strip_generation_artifacts(text: str) -> str:
    for marker in ["<|user|>", "<|assistant|>", "<|system|>", "<|unexpected", "<|response|>", "</s>"]:
        marker_index = text.find(marker)
        if marker_index != -1:
            text = text[:marker_index]
    return text.strip()


def _has_lesson_payload_fields(value: Any) -> bool:
    required = {
        "title",
        "introduction",
        "main_content",
        "worked_example",
        "practice_question",
        "answer",
        "cultural_hook",
    }
    return isinstance(value, dict) and required.issubset(value)


def _json_dict_to_section_text(value: dict[str, Any]) -> str:
    return "\n".join(f"{key}: {content}" for key, content in value.items() if content)


def _extract_labelled_sections(text: str) -> dict[str, str]:
    labels = [
        "title",
        "grade",
        "subject",
        "caps alignment",
        "lesson objective",
        "objective",
        "teaching activity",
        "worked example",
        "assessment evidence",
        "support and extension",
        "practice question",
        "answer",
    ]
    positions: list[tuple[int, str, int]] = []
    lowered = text.lower()
    for label in labels:
        needle = f"{label}:"
        start = lowered.find(needle)
        if start != -1:
            positions.append((start, label, start + len(needle)))
    positions.sort()

    sections: dict[str, str] = {}
    for index, (start, label, content_start) in enumerate(positions):
        end = positions[index + 1][0] if index + 1 < len(positions) else len(text)
        value = text[content_start:end].strip(" \n\r\t-*0123456789.")
        if value:
            sections[label] = value
    return sections
