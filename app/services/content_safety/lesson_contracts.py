"""Structured lesson output, CAPS map, and validation contract."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .pii import contains_pii

CAPS_TOPIC_MAP: tuple[dict[str, Any], ...] = (
    {
        "phase": "intermediate",
        "grade": 4,
        "subject": "Mathematics",
        "term": 1,
        "topic": "Numbers, operations and relationships",
        "subtopic": "Fractions",
        "prerequisites": ["whole numbers", "sharing equally"],
        "assessment_standards": ["compare common fractions", "solve fraction word problems"],
    },
    {
        "phase": "intermediate",
        "grade": 5,
        "subject": "Mathematics",
        "term": 2,
        "topic": "Patterns, functions and algebra",
        "subtopic": "Number patterns",
        "prerequisites": ["skip counting", "multiplication facts"],
        "assessment_standards": ["describe rules", "extend numeric patterns"],
    },
    {
        "phase": "senior",
        "grade": 7,
        "subject": "Natural Sciences",
        "term": 3,
        "topic": "Energy and change",
        "subtopic": "Electric circuits",
        "prerequisites": ["energy transfer", "conductors and insulators"],
        "assessment_standards": ["draw simple circuits", "explain open and closed circuits"],
    },
)

SUPPORTED_LANGUAGES = ("English", "isiZulu", "Afrikaans", "isiXhosa")
SUPPORTED_VARIANTS = ("standard", "visual", "story_based", "step_by_step", "exam_style", "real_world_sa")
UNSAFE_TERMS = re.compile(r"\b(explicit|gambling|hate|weapon|drug|self-harm)\b", re.I)


@dataclass(frozen=True, slots=True)
class LessonOutput:
    topic: str
    grade: int
    subject: str
    caps_reference: str
    objectives: list[str]
    explanation: str
    worked_examples: list[str]
    practice_questions: list[str]
    answer_key: list[str]
    remediation_hints: list[str]
    difficulty: str
    language_level: str
    safety_classification: str
    alignment_confidence: float
    quality_score: float


@dataclass(frozen=True, slots=True)
class LessonValidationResult:
    accepted: bool
    reasons: tuple[str, ...]


def caps_topic_exists(*, grade: int, subject: str, topic: str) -> bool:
    return any(
        item["grade"] == grade
        and item["subject"].casefold() == subject.casefold()
        and item["topic"].casefold() == topic.casefold()
        for item in CAPS_TOPIC_MAP
    )


def _answer_key_consistent(lesson: LessonOutput) -> bool:
    return bool(lesson.answer_key) and len(lesson.answer_key) >= len(lesson.practice_questions)


def arithmetic_expression_is_correct(expression: str, expected: str) -> bool:
    """Small arithmetic validator for generated examples such as '2 + 3' -> '5'."""
    if not re.fullmatch(r"[0-9\s+\-*/().]+", expression):
        return False
    try:
        return abs(float(eval(expression, {"__builtins__": {}}, {})) - float(expected)) < 1e-9
    except Exception:
        return False


def validate_lesson_output(lesson: LessonOutput) -> LessonValidationResult:
    reasons: list[str] = []
    if not lesson.topic:
        reasons.append("topic missing")
    if not caps_topic_exists(grade=lesson.grade, subject=lesson.subject, topic=lesson.topic):
        reasons.append("CAPS alignment invalid")
    if lesson.safety_classification != "safe" or UNSAFE_TERMS.search(lesson.explanation):
        reasons.append("unsafe content")
    joined = " ".join(
        [lesson.explanation]
        + lesson.objectives
        + lesson.worked_examples
        + lesson.practice_questions
        + lesson.answer_key
        + lesson.remediation_hints
    )
    if contains_pii(joined):
        reasons.append("PII detected")
    if not lesson.explanation.strip():
        reasons.append("explanation missing")
    if not _answer_key_consistent(lesson):
        reasons.append("answer key missing or inconsistent")
    if lesson.alignment_confidence < 0.7:
        reasons.append("low alignment confidence")
    if lesson.quality_score < 0.7:
        reasons.append("low quality score")
    return LessonValidationResult(accepted=not reasons, reasons=tuple(reasons))
