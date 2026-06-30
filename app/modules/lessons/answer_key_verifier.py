"""
EduBoost SA — Phase 2 (L2-03)
Answer-Key Verifier

Orchestrates the second, independent LLM call that re-solves every practice
question in a generated lesson WITHOUT seeing the original answer key.

If any question's derived answer disagrees with the key, the lesson is flagged
for human review rather than being accepted.

Usage (called from lesson_generator.py)
---------------------------------------
    verifier = AnswerKeyVerifier(llm_gateway, prompt_loader)
    result = await verifier.verify(lesson_dict)
    if result.all_agree:
        lesson_dict["answer_key_verified"] = True
    else:
        lesson_dict["answer_key_verified"] = False
        lesson_dict["review_status"] = "requires_review"
        lesson_dict["_verification_report"] = result.to_dict()
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE_VERSION = "answer_key_verification_v1"
PROMPTS_DIR = "app/modules/lessons/prompts"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class QuestionVerification:
    question_id: str
    derived_answer: str
    working: str
    confidence: float
    agrees_with_key: bool | None = None  # filled after comparison
    original_answer: str | None = None   # filled after comparison


@dataclass
class VerificationResult:
    lesson_id: str
    all_agree: bool
    verifications: list[QuestionVerification] = field(default_factory=list)
    disagreements: list[dict[str, Any]] = field(default_factory=list)
    verification_model: str = ""
    verification_provider: str = ""
    prompt_template_version: str = PROMPT_TEMPLATE_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "lesson_id": self.lesson_id,
            "all_agree": self.all_agree,
            "prompt_template_version": self.prompt_template_version,
            "verification_model": self.verification_model,
            "verification_provider": self.verification_provider,
            "verifications": [
                {
                    "question_id": v.question_id,
                    "derived_answer": v.derived_answer,
                    "working": v.working,
                    "confidence": v.confidence,
                    "agrees_with_key": v.agrees_with_key,
                    "original_answer": v.original_answer,
                }
                for v in self.verifications
            ],
            "disagreements": self.disagreements,
        }


# ---------------------------------------------------------------------------
# Prompt strip helper — removes correct_answer from questions before rendering
# ---------------------------------------------------------------------------

def _strip_answers_from_questions(
    questions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return a copy of *questions* with answer fields removed.

    This ensures the verification LLM cannot see the original answers.
    """
    stripped = []
    for q in questions:
        clean = {k: v for k, v in q.items() if k not in {
            "correct_answer", "answer", "answer_key", "explanation", "is_correct",
        }}
        # Keep options but mark them without indicating which is correct
        if "options" in clean and isinstance(clean["options"], list):
            clean["options"] = [
                {k2: v2 for k2, v2 in opt.items() if k2 not in {"is_correct", "correct"}}
                for opt in clean["options"]
            ]
        stripped.append(clean)
    return stripped


# ---------------------------------------------------------------------------
# Answer comparison
# ---------------------------------------------------------------------------

def _normalise_answer(answer: str) -> str:
    """Normalise an answer string for comparison (case, whitespace, punctuation)."""
    answer = answer.strip().lower()
    # Normalise decimal separators (SA uses comma; LLM may use period)
    answer = answer.replace(",", ".")
    # Remove trailing zeros after decimal
    try:
        as_float = float(answer)
        if as_float == int(as_float):
            return str(int(as_float))
        return str(round(as_float, 6))
    except ValueError:
        pass
    # Strip common noise
    answer = re.sub(r"[^\w\s./-]", "", answer)
    return re.sub(r"\s+", " ", answer).strip()


def _answers_agree(derived: str, original: str) -> bool:
    """Return True if derived and original answers agree after normalisation."""
    return _normalise_answer(derived) == _normalise_answer(original)


# ---------------------------------------------------------------------------
# AnswerKeyVerifier
# ---------------------------------------------------------------------------

class AnswerKeyVerifier:
    """Verifies a lesson's answer key via a second independent LLM call.

    Parameters
    ----------
    llm_gateway:
        An object exposing ``async complete(prompt: str, **kwargs) -> dict``
        matching the existing EduBoost LLM gateway interface.
    prompts_dir:
        Directory containing Jinja2 prompt templates.
    """

    def __init__(
        self,
        llm_gateway: Any,
        prompts_dir: str = PROMPTS_DIR,
    ) -> None:
        self._gateway = llm_gateway
        self._jinja = Environment(
            loader=FileSystemLoader(prompts_dir),
            autoescape=select_autoescape(disabled_extensions=("jinja2",)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    async def verify(self, lesson: dict[str, Any]) -> VerificationResult:
        """Run the independent answer-key verification call.

        Parameters
        ----------
        lesson:
            Full lesson dict (as returned by the lesson generator).
            Must contain: lesson_id, caps_ref, grade, subject, topic, subtopic,
            practice_questions, answer_key.

        Returns
        -------
        VerificationResult
            If ``result.all_agree`` is False, the caller must set
            ``lesson["answer_key_verified"] = False`` and queue the lesson for
            human review.
        """
        lesson_id = str(lesson.get("lesson_id", "unknown"))
        practice_questions = lesson.get("practice_questions", [])
        answer_key: dict[str, Any] = lesson.get("answer_key") or {}

        if not practice_questions:
            logger.warning("Lesson %s has no practice_questions — skipping verification.", lesson_id)
            return VerificationResult(lesson_id=lesson_id, all_agree=False)

        # Build prompt with answers stripped
        stripped_questions = _strip_answers_from_questions(practice_questions)
        prompt = self._render_prompt(lesson, stripped_questions)

        logger.info(
            "Answer-key verification: calling LLM for lesson %s (%d questions).",
            lesson_id,
            len(stripped_questions),
        )

        try:
            response = await self._gateway.complete(
                prompt=prompt,
                system=(
                    "You are a South African primary-school curriculum expert and "
                    "answer-key auditor. Respond ONLY with a valid JSON array."
                ),
                temperature=0.0,   # deterministic for verification
                max_tokens=2048,
                metadata={"purpose": "answer_key_verification", "lesson_id": lesson_id},
            )
        except Exception as exc:
            logger.error("LLM call failed during answer-key verification for lesson %s: %s", lesson_id, exc)
            return VerificationResult(
                lesson_id=lesson_id,
                all_agree=False,
                disagreements=[{"error": str(exc)}],
            )

        raw_text: str = response.get("content", "") if isinstance(response, dict) else str(response)

        verifications = self._parse_verifier_response(raw_text, lesson_id)
        if not verifications:
            logger.warning("Verifier returned no parseable results for lesson %s.", lesson_id)
            return VerificationResult(lesson_id=lesson_id, all_agree=False)

        # Compare derived answers against original answer key
        disagreements: list[dict[str, Any]] = []
        for v in verifications:
            # Look up original answer: try answer_key dict first, then embedded in question
            original = None
            if isinstance(answer_key, dict):
                original = answer_key.get(v.question_id)
            if original is None:
                # Fall back to answer embedded in the question object
                for q in practice_questions:
                    if isinstance(q, dict):
                        q_id = q.get("question_id") or q.get("id")
                        if str(q_id) == v.question_id:
                            original = q.get("correct_answer") or q.get("answer")
                            break

            v.original_answer = str(original) if original is not None else None

            if v.original_answer is None:
                logger.warning("No original answer found for question %s in lesson %s.", v.question_id, lesson_id)
                v.agrees_with_key = False
                disagreements.append({
                    "question_id": v.question_id,
                    "reason": "original_answer_not_found_in_key",
                    "derived": v.derived_answer,
                })
            else:
                v.agrees_with_key = _answers_agree(v.derived_answer, v.original_answer)
                if not v.agrees_with_key:
                    disagreements.append({
                        "question_id": v.question_id,
                        "derived_answer": v.derived_answer,
                        "original_answer": v.original_answer,
                        "derived_working": v.working,
                        "confidence": v.confidence,
                    })

        all_agree = len(disagreements) == 0

        if all_agree:
            logger.info("Lesson %s: all %d answers verified ✓", lesson_id, len(verifications))
        else:
            logger.warning(
                "Lesson %s: %d/%d answer(s) DISAGREE — flagging for human review.",
                lesson_id,
                len(disagreements),
                len(verifications),
            )

        model_info = response.get("model", "") if isinstance(response, dict) else ""
        provider_info = response.get("provider", "") if isinstance(response, dict) else ""

        return VerificationResult(
            lesson_id=lesson_id,
            all_agree=all_agree,
            verifications=verifications,
            disagreements=disagreements,
            verification_model=model_info,
            verification_provider=provider_info,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _render_prompt(
        self,
        lesson: dict[str, Any],
        stripped_questions: list[dict[str, Any]],
    ) -> str:
        template = self._jinja.get_template(f"{PROMPT_TEMPLATE_VERSION}.jinja2")
        return template.render(
            lesson_id=lesson.get("lesson_id", ""),
            caps_ref=lesson.get("caps_ref", ""),
            grade=lesson.get("grade", ""),
            subject=lesson.get("subject", "Mathematics"),
            topic=lesson.get("topic", ""),
            subtopic=lesson.get("subtopic", ""),
            practice_questions=stripped_questions,
        )

    @staticmethod
    def _parse_verifier_response(
        raw: str,
        lesson_id: str,
    ) -> list[QuestionVerification]:
        """Parse the LLM's JSON array response into QuestionVerification objects."""
        # Strip markdown fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip()

        # Extract the outermost JSON array
        start = raw.find("[")
        end = raw.rfind("]")
        if start == -1 or end == -1:
            logger.error("Verifier response for lesson %s contains no JSON array.", lesson_id)
            return []

        try:
            items: list[dict[str, Any]] = json.loads(raw[start : end + 1])
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse verifier JSON for lesson %s: %s", lesson_id, exc)
            return []

        results: list[QuestionVerification] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            results.append(
                QuestionVerification(
                    question_id=str(item.get("question_id", "")),
                    derived_answer=str(item.get("derived_answer", "")),
                    working=str(item.get("working", "")),
                    confidence=float(item.get("confidence", 0.0)),
                    agrees_with_key=None,  # set by caller after comparison
                )
            )

        return results
