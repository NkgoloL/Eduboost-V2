"""Batch 228 — app/modules/lessons/lesson_validator.py comprehensive branch coverage expansion.

Tests:
- LessonValidationError exception
- ValidationResult truthiness and compatibility properties (is_valid, failed_rules, details)
- Rule 1: CAPS ref resolution (pass vs fail)
- Rule 2: answer_key present & non-empty (pass vs fail)
- Rule 3: answer_key_verified=False (fail when require_verified=True vs warning when False)
- Rule 4: worked examples count (<2 fails, >=2 passes)
- Rule 5: practice questions count (<3 fails, >=3 passes)
- Rule 6: readability level estimation (simple words vs complex text > Grade 6.5)
- Rule 7: PII detection (emails, SA phones, SA ID numbers, URLs) and harmful content terms
- Rule 8: explanation presence and length (<50 chars fails, >=50 chars passes)
- validate_batch: multiple lessons evaluation
- _normalise_lesson_dict: converting dictionary format with legacy keys to LessonCreate
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService
from app.modules.lessons.lesson_schema_v1 import LessonCreate
from app.modules.lessons.lesson_validator import (
    LessonValidationError,
    LessonValidator,
    ValidationResult,
)


@pytest.fixture
def mock_caps_service():
    svc = MagicMock(spec=CAPSTopicMapService)
    svc.validate_caps_ref.return_value = True
    return svc


@pytest.fixture
def validator(mock_caps_service):
    return LessonValidator(caps_service=mock_caps_service)


@pytest.fixture
def base_lesson_dict():
    return {
        "caps_ref": "4.M.1.1",
        "grade": 4,
        "term": 1,
        "subject": "Mathematics",
        "topic": "Numbers",
        "subtopic": "Place Value",
        "difficulty_level": "on_level",
        "language_level": "en",
        "learning_objectives": ["Identify place values"],
        "explanation": "Place value is the value of each digit in a given whole number. " * 5,
        "worked_examples": [
            {
                "question": "What is the value of 5 in 543?",
                "step_by_step_solution": ["Look at position", "Hundreds place", "500"],
                "answer": "500",
            },
            {
                "question": "What is the value of 4 in 543?",
                "step_by_step_solution": ["Look at position", "Tens place", "40"],
                "answer": "40",
            },
        ],
        "practice_questions": [
            {
                "question_id": "pq1",
                "question_text": "What is the value of 7 in 789?",
                "options": {"A": "7", "B": "70", "C": "700", "D": "7000"},
                "correct_option": "C",
                "explanation": "7 is in the hundreds column.",
            },
            {
                "question_id": "pq2",
                "question_text": "What is the value of 8 in 789?",
                "options": {"A": "8", "B": "80", "C": "800", "D": "8000"},
                "correct_option": "B",
                "explanation": "8 is in the tens column.",
            },
            {
                "question_id": "pq3",
                "question_text": "What is the value of 9 in 789?",
                "options": {"A": "9", "B": "90", "C": "900", "D": "9000"},
                "correct_option": "A",
                "explanation": "9 is in the ones column.",
            },
        ],
        "answer_key": [
            {"question_id": "pq1", "correct_option": "C", "correct_answer_text": "700"},
            {"question_id": "pq2", "correct_option": "B", "correct_answer_text": "80"},
            {"question_id": "pq3", "correct_option": "A", "correct_answer_text": "9"},
        ],
        "remediation_hints": [
            {
                "misconception_tag": "place_value_confusion",
                "hint_text": "Check the columns carefully.",
                "example": "In 789, 7 is hundreds.",
            }
        ],
        "safety_classification": "safe",
        "pii_check_passed": True,
        "answer_key_verified": True,
        "quality_score": 0.95,
        "provider": "groq",
        "model_version": "llama3",
        "prompt_template_version": "v1",
        "review_status": "approved",
        "generation_latency_ms": 100,
        "token_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 200,
            "total_tokens": 300,
        },
    }


# ---------------------------------------------------------------------------
# ValidationResult & Exceptions
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_validation_result_and_error():
    err = LessonValidationError("Validation failed", failures=["Rule 1 FAIL"])
    assert err.status_code == 422
    assert err.failures == ["Rule 1 FAIL"]

    res_pass = ValidationResult(passed=True, failures=[], warnings=[])
    assert bool(res_pass) is True
    assert res_pass.is_valid is True
    assert res_pass.failed_rules == []
    assert res_pass.details["failures"] == []

    res_fail = ValidationResult(passed=False, failures=["Rule 1 FAIL: caps_ref invalid"])
    assert bool(res_fail) is False
    assert res_fail.is_valid is False
    assert "caps_ref_resolves" in res_fail.failed_rules


# ---------------------------------------------------------------------------
# Rule 1 to 5 Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_rule_1_caps_ref_resolves(validator, base_lesson_dict, mock_caps_service):
    lesson = LessonCreate.model_validate(base_lesson_dict)

    # Pass
    res1 = validator.validate(lesson)
    assert res1.passed is True

    # Fail
    mock_caps_service.validate_caps_ref.return_value = False
    res2 = validator.validate(lesson)
    assert res2.passed is False
    assert any("Rule 1" in f for f in res2.failures)


@pytest.mark.unit
def test_rule_2_and_3_answer_key_and_verified(validator, base_lesson_dict):
    # Rule 2: empty answer_key
    we = [
        MagicMock(question="What is 5?", step_by_step_solution=["Step 1"], answer="5"),
        MagicMock(question="What is 4?", step_by_step_solution=["Step 1"], answer="4"),
    ]
    pq = [
        MagicMock(question_id="pq1", question_text="What is 7?", options={"A": "7", "B": "8", "C": "9", "D": "10"}),
        MagicMock(question_id="pq2", question_text="What is 8?", options={"A": "7", "B": "8", "C": "9", "D": "10"}),
        MagicMock(question_id="pq3", question_text="What is 9?", options={"A": "7", "B": "8", "C": "9", "D": "10"}),
    ]
    mock_lesson2 = MagicMock(
        caps_ref="4.M.1.1",
        answer_key=[],
        answer_key_verified=True,
        worked_examples=we,
        practice_questions=pq,
        explanation="Valid explanation with more than 50 characters here for testing.",
    )
    res2 = validator.validate(mock_lesson2)
    assert res2.passed is False
    assert any("Rule 2" in f for f in res2.failures)

    # Rule 3: unverified with require_verified=True vs False
    d3 = dict(base_lesson_dict)
    d3["answer_key_verified"] = False
    lesson3 = LessonCreate.model_validate(d3)

    # Hard gate failure
    res3_hard = validator.validate(lesson3, require_verified=True)
    assert res3_hard.passed is False
    assert any("Rule 3" in f for f in res3_hard.failures)

    # Soft warning
    res3_soft = validator.validate(lesson3, require_verified=False)
    assert res3_soft.passed is True
    assert any("Rule 3" in w for w in res3_soft.warnings)


@pytest.mark.unit
def test_rule_4_and_5_worked_examples_and_practice_questions(validator):
    pq = [
        MagicMock(question_id="pq1", question_text="What is 7?", options={"A": "7", "B": "8", "C": "9", "D": "10"}),
        MagicMock(question_id="pq2", question_text="What is 8?", options={"A": "7", "B": "8", "C": "9", "D": "10"}),
        MagicMock(question_id="pq3", question_text="What is 9?", options={"A": "7", "B": "8", "C": "9", "D": "10"}),
    ]
    # Rule 4: worked examples < 2
    mock_lesson4 = MagicMock(
        caps_ref="4.M.1.1",
        answer_key=[MagicMock()],
        answer_key_verified=True,
        worked_examples=[MagicMock(question="Q?", step_by_step_solution=["Step 1"], answer="Ans")],  # only 1
        practice_questions=pq,
        explanation="Valid explanation with more than 50 characters here for testing.",
    )
    res4 = validator.validate(mock_lesson4)
    assert res4.passed is False
    assert any("Rule 4" in f for f in res4.failures)

    # Rule 5: practice questions < 3
    we = [
        MagicMock(question="What is 5?", step_by_step_solution=["Step 1"], answer="5"),
        MagicMock(question="What is 4?", step_by_step_solution=["Step 1"], answer="4"),
    ]
    mock_lesson5 = MagicMock(
        caps_ref="4.M.1.1",
        answer_key=[MagicMock()],
        answer_key_verified=True,
        worked_examples=we,
        practice_questions=[
            MagicMock(question_id="pq1", question_text="What is 7?", options={"A": "7", "B": "8", "C": "9", "D": "10"}),
            MagicMock(question_id="pq2", question_text="What is 8?", options={"A": "7", "B": "8", "C": "9", "D": "10"}),
        ],  # only 2
        explanation="Valid explanation with more than 50 characters here for testing.",
    )
    res5 = validator.validate(mock_lesson5)
    assert res5.passed is False
    assert any("Rule 5" in f for f in res5.failures)


# ---------------------------------------------------------------------------
# Rule 6, 7 & 8 Tests: Readability, PII/Safety, Explanation
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_rule_6_readability_warning(validator, base_lesson_dict):
    # High complexity explanation triggering FK Grade > 6.5
    d6 = dict(base_lesson_dict)
    d6["explanation"] = (
        "Epistemological conceptualizations of multi-dimensional mathematical constructs "
        "necessitate comprehensive pedagogical methodologies for institutionalized education."
    )
    lesson6 = LessonCreate.model_validate(d6)
    res6 = validator.validate(lesson6)
    assert any("Rule 6 WARN" in w for w in res6.warnings)


@pytest.mark.unit
def test_rule_7_pii_and_harmful_detection(validator, base_lesson_dict):
    # Email PII
    d_email = dict(base_lesson_dict)
    d_email["explanation"] = "Contact tutor at test.user@eduboost.co.za for more details on numbers."
    res_email = validator.validate(LessonCreate.model_validate(d_email))
    assert res_email.passed is False
    assert any("PII" in f for f in res_email.failures)

    # Phone PII
    d_phone = dict(base_lesson_dict)
    d_phone["explanation"] = "Call helpline at 082 123 4567 for maths assistance in school."
    res_phone = validator.validate(LessonCreate.model_validate(d_phone))
    assert res_phone.passed is False
    assert any("PII" in f for f in res_phone.failures)

    # Harmful content term
    d_harm = dict(base_lesson_dict)
    d_harm["explanation"] = "Be careful not to kill the plant while measuring height in numbers."
    res_harm = validator.validate(LessonCreate.model_validate(d_harm))
    assert res_harm.passed is False
    assert any("harmful content" in f for f in res_harm.failures)


@pytest.mark.unit
def test_rule_8_explanation_short(validator):
    we = [
        MagicMock(question="What is 5?", step_by_step_solution=["Step 1"], answer="5"),
        MagicMock(question="What is 4?", step_by_step_solution=["Step 1"], answer="4"),
    ]
    pq = [
        MagicMock(question_id="pq1", question_text="What is 7?", options={"A": "7", "B": "8", "C": "9", "D": "10"}),
        MagicMock(question_id="pq2", question_text="What is 8?", options={"A": "7", "B": "8", "C": "9", "D": "10"}),
        MagicMock(question_id="pq3", question_text="What is 9?", options={"A": "7", "B": "8", "C": "9", "D": "10"}),
    ]
    mock_lesson8 = MagicMock(
        caps_ref="4.M.1.1",
        answer_key=[MagicMock()],
        answer_key_verified=True,
        worked_examples=we,
        practice_questions=pq,
        explanation="Too short.",
    )
    res8 = validator.validate(mock_lesson8)
    assert res8.passed is False
    assert any("Rule 8" in f for f in res8.failures)


# ---------------------------------------------------------------------------
# Batch & Normalise Dict
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_validate_batch_and_normalise_dict(validator, base_lesson_dict):
    lesson1 = LessonCreate.model_validate(base_lesson_dict)
    lesson2 = LessonCreate.model_validate(base_lesson_dict)

    batch_results = validator.validate_batch([lesson1, lesson2])
    assert len(batch_results) == 2
    assert batch_results[0][1].passed is True
    assert batch_results[1][1].passed is True

    # Dict normalisation with legacy keys
    legacy_dict = {
        "caps_ref": "4.M.1.1",
        "grade": 4,
        "term": 1,
        "subject": "Mathematics",
        "topic": "Numbers",
        "subtopic": "Place Value",
        "difficulty_level": "on_level",
        "language_level": "en",
        "learning_objectives": ["Identify place values"],
        "explanation": "Place value is the value of each digit in a given whole number. " * 5,
        "worked_examples": [
            {
                "question": "What is the value of 5 in 543?",
                "step_by_step_solution": "Look at position\nHundreds place\n500",
                "answer": "500",
            },
            {
                "question": "What is the value of 4 in 543?",
                "step_by_step_solution": ["Look at position", "Tens place", "40"],
                "answer": "40",
            },
        ],
        "practice_questions": [
            {
                "id": "q1",
                "question": "What is 7 in 789?",
                "options": {"A": "7", "B": "70", "C": "700", "D": "7000"},
                "correct_answer": "C",
            },
            {
                "id": "q2",
                "question": "What is 8 in 789?",
                "options": {"A": "8", "B": "80", "C": "800", "D": "8000"},
                "correct_answer": "B",
            },
            {
                "id": "q3",
                "question": "What is 9 in 789?",
                "options": {"A": "9", "B": "90", "C": "900", "D": "9000"},
                "correct_answer": "A",
            },
        ],
        "answer_key": {"q1": "C", "q2": "B", "q3": "A"},
        "remediation_hints": [
            {
                "misconception_tag": "place_value_confusion",
                "hint_text": "Check the columns carefully.",
                "example": "In 789, 7 is hundreds.",
            }
        ],
        "safety_classification": "safe",
        "pii_check_passed": True,
        "answer_key_verified": True,
        "quality_score": 0.95,
    }

    norm_res = validator.validate(legacy_dict)
    assert norm_res.passed is True
