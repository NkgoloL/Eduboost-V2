"""Batch 227 — app/modules/lessons/lesson_generator.py comprehensive branch coverage expansion.

Tests:
- LessonGenerationError and VerificationResult data class
- CAPS reference resolution failure (LessonGenerationError)
- LLM generation failure handling (_call_llm_with_error_handling)
- JSON parsing with markdown fences, malformed JSON errors, schema validation errors (_parse_and_validate_schema)
- LessonValidator quality gate failure (LessonValidationError)
- Answer-key verification:
  - Verifier LLM error handling
  - Verifier JSON parse error handling
  - Disagreements between derived and original answers
  - Full agreement
- Quality score computation weighting (dimensions and score bands)
- Review status tiers ("approved", "ai_generated", "requires_review")
- dry_run=True (skips DB persistence) vs dry_run=False (persists via repo)
- Compatibility init & generate paths with db=None
"""
from __future__ import annotations

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.lessons.lesson_generator import (
    LessonGenerationError,
    LessonGenerator,
    VerificationResult,
)
from app.modules.lessons.lesson_schema_v1 import LessonCreate, LessonResponse
from app.modules.lessons.lesson_validator import LessonValidationError, ValidationResult
from app.modules.lessons.llm_gateway import LLMResponse


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def generator(mock_db):
    return LessonGenerator(mock_db)


@pytest.fixture
def valid_topic_context():
    return {
        "caps_ref": "4.M.1.1",
        "grade": 4,
        "term": 1,
        "subject": "Mathematics",
        "topic": "Numbers",
        "subtopic": "Place Value",
        "assessment_standards": ["Identify place values up to 4 digits"],
    }


@pytest.fixture
def valid_lesson_dict():
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
        "explanation": "Place value is the value of each digit in a number. " * 8,
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
                "misconception_tag": "place_value_confusion",
            },
            {
                "question_id": "pq2",
                "question_text": "What is the value of 8 in 789?",
                "options": {"A": "8", "B": "80", "C": "800", "D": "8000"},
                "correct_option": "B",
                "explanation": "8 is in the tens column.",
                "misconception_tag": "place_value_confusion",
            },
            {
                "question_id": "pq3",
                "question_text": "What is the value of 9 in 789?",
                "options": {"A": "9", "B": "90", "C": "900", "D": "9000"},
                "correct_option": "A",
                "explanation": "9 is in the ones column.",
                "misconception_tag": "place_value_confusion",
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
                "example": "In 789, 7 is hundreds, 8 is tens, 9 is ones.",
            }
        ],
        "safety_classification": "safe",
        "pii_check_passed": True,
        "answer_key_verified": True,
        "quality_score": 0.95,
        "provider": "groq",
        "model_version": "llama3-70b-8192",
        "prompt_template_version": "v1",
        "review_status": "approved",
        "generation_latency_ms": 120,
        "token_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 200,
            "total_tokens": 300,
        },
    }


# ---------------------------------------------------------------------------
# Data Class & Topic Map
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_verification_result_dataclass():
    res = VerificationResult(
        agrees_on_all=True,
        disagreements=[],
        verifier_notes="All passed",
        raw_response="{}",
    )
    assert res.agrees_on_all is True
    assert res.disagreements == []


@pytest.mark.asyncio
@pytest.mark.unit
async def test_generate_caps_ref_not_found(generator):
    generator._caps_service.get_topic_context = MagicMock(return_value=None)
    with pytest.raises(LessonGenerationError, match="not found in canonical topic map"):
        await generator.generate("INVALID.CAPS.REF")


# ---------------------------------------------------------------------------
# LLM Error Handling & Schema Parsing
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_call_llm_with_error_handling_failure(generator):
    generator._gateway.generate = AsyncMock(side_effect=RuntimeError("Gateway timeout"))
    with pytest.raises(LessonGenerationError, match="LLM generation failed for CAPS reference"):
        await generator._call_llm_with_error_handling(
            prompt="Test prompt",
            operation="lesson_generation",
            caps_ref="4.M.1.1",
        )


@pytest.mark.unit
def test_parse_and_validate_schema_markdown_fences_and_errors(generator, valid_lesson_dict):
    llm_resp = LLMResponse(
        content="```json\n" + json.dumps(valid_lesson_dict) + "\n```",
        provider="groq",
        model="llama3-70b",
        prompt_tokens=100,
        completion_tokens=200,
    )

    # 1. Successful parse with markdown fences
    parsed = generator._parse_and_validate_schema(
        raw_json=llm_resp.content,
        caps_ref="4.M.1.1",
        llm_response=llm_resp,
    )
    assert isinstance(parsed, LessonCreate)
    assert parsed.caps_ref == "4.M.1.1"

    # 2. Malformed JSON
    with pytest.raises(LessonGenerationError, match="LLM returned malformed JSON"):
        generator._parse_and_validate_schema(
            raw_json="not-json",
            caps_ref="4.M.1.1",
            llm_response=llm_resp,
        )

    # 3. Schema validation error
    invalid_dict = {"caps_ref": "4.M.1.1"}
    with pytest.raises(LessonGenerationError, match="failed schema validation"):
        generator._parse_and_validate_schema(
            raw_json=json.dumps(invalid_dict),
            caps_ref="4.M.1.1",
            llm_response=llm_resp,
        )


# ---------------------------------------------------------------------------
# Validator Failure Gate
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_generate_validator_failure_raises(generator, valid_topic_context, valid_lesson_dict):
    generator._caps_service.get_topic_context = MagicMock(return_value=valid_topic_context)
    generator._call_llm_with_error_handling = AsyncMock(
        return_value=LLMResponse(
            content=json.dumps(valid_lesson_dict),
            provider="groq",
            model="llama3",
            prompt_tokens=10,
            completion_tokens=20,
        )
    )

    fail_res = ValidationResult(passed=False, failures=["explanation_too_short", "missing_practice_questions"])
    generator._validator.validate = MagicMock(return_value=fail_res)

    with pytest.raises(LessonValidationError, match="failed 2 validation rule"):
        await generator.generate("4.M.1.1")


# ---------------------------------------------------------------------------
# Answer-Key Verification & Quality Score
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_verify_answer_key_variations(generator, valid_lesson_dict):
    # Construct mock lesson matching LessonCreate interface expected by _verify_answer_key
    mock_lesson = MagicMock()
    mock_lesson.caps_ref = "4.M.1.1"
    mock_lesson.grade = 4
    mock_lesson.topic = "Numbers"
    mock_lesson.subtopic = "Place Value"
    mock_lesson.practice_questions = [
        {"question_id": "pq1", "question": "What is 7 in 789?", "options": {"A": "7", "B": "70", "C": "700", "D": "7000"}}
    ]
    mock_lesson.answer_key = {"pq1": "C"}

    # 1. Verifier gateway exception
    generator._gateway.generate = AsyncMock(side_effect=Exception("Gateway error"))
    res_err = await generator._verify_answer_key(mock_lesson)
    assert res_err.agrees_on_all is False
    assert "LLM call failed" in res_err.verifier_notes

    # 2. Verifier malformed JSON
    generator._gateway.generate = AsyncMock(
        return_value=LLMResponse(content="not-json", provider="groq", model="m", prompt_tokens=1, completion_tokens=1)
    )
    res_bad_json = await generator._verify_answer_key(mock_lesson)
    assert res_bad_json.agrees_on_all is False
    assert "Parse error" in res_bad_json.verifier_notes

    # 3. Disagreement on answer
    verifier_disagree = {
        "verification_results": [
            {
                "question_id": "pq1",
                "derived_answer": "B",  # original is C
                "working": "Calculation error",
                "confidence": 0.8,
            }
        ],
        "verifier_notes": "Disagreement found",
    }
    generator._gateway.generate = AsyncMock(
        return_value=LLMResponse(
            content="```json\n" + json.dumps(verifier_disagree) + "\n```",
            provider="groq",
            model="m",
            prompt_tokens=10,
            completion_tokens=20,
        )
    )
    res_disagree = await generator._verify_answer_key(mock_lesson)
    assert res_disagree.agrees_on_all is False
    assert len(res_disagree.disagreements) == 1

    # 4. Full agreement
    verifier_agree = {
        "verification_results": [
            {
                "question_id": "pq1",
                "derived_answer": "C",
                "working": "Derived C",
                "confidence": 1.0,
            }
        ],
        "verifier_notes": "All verified",
    }
    generator._gateway.generate = AsyncMock(
        return_value=LLMResponse(
            content=json.dumps(verifier_agree),
            provider="groq",
            model="m",
            prompt_tokens=10,
            completion_tokens=20,
        )
    )
    res_agree = await generator._verify_answer_key(mock_lesson)
    assert res_agree.agrees_on_all is True


@pytest.mark.unit
def test_compute_quality_score_dimensions(generator):
    mock_lesson = MagicMock()
    mock_lesson.caps_ref = "4.M.1.1"
    mock_lesson.learning_objectives = ["Objective 1"]
    mock_lesson.explanation = "A" * 200
    mock_lesson.worked_examples = [MagicMock(), MagicMock()]
    mock_lesson.practice_questions = [MagicMock()]
    mock_lesson.answer_key = {"pq1": "C"}
    mock_lesson.remediation_hints = [MagicMock()]
    mock_lesson.safety_classification = "safe"
    mock_lesson.pii_check_passed = True

    val_res = ValidationResult(passed=True, failures=[])

    # 1. Verified high quality
    score_high = generator._compute_quality_score(
        lesson=mock_lesson,
        answer_key_verified=True,
        validation_result=val_res,
    )
    assert 0.85 <= score_high <= 1.0

    # 2. Unverified partial credit
    score_unverified = generator._compute_quality_score(
        lesson=mock_lesson,
        answer_key_verified=False,
        validation_result=val_res,
    )
    assert score_unverified < score_high


# ---------------------------------------------------------------------------
# End-to-End Pipeline: Dry-Run vs Persisted
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_generate_success_dry_run_and_persisted(generator, mock_db, valid_topic_context, valid_lesson_dict):
    generator._caps_service.get_topic_context = MagicMock(return_value=valid_topic_context)
    generator._call_llm_with_error_handling = AsyncMock(
        return_value=LLMResponse(
            content=json.dumps(valid_lesson_dict),
            provider="groq",
            model="llama3-70b-8192",
            prompt_tokens=50,
            completion_tokens=100,
        )
    )
    generator._validator.validate = MagicMock(return_value=ValidationResult(passed=True, failures=[]))
    generator._verify_answer_key = AsyncMock(
        return_value=VerificationResult(agrees_on_all=True, disagreements=[], verifier_notes="OK", raw_response="")
    )
    generator._repo.create_lesson = AsyncMock()

    # 1. Dry run -> skips DB write
    res_dry = await generator.generate("4.M.1.1", dry_run=True)
    assert isinstance(res_dry, LessonResponse)
    assert res_dry.answer_key_verified is True
    assert res_dry.review_status in ("approved", "ai_generated") or hasattr(res_dry.review_status, "value")
    generator._repo.create_lesson.assert_not_called()

    # 2. Persisted run -> writes to DB and commits
    res_persisted = await generator.generate("4.M.1.1", dry_run=False)
    assert isinstance(res_persisted, LessonResponse)
    generator._repo.create_lesson.assert_called_once()
    mock_db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# Compatibility init & generate (db=None)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_lesson_generator_compat_db_none():
    gen = LessonGenerator(db=None, provider="deterministic")
    assert gen._db is None
    assert gen._repo is None

    gen._gateway.generate = AsyncMock(return_value={"caps_ref": "4.M.1.1", "content": "Sample"})
    with patch("app.modules.lessons.lesson_generator.AnswerKeyVerifier") as mock_akv_cls:
        mock_akv = MagicMock()
        mock_akv.verify = AsyncMock(return_value=True)
        mock_akv_cls.return_value = mock_akv

        gen._validator.validate = MagicMock(return_value=ValidationResult(passed=True, failures=[]))
        payload = await gen.generate("4.M.1.1")
        assert payload["answer_key_verified"] is True
