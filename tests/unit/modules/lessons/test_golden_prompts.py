# tests/unit/modules/lessons/test_golden_prompts.py
#
# L5-03 — EduBoost SA Phase 5
# Golden prompt tests: for each of the 3 launch caps_refs, a fixture lesson
# is generated with the mock provider and all validators pass.
# Fails CI if any golden test degrades.
#
# Run with:  pytest tests/unit/modules/lessons/test_golden_prompts.py -v
#
# The mock provider (L2-07) returns deterministic fixture JSON so these tests
# never make real LLM calls. They validate the pipeline logic, the validator
# rules, and the schema contract — not the LLM output itself.

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from app.modules.lessons.lesson_generator import LessonGenerator
from app.modules.lessons.lesson_validator import LessonValidator, ValidationResult
from app.modules.lessons.caps_topic_map_service import CapsTopicMapService

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "golden_lessons"
LAUNCH_CAPS_REFS = ["4.M.1.1", "4.M.1.2", "4.M.1.3"]

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _make_golden_lesson(caps_ref: str, **overrides: Any) -> dict[str, Any]:
    """Return a minimal, fully-valid lesson fixture for the given caps_ref."""
    grade, subject, term, topic_idx = caps_ref.split(".")
    base: dict[str, Any] = {
        "lesson_id": str(uuid.uuid4()),
        "caps_ref": caps_ref,
        "grade": int(grade),
        "subject": "Mathematics",
        "term": int(term),
        "topic": f"Topic {topic_idx}",
        "subtopic": f"Subtopic {topic_idx}.1",
        "learning_objectives": [
            "Learners can identify place values up to 4-digit numbers.",
            "Learners can order and compare 4-digit numbers.",
        ],
        "explanation": (
            "A 4-digit number has thousands, hundreds, tens and ones. "
            "The number 3 452 means 3 thousands, 4 hundreds, 5 tens and 2 ones. "
            "We write it in a place-value table to compare numbers easily."
        ),
        "worked_examples": [
            {
                "question": "What is the value of the digit 5 in 3 452?",
                "step_by_step_solution": (
                    "Step 1: Write the number in a place-value table.\n"
                    "Step 2: Find the column for the digit 5.\n"
                    "Step 3: The digit 5 is in the tens column.\n"
                    "Answer: 5 tens = 50."
                ),
                "answer": "50",
            },
            {
                "question": "Which is bigger: 4 201 or 4 021?",
                "step_by_step_solution": (
                    "Step 1: Both numbers have 4 thousands — equal.\n"
                    "Step 2: Compare hundreds: 4 201 has 2 hundreds, 4 021 has 0 hundreds.\n"
                    "Step 3: 2 hundreds > 0 hundreds.\n"
                    "Answer: 4 201 is bigger."
                ),
                "answer": "4 201",
            },
        ],
        "practice_questions": [
            {
                "id": "pq1",
                "question": "What is the value of the digit 7 in 2 730?",
                "options": {"A": "7", "B": "70", "C": "700", "D": "7 000"},
                "correct_answer": "C",
                "explanation": "The digit 7 is in the hundreds column, so its value is 700.",
            },
            {
                "id": "pq2",
                "question": "Which number is the smallest: 1 023, 1 203, 1 032, 1 302?",
                "options": {"A": "1 023", "B": "1 203", "C": "1 032", "D": "1 302"},
                "correct_answer": "A",
                "explanation": "Compare hundreds: 1 023 has 0 hundreds — the smallest.",
            },
            {
                "id": "pq3",
                "question": "Complete: 3 000 + ___ + 40 + 5 = 3 645",
                "options": {"A": "6", "B": "60", "C": "600", "D": "6 000"},
                "correct_answer": "C",
                "explanation": "The missing value is in the hundreds column: 600.",
            },
        ],
        "answer_key": {"pq1": "C", "pq2": "A", "pq3": "C"},
        "remediation_hints": [
            {
                "misconception_tag": "place_value_confusion",
                "hint_text": "Remember: each column has a different value. The tens column is 10 times bigger than the ones column.",
                "example": "In 54, the digit 5 means 5 tens = 50, not just 5.",
            }
        ],
        "difficulty_level": "on_level",
        "language_level": "Grade 4",
        "safety_classification": "safe",
        "pii_check_passed": True,
        "answer_key_verified": True,
        "quality_score": 0.88,
        "review_status": "ai_generated",
        "reviewer_id": None,
        "reviewed_at": None,
        "prompt_template_version": "lesson_generation_v1",
        "provider": "mock",
        "model_version": "mock-deterministic-v1",
        "generation_latency_ms": 850,
        "token_usage": {"prompt_tokens": 512, "completion_tokens": 890, "total_tokens": 1402},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    base.update(overrides)
    return base


@pytest.fixture(scope="module")
def caps_map_service() -> CapsTopicMapService:
    """Load the real Grade 4 Maths CAPS topic map."""
    return CapsTopicMapService()


@pytest.fixture(scope="module")
def validator(caps_map_service: CapsTopicMapService) -> LessonValidator:
    return LessonValidator(caps_topic_map_service=caps_map_service)


# ---------------------------------------------------------------------------
# Parametrised golden tests — one per launch caps_ref
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
def test_golden_lesson_passes_all_validators(
    caps_ref: str,
    validator: LessonValidator,
) -> None:
    """
    L5-03: a golden fixture lesson for each launch caps_ref passes all 8
    validator rules.  Fails CI if schema, CAPS alignment, or safety
    rules have regressed.
    """
    lesson = _make_golden_lesson(caps_ref)
    result: ValidationResult = validator.validate(lesson)

    assert result.is_valid, (
        f"Golden lesson for {caps_ref} FAILED validation.\n"
        f"Failed rules: {result.failed_rules}\n"
        f"Details: {json.dumps(result.details, indent=2)}"
    )
    assert len(result.failed_rules) == 0, (
        f"Expected 0 failed rules, got: {result.failed_rules}"
    )


@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
def test_golden_lesson_quality_score_meets_threshold(
    caps_ref: str,
    validator: LessonValidator,
) -> None:
    """Golden lessons must score ≥0.7 to avoid auto-queuing for human review."""
    lesson = _make_golden_lesson(caps_ref)
    result: ValidationResult = validator.validate(lesson)
    assert result.quality_score is not None
    assert result.quality_score >= 0.7, (
        f"Golden lesson for {caps_ref} quality_score={result.quality_score:.3f} "
        f"is below the 0.70 review threshold."
    )


@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
def test_golden_lesson_answer_key_verified(caps_ref: str) -> None:
    """answer_key_verified must always be True on a golden lesson."""
    lesson = _make_golden_lesson(caps_ref)
    assert lesson["answer_key_verified"] is True, (
        f"Golden lesson for {caps_ref} has answer_key_verified=False."
    )


@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
def test_golden_lesson_caps_ref_resolves(
    caps_ref: str,
    caps_map_service: CapsTopicMapService,
) -> None:
    """The golden caps_ref must resolve against the canonical topic map."""
    assert caps_map_service.is_valid_ref(caps_ref), (
        f"caps_ref {caps_ref} does not resolve in the canonical CAPS topic map."
    )


# ---------------------------------------------------------------------------
# Regression guard: altering explanation to empty must trigger failure
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
def test_golden_regression_empty_explanation_fails(
    caps_ref: str,
    validator: LessonValidator,
) -> None:
    """
    Regression guard: a previously-passing golden lesson that loses its
    explanation must now fail validation. This guards against silent
    regressions after prompt template changes.
    """
    broken_lesson = _make_golden_lesson(caps_ref, explanation="")
    result = validator.validate(broken_lesson)
    assert not result.is_valid, (
        f"Expected validation failure for empty explanation in {caps_ref} "
        f"but validator passed."
    )
    assert "explanation_non_empty" in result.failed_rules, (
        f"Expected 'explanation_non_empty' rule failure, got: {result.failed_rules}"
    )


@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
def test_golden_regression_unverified_answer_key_fails(
    caps_ref: str,
    validator: LessonValidator,
) -> None:
    """answer_key_verified=False on a previously-approved lesson must fail."""
    broken_lesson = _make_golden_lesson(caps_ref, answer_key_verified=False)
    result = validator.validate(broken_lesson)
    assert not result.is_valid
    assert "answer_key_verified" in result.failed_rules


@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
def test_golden_regression_invalid_caps_ref_fails(
    caps_ref: str,
    validator: LessonValidator,
) -> None:
    """A bogus CAPS ref must fail caps_ref_resolves rule."""
    broken_lesson = _make_golden_lesson(caps_ref)
    broken_lesson["caps_ref"] = "9.X.9.9"
    result = validator.validate(broken_lesson)
    assert not result.is_valid
    assert "caps_ref_resolves" in result.failed_rules


# ---------------------------------------------------------------------------
# Mock-provider integration: generator produces a lesson that passes validators
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
async def test_mock_provider_pipeline_passes_validation(
    caps_ref: str,
    validator: LessonValidator,
) -> None:
    """
    L5-03 (pipeline): run the full lesson_generator with the mock provider.
    The generated lesson must pass all validators without error.
    """
    fixture_lesson = _make_golden_lesson(caps_ref)

    with (
        patch(
            "app.modules.lessons.lesson_generator.LLMGateway.generate",
            new_callable=AsyncMock,
            return_value=fixture_lesson,
        ),
        patch(
            "app.modules.lessons.lesson_generator.LessonRepository.create",
            new_callable=AsyncMock,
            return_value=fixture_lesson,
        ),
        patch(
            "app.modules.lessons.lesson_generator.AnswerKeyVerifier.verify",
            new_callable=AsyncMock,
            return_value=True,
        ),
    ):
        generator = LessonGenerator(provider="mock")
        lesson_response = await generator.generate(
            caps_ref=caps_ref,
            difficulty="on_level",
            misconception_tags=[],
        )

    result = validator.validate(lesson_response if isinstance(lesson_response, dict) else lesson_response.dict())
    assert result.is_valid, (
        f"Mock-provider pipeline output for {caps_ref} failed validation: "
        f"{result.failed_rules}"
    )
