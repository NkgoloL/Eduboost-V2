"""
EduBoost V2 — Judiciary Service (Pillar 3)
Strict schema enforcement + constitutional policy gate.
All AI output MUST pass through the Judiciary Stamp before being returned.
"""
from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, ValidationError

from app.core.logging import get_logger

log = get_logger(__name__)

# ── Pydantic schemas the AI must conform to ───────────────────────────────────


class LessonPayload(BaseModel):
    title: str
    introduction: str
    main_content: str
    worked_example: str
    practice_question: str
    answer: str
    cultural_hook: str  # SA-relevant context


class StudyPlanPayload(BaseModel):
    week_label: str
    daily_topics: list[str]
    priority_gaps: list[str]


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
        payload = self._parse_json(raw_output)
        self._assert_no_violations(raw_output)
        try:
            return LessonPayload(**payload)
        except ValidationError as exc:
            log.warning("judiciary_lesson_invalid", errors=exc.errors())
            raise ConstitutionalViolation(f"Lesson schema violation: {exc}") from exc

    def stamp_study_plan(self, raw_output: str) -> StudyPlanPayload:
        payload = self._parse_json(raw_output)
        self._assert_no_violations(raw_output)
        try:
            return StudyPlanPayload(**payload)
        except ValidationError as exc:
            raise ConstitutionalViolation(f"StudyPlan schema violation: {exc}") from exc

    def _parse_json(self, text: str) -> dict[str, Any]:
        # Strip markdown fences if present
        clean = re.sub(r"```(?:json)?|```", "", text).strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError as exc:
            raise ConstitutionalViolation(f"LLM did not return valid JSON: {exc}") from exc

    def _assert_no_violations(self, text: str) -> None:
        if _BLOCKED_PATTERNS.search(text):
            raise ConstitutionalViolation("Content policy violation detected in AI output")
