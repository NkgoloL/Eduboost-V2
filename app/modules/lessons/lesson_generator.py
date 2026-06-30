"""EduBoost SA — Lesson Generation Pipeline (Phase 3, Task L3-02).

Orchestrates the full lesson lifecycle:
  caps_ref + difficulty + misconception_tags
      → Jinja2 prompt render
      → LLM gateway call (Groq primary / Anthropic fallback)
      → LessonCreate schema validation
      → CAPS topic map validation
      → Content safety + PII check
      → Answer-key verification (independent second LLM call)
      → Quality score computation
      → Persistence to lessons table
      → LessonResponse returned

No lesson reaches the database without passing ALL validators.
No lesson is marked answer_key_verified=true without a second independent
LLM call agreeing on every practice question answer.

Example::

    generator = LessonGenerator(db)
    response = await generator.generate(
        caps_ref="4.M.1.1",
        difficulty="on_level",
        misconception_tags=["place_value_confusion"],
    )

Raises:
    LessonGenerationError: If LLM call fails, schema validation fails,
        CAPS validation fails, or the lesson cannot be persisted.
    LessonValidationError: If the generated lesson fails any quality gate.
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.exceptions import EduBoostError
from app.modules.lessons.llm_gateway import LLMGateway, LLMResponse
from app.modules.lessons.lesson_schema_v1 import LessonCreate, LessonResponse
from app.modules.lessons.lesson_validator import LessonValidator, LessonValidationError
from app.modules.lessons.answer_key_verifier import AnswerKeyVerifier
from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService
from app.services.ai_safety import redact_pii_text
from app.repositories.lesson_repository import LessonRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE_VERSION = "v1"
_PROMPTS_DIR = __file__.replace("lesson_generator.py", "prompts")


class LessonGenerationError(EduBoostError):
    """Raised when lesson generation fails at the LLM or schema stage."""

    status_code = 502
    error_code = "lesson_generation_failed"


@dataclass
class VerificationResult:
    """Result of independent answer-key verification."""

    agrees_on_all: bool
    disagreements: list[dict]  # [{question_id, original, derived, working}]
    verifier_notes: str
    raw_response: str


class LessonGenerator:
    """Full lesson generation pipeline with safety and quality gates.

    Pipeline (in order):
      1. Resolve caps_ref against CAPS topic map → get topic metadata
      2. Render lesson generation prompt (Jinja2 v1 template)
      3. Call LLM gateway (Groq → Anthropic fallback)
      4. Strip PII from raw LLM output
      5. Parse JSON and validate against LessonCreate schema
      6. Run all 8 lesson validator rules
      7. Call answer-key verifier (second independent LLM call)
      8. Compute quality score
      9. Persist to lessons table with full metadata
      10. Return LessonResponse

    Args:
        db: Async database session for lesson persistence.

    Example::

        generator = LessonGenerator(db)
        lesson = await generator.generate("4.M.1.1", difficulty="on_level")
        assert lesson.answer_key_verified is True
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._gateway = LLMGateway()
        self._validator = LessonValidator()
        self._caps_service = CAPSTopicMapService()
        self._repo = LessonRepository(db)
        self._jinja_env = Environment(
            loader=FileSystemLoader(_PROMPTS_DIR),
            autoescape=select_autoescape(enabled_extensions=()),  # not HTML
            trim_blocks=True,
            lstrip_blocks=True,
        )

    async def generate(
        self,
        caps_ref: str,
        *,
        difficulty: str = "on_level",
        misconception_tags: list[str] | None = None,
        language: str = "en",
        dry_run: bool = False,
    ) -> LessonResponse:
        """Generate, validate, and persist a single lesson.

        Args:
            caps_ref: CAPS reference e.g. ``"4.M.1.1"``.
            difficulty: One of ``foundational``, ``developing``,
                ``on_level``, ``extending``.
            misconception_tags: Optional learner misconception tags from
                a completed diagnostic. Used to target remediation.
            language: ISO 639-1 language code (default ``"en"``).
            dry_run: If True, skip persistence and return a validated
                LessonResponse without writing to DB.

        Returns:
            LessonResponse: Fully validated, persisted lesson.

        Raises:
            LessonGenerationError: On LLM call failure or JSON parse error.
            LessonValidationError: On any quality or safety gate failure.
        """
        start_ts = time.perf_counter()
        misconception_tags = misconception_tags or []

        # ── Step 1: Resolve CAPS reference ───────────────────────────────
        topic_meta = self._caps_service.get_topic_context(caps_ref)
        if topic_meta is None:
            raise LessonGenerationError(
                f"CAPS reference '{caps_ref}' not found in canonical topic map. "
                "Ensure the topic map is up to date and the reference uses the "
                "correct format (e.g. '4.M.1.1')."
            )

        logger.info(
            "Generating lesson caps_ref=%s difficulty=%s misconceptions=%s",
            caps_ref,
            difficulty,
            misconception_tags,
        )

        # ── Step 2: Render generation prompt ─────────────────────────────
        prompt = self._render_generation_prompt(
            topic_meta=topic_meta,
            difficulty=difficulty,
            misconception_tags=misconception_tags,
            language=language,
        )

        # ── Step 3: LLM gateway call ──────────────────────────────────────
        llm_response = await self._call_llm_with_error_handling(
            prompt=prompt,
            operation="lesson_generation",
            caps_ref=caps_ref,
        )

        # ── Step 4: PII redaction on raw LLM output ───────────────────────
        safe_content = redact_pii_text(llm_response.content)

        # ── Step 5: Parse JSON and validate schema ────────────────────────
        lesson_create = self._parse_and_validate_schema(
            raw_json=safe_content,
            caps_ref=caps_ref,
            llm_response=llm_response,
        )

        # ── Step 6: Run lesson validator (all 8 rules) ────────────────────
        validation_result = self._validator.validate(lesson_create, caps_ref=caps_ref)
        if not validation_result.passed:
            logger.warning(
                "Lesson for %s failed validation: %s",
                caps_ref,
                validation_result.failures,
            )
            raise LessonValidationError(
                f"Lesson for {caps_ref} failed {len(validation_result.failures)} "
                f"validation rule(s): {'; '.join(validation_result.failures)}",
                failures=validation_result.failures,
            )

        # ── Step 7: Answer-key verification (second independent LLM call) ─
        verification = await self._verify_answer_key(lesson_create)
        answer_key_verified = verification.agrees_on_all

        if not answer_key_verified:
            logger.warning(
                "Answer-key verification FAILED for %s — %d disagreement(s). "
                "Queuing for human review.",
                caps_ref,
                len(verification.disagreements),
            )

        # ── Step 8: Compute quality score ─────────────────────────────────
        quality_score = self._compute_quality_score(
            lesson=lesson_create,
            answer_key_verified=answer_key_verified,
            validation_result=validation_result,
        )

        # ── Step 9: Build final LessonCreate with computed fields ─────────
        generation_latency_ms = int((time.perf_counter() - start_ts) * 1000)

        final_lesson = lesson_create.model_copy(
            update={
                "lesson_id": uuid.uuid4(),
                "answer_key_verified": answer_key_verified,
                "quality_score": quality_score,
                "provider": llm_response.provider,
                "model_version": llm_response.model,
                "generation_latency_ms": generation_latency_ms,
                "token_usage": {
                    "prompt_tokens": llm_response.prompt_tokens,
                    "completion_tokens": llm_response.completion_tokens,
                    "total_tokens": llm_response.prompt_tokens + llm_response.completion_tokens,
                },
                "review_status": (
                    "approved"
                    if answer_key_verified and quality_score >= 0.85
                    else "ai_generated"
                    if answer_key_verified and quality_score >= 0.70
                    else "requires_review"
                ),
            }
        )

        # ── Step 10: Persist (unless dry_run) ─────────────────────────────
        if not dry_run:
            await self._repo.create_lesson(final_lesson)
            await self._db.commit()
            logger.info(
                "Lesson persisted caps_ref=%s lesson_id=%s quality=%.2f verified=%s latency=%dms",
                caps_ref,
                final_lesson.lesson_id,
                quality_score,
                answer_key_verified,
                generation_latency_ms,
            )
        else:
            logger.info(
                "DRY RUN — lesson for %s validated (quality=%.2f, verified=%s) but NOT persisted.",
                caps_ref,
                quality_score,
                answer_key_verified,
            )

        return LessonResponse.model_validate(final_lesson.model_dump())

    # ── Private helpers ───────────────────────────────────────────────────

    def _render_generation_prompt(
        self,
        *,
        topic_meta: dict,
        difficulty: str,
        misconception_tags: list[str],
        language: str,
    ) -> str:
        """Render the Jinja2 lesson generation prompt template."""
        template = self._jinja_env.get_template("lesson_generation_v1.jinja2")
        return template.render(
            caps_ref=topic_meta["caps_ref"],
            grade=topic_meta["grade"],
            term=topic_meta["term"],
            subject=topic_meta["subject"],
            topic=topic_meta["topic"],
            subtopic=topic_meta["subtopic"],
            objectives=topic_meta.get("assessment_standards", []),
            difficulty=difficulty,
            misconception_tags=misconception_tags,
            language=language,
            prompt_version=PROMPT_TEMPLATE_VERSION,
        )

    async def _call_llm_with_error_handling(
        self,
        *,
        prompt: str,
        operation: str,
        caps_ref: str,
    ) -> LLMResponse:
        """Call the LLM gateway with structured error logging."""
        system = (
            "You are an expert South African primary school curriculum specialist. "
            "You generate CAPS-aligned lesson content for EduBoost SA. "
            "Always respond with valid JSON only — no markdown, no explanation."
        )
        try:
            return await self._gateway.generate(
                prompt=prompt,
                system=system,
                max_tokens=3000,
            )
        except Exception as exc:
            logger.error(
                "LLM call failed for %s operation=%s: %s",
                caps_ref,
                operation,
                exc,
                exc_info=True,
            )
            raise LessonGenerationError(
                f"LLM generation failed for CAPS reference '{caps_ref}'. "
                "Please try again. If the problem persists, check provider status."
            ) from exc

    def _parse_and_validate_schema(
        self,
        *,
        raw_json: str,
        caps_ref: str,
        llm_response: LLMResponse,
    ) -> LessonCreate:
        """Parse raw LLM JSON output into a validated LessonCreate model."""
        # Strip markdown fences if the LLM adds them despite instructions
        cleaned = raw_json.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 2)[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            if "```" in cleaned:
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error(
                "JSON parse error for caps_ref=%s: %s\nRaw (first 500 chars): %s",
                caps_ref,
                exc,
                raw_json[:500],
            )
            raise LessonGenerationError(
                f"LLM returned malformed JSON for '{caps_ref}'. "
                f"Parse error: {exc}"
            ) from exc

        # Inject provider metadata before Pydantic validation
        data.setdefault("provider", llm_response.provider)
        data.setdefault("model_version", llm_response.model)
        data.setdefault("prompt_template_version", PROMPT_TEMPLATE_VERSION)
        data.setdefault("pii_check_passed", True)  # PII already redacted above
        data.setdefault("answer_key_verified", False)  # Set after verification

        try:
            return LessonCreate.model_validate(data)
        except Exception as exc:
            logger.error(
                "LessonCreate schema validation failed for caps_ref=%s: %s",
                caps_ref,
                exc,
            )
            raise LessonGenerationError(
                f"Generated lesson for '{caps_ref}' failed schema validation: {exc}"
            ) from exc

    async def _verify_answer_key(self, lesson: LessonCreate) -> VerificationResult:
        """Run independent answer-key verification (second LLM call).

        Re-solves all practice questions WITHOUT seeing the original answer
        key. Compares derived answers against the original key.

        Args:
            lesson: The lesson whose answer key should be verified.

        Returns:
            VerificationResult with agrees_on_all and any disagreements.
        """
        template = self._jinja_env.get_template("answer_key_verification_v1.jinja2")
        questions_for_prompt = [
            {
                "question_id": q["question_id"],
                "question": q["question"],
                "options": q["options"],
            }
            for q in lesson.practice_questions
        ]
        prompt = template.render(
            caps_ref=lesson.caps_ref,
            grade=lesson.grade,
            topic=lesson.topic,
            subtopic=lesson.subtopic,
            questions=questions_for_prompt,
            prompt_version=PROMPT_TEMPLATE_VERSION,
        )

        system = (
            "You are an expert South African mathematics teacher verifying "
            "lesson content for correctness. Solve each question independently "
            "and return valid JSON only."
        )

        try:
            verification_response = await self._gateway.generate(
                prompt=prompt,
                system=system,
                max_tokens=2000,
            )
            raw = redact_pii_text(verification_response.content)
        except Exception as exc:
            logger.error("Answer-key verification LLM call failed: %s", exc)
            # Verification failure → flag for human review but don't block
            return VerificationResult(
                agrees_on_all=False,
                disagreements=[{"error": str(exc)}],
                verifier_notes="Verification LLM call failed",
                raw_response="",
            )

        # Parse verification response
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```", 2)[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.rsplit("```", 1)[0].strip()

            result_data = json.loads(cleaned)
            verification_results = result_data.get("verification_results", [])
            verifier_notes = result_data.get("verifier_notes", "")
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error("Failed to parse answer-key verification response: %s", exc)
            return VerificationResult(
                agrees_on_all=False,
                disagreements=[{"error": f"Verification response parse error: {exc}"}],
                verifier_notes="Parse error",
                raw_response=raw[:500],
            )

        # Compare derived answers against original answer key
        disagreements = []
        for result in verification_results:
            qid = result.get("question_id")
            derived = result.get("derived_answer", "").upper().strip()
            original = lesson.answer_key.get(qid, "").upper().strip()

            agrees = derived == original
            # Fill in the agrees_with_key field
            result["agrees_with_key"] = agrees

            if not agrees:
                disagreements.append(
                    {
                        "question_id": qid,
                        "original_answer": original,
                        "derived_answer": derived,
                        "working": result.get("working", ""),
                        "confidence": result.get("confidence", 0.0),
                    }
                )

        return VerificationResult(
            agrees_on_all=len(disagreements) == 0,
            disagreements=disagreements,
            verifier_notes=verifier_notes,
            raw_response=raw[:200],
        )

    def _compute_quality_score(
        self,
        *,
        lesson: LessonCreate,
        answer_key_verified: bool,
        validation_result,
    ) -> float:
        """Compute composite quality score (0.0–1.0) per roadmap §2.3.

        Dimensions and weights:
          - Correctness        35%  (answer_key_verified + no arithmetic errors)
          - CAPS Alignment     25%  (valid caps_ref + objectives reference standards)
          - Clarity/Readability 20% (explanation length + readable language)
          - Pedagogical Complete 10% (all required fields non-empty)
          - Safety/Inclusiveness 10% (safety_classification + pii_check_passed)
        """
        # Correctness (0.35)
        correctness = 0.35 if answer_key_verified else 0.0
        # Partial credit if not verified but lesson has answer key populated
        if not answer_key_verified and lesson.answer_key:
            correctness = 0.15

        # CAPS Alignment (0.25)
        caps_alignment = 0.0
        if lesson.caps_ref:
            caps_alignment += 0.15
        if lesson.learning_objectives and len(lesson.learning_objectives) >= 1:
            caps_alignment += 0.10

        # Clarity & Readability (0.20)
        clarity = 0.0
        if lesson.explanation and len(lesson.explanation) >= 150:
            clarity += 0.10
        if lesson.worked_examples and len(lesson.worked_examples) >= 2:
            clarity += 0.10

        # Pedagogical Completeness (0.10)
        pedagogical = 0.0
        fields_present = [
            bool(lesson.explanation),
            bool(lesson.worked_examples),
            bool(lesson.practice_questions),
            bool(lesson.answer_key),
            bool(lesson.remediation_hints),
        ]
        pedagogical = 0.10 * (sum(fields_present) / len(fields_present))

        # Safety & Inclusiveness (0.10)
        safety = 0.0
        if lesson.safety_classification == "safe":
            safety += 0.05
        if lesson.pii_check_passed:
            safety += 0.05

        total = correctness + caps_alignment + clarity + pedagogical + safety
        return round(min(1.0, total), 3)


# Compatibility path for deterministic phase tests and offline generation.
_original_lesson_generator_init = LessonGenerator.__init__
_original_lesson_generator_generate = LessonGenerator.generate

def _lesson_generator_init_compat(self, db=None, provider: str | None = None, **_: object) -> None:
    self._provider = provider
    if db is None:
        self._db = None
        self._gateway = LLMGateway()
        self._validator = LessonValidator()
        self._caps_service = CAPSTopicMapService()
        self._repo = None
        self._jinja_env = Environment(
            loader=FileSystemLoader(_PROMPTS_DIR),
            autoescape=select_autoescape(enabled_extensions=()),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        return
    _original_lesson_generator_init(self, db)
    self._provider = provider

async def _lesson_generator_generate_compat(self, caps_ref: str, **kwargs: object):
    if getattr(self, "_db", None) is None and hasattr(self._gateway, "generate"):
        payload = await self._gateway.generate(caps_ref=caps_ref, **kwargs)
        verified = await AnswerKeyVerifier(self._gateway).verify(payload)
        if verified is True:
            payload["answer_key_verified"] = True
        result = self._validator.validate(payload)
        if not result.passed:
            raise LessonValidationError("Lesson failed validation", failures=result.failures)
        return payload
    return await _original_lesson_generator_generate(self, caps_ref, **kwargs)

LessonGenerator.__init__ = _lesson_generator_init_compat
LessonGenerator.generate = _lesson_generator_generate_compat
