"""
EduBoost V2 — Judiciary Service (Pillar 3)
Strict schema enforcement + constitutional policy gate.
All AI output MUST pass through the Judiciary Stamp before being returned.
"""
from __future__ import annotations

import re

from pydantic import TypeAdapter, ValidationError

from app.domain.llm_schemas import DiagnosticFeedback, LessonContent, StudyPlanContent
from app.core.logging import get_logger

log = get_logger(__name__)

LessonPayload = LessonContent
StudyPlanPayload = StudyPlanContent
DiagnosticFeedbackPayload = DiagnosticFeedback

_LESSON_ADAPTER = TypeAdapter(LessonPayload)
_STUDY_PLAN_ADAPTER = TypeAdapter(StudyPlanPayload)
_DIAGNOSTIC_ADAPTER = TypeAdapter(DiagnosticFeedbackPayload)


# ── Safety word-list (simple constitutional filter) ───────────────────────────
_BLOCKED_PATTERNS = re.compile(
    r"\b(violence|weapon|drug|explicit|adult|gambling|hate|racist)\b",
    re.IGNORECASE,
)


class ConstitutionalViolation(Exception):
    pass


class JudiciaryService:
    """
    Constitutional Pillar 3: The Judiciary.
    Validates all AI output against strict Pydantic schemas and content policy.
    """

    def stamp_lesson(self, raw_output: str) -> LessonPayload:
        """Parse + validate an LLM lesson response. Raises on any violation."""
        self._assert_no_violations(raw_output)
        try:
            return _LESSON_ADAPTER.validate_json(self._clean_json(raw_output))
        except ValidationError as exc:
            log.warning("judiciary_lesson_invalid", errors=exc.errors())
            raise ConstitutionalViolation(f"Lesson schema violation: {exc}") from exc

    def stamp_study_plan(self, raw_output: str) -> StudyPlanPayload:
        self._assert_no_violations(raw_output)
        try:
            return _STUDY_PLAN_ADAPTER.validate_json(self._clean_json(raw_output))
        except ValidationError as exc:
            raise ConstitutionalViolation(f"StudyPlan schema violation: {exc}") from exc

    def stamp_diagnostic_feedback(self, raw_output: str) -> DiagnosticFeedbackPayload:
        self._assert_no_violations(raw_output)
        try:
            return _DIAGNOSTIC_ADAPTER.validate_json(self._clean_json(raw_output))
        except ValidationError as exc:
            raise ConstitutionalViolation(f"Diagnostic feedback schema violation: {exc}") from exc

    def _clean_json(self, text: str) -> str:
        clean = re.sub(r"```(?:json)?|```", "", text).strip()
        if not clean:
            raise ConstitutionalViolation("LLM did not return valid JSON: empty response")
        return clean

    def _assert_no_violations(self, text: str) -> None:
        if _BLOCKED_PATTERNS.search(text):
            raise ConstitutionalViolation("Content policy violation detected in AI output")
