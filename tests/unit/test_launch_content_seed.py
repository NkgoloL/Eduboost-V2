"""tests/unit/test_launch_content_seed.py
Unit tests for launch content seed service.
"""
from __future__ import annotations

from uuid import UUID

import pytest

from app.services.launch_content_seed import _lesson_row


@pytest.mark.unit
def test_lesson_row_maps_all_fields():
    """Verify _lesson_row maps all lesson fields correctly."""
    lesson = {
        "lesson_id": "lesson-123",
        "grade": 4,
        "subject": "Mathematics",
        "topic": "Numbers",
        "caps_ref": "4.M.1.1",
        "term": 1,
        "subtopic": "Counting",
        "learning_objectives": ["objective1", "objective2"],
        "explanation": "Test explanation",
        "worked_examples": ["example1"],
        "practice_questions": ["question1"],
        "answer_key": ["answer1"],
        "remediation_hints": ["hint1"],
        "difficulty_level": "easy",
        "language_level": "A1",
        "safety_classification": "safe",
        "pii_check_passed": True,
        "answer_key_verified": True,
        "alignment_confidence": 0.9,
        "quality_score": 0.85,
        "trust_label": {"source": "verified"},
        "review_status": "approved",
        "reviewer_id": "550e8400-e29b-41d4-a716-446655440000",
        "prompt_template_version": "v1",
        "provider": "google",
        "model_version": "gemini-1.5",
        "generation_latency_ms": 1500,
        "token_usage": {"input": 100, "output": 200},
        "variant_type": "standard",
    }

    result = _lesson_row(lesson, "learner-456")

    assert result["id"] == "lesson-123"
    assert result["learner_id"] == "learner-456"
    assert result["grade"] == 4
    assert result["subject"] == "Mathematics"
    assert result["topic"] == "Numbers"
    assert result["caps_ref"] == "4.M.1.1"
    assert result["caps_reference"] == "4.M.1.1"
    assert result["term"] == 1
    assert result["subtopic"] == "Counting"
    assert result["learning_objectives"] == ["objective1", "objective2"]
    assert result["explanation"] == "Test explanation"
    assert result["worked_examples"] == ["example1"]
    assert result["practice_questions"] == ["question1"]
    assert result["answer_key"] == ["answer1"]
    assert result["remediation_hints"] == ["hint1"]
    assert result["difficulty_level"] == "easy"
    assert result["language_level"] == "A1"
    assert result["safety_classification"] == "safe"
    assert result["pii_check_passed"] is True
    assert result["answer_key_verified"] is True
    assert result["alignment_confidence"] == 0.9
    assert result["quality_score"] == 0.85
    assert result["trust_label"] == {"source": "verified"}
    assert result["review_status"] == "approved"
    assert result["reviewer_id"] == UUID("550e8400-e29b-41d4-a716-446655440000")
    assert result["prompt_template_version"] == "v1"
    assert result["provider"] == "google"
    assert result["model_version"] == "gemini-1.5"
    assert result["generation_latency_ms"] == 1500
    assert result["token_usage"] == {"input": 100, "output": 200}
    assert result["variant_type"] == "standard"
    assert result["llm_provider"] == "google"


@pytest.mark.unit
def test_lesson_row_uses_defaults_for_missing_fields():
    """Verify _lesson_row uses sensible defaults for missing optional fields."""
    lesson = {
        "lesson_id": "lesson-123",
        "grade": 4,
        "subject": "Mathematics",
        "topic": "Numbers",
        "caps_ref": "4.M.1.1",
    }

    result = _lesson_row(lesson, "learner-456")

    assert result["id"] == "lesson-123"
    assert result["learner_id"] == "learner-456"
    assert result["term"] is None
    assert result["subtopic"] is None
    assert result["learning_objectives"] == []
    assert result["explanation"] is None
    assert result["worked_examples"] == []
    assert result["practice_questions"] == []
    assert result["answer_key"] == []
    assert result["remediation_hints"] == []
    assert result["difficulty_level"] is None
    assert result["language_level"] is None
    assert result["safety_classification"] == "safe"  # default
    assert result["pii_check_passed"] is False  # bool of None
    assert result["answer_key_verified"] is False  # bool of None
    assert result["alignment_confidence"] == 0.0  # default
    assert result["quality_score"] == 0.0  # default
    assert result["trust_label"] == {}  # default
    assert result["review_status"] == "approved"  # default
    assert result["reviewer_id"] is None
    assert result["prompt_template_version"] is None
    assert result["provider"] is None
    assert result["model_version"] is None
    assert result["generation_latency_ms"] == 0  # default
    assert result["token_usage"] == {}  # default
    assert result["variant_type"] == "standard"  # default
    assert result["llm_provider"] == "google"  # default


@pytest.mark.unit
def test_lesson_row_handles_null_reviewer_id():
    """Verify _lesson_row handles null reviewer_id gracefully."""
    lesson = {
        "lesson_id": "lesson-123",
        "grade": 4,
        "subject": "Mathematics",
        "topic": "Numbers",
        "caps_ref": "4.M.1.1",
        "reviewer_id": None,
    }

    result = _lesson_row(lesson, "learner-456")

    assert result["reviewer_id"] is None


@pytest.mark.unit
def test_lesson_row_handles_empty_string_reviewer_id():
    """Verify _lesson_row handles empty string reviewer_id gracefully."""
    lesson = {
        "lesson_id": "lesson-123",
        "grade": 4,
        "subject": "Mathematics",
        "topic": "Numbers",
        "caps_ref": "4.M.1.1",
        "reviewer_id": "",
    }

    result = _lesson_row(lesson, "learner-456")

    assert result["reviewer_id"] is None


@pytest.mark.unit
def test_lesson_row_uses_provider_for_llm_provider():
    """Verify _lesson_row uses provider field for llm_provider when available."""
    lesson = {
        "lesson_id": "lesson-123",
        "grade": 4,
        "subject": "Mathematics",
        "topic": "Numbers",
        "caps_ref": "4.M.1.1",
        "provider": "openai",
    }

    result = _lesson_row(lesson, "learner-456")

    assert result["llm_provider"] == "openai"


@pytest.mark.unit
def test_lesson_row_defaults_llm_provider_to_google():
    """Verify _lesson_row defaults llm_provider to google when provider missing."""
    lesson = {
        "lesson_id": "lesson-123",
        "grade": 4,
        "subject": "Mathematics",
        "topic": "Numbers",
        "caps_ref": "4.M.1.1",
    }

    result = _lesson_row(lesson, "learner-456")

    assert result["llm_provider"] == "google"


@pytest.mark.unit
def test_lesson_row_converts_floats_safely():
    """Verify _lesson_row converts alignment_confidence and quality_score to float safely."""
    lesson = {
        "lesson_id": "lesson-123",
        "grade": 4,
        "subject": "Mathematics",
        "topic": "Numbers",
        "caps_ref": "4.M.1.1",
        "alignment_confidence": "0.9",  # string that should convert
        "quality_score": None,  # None that should default to 0.0
    }

    result = _lesson_row(lesson, "learner-456")

    assert result["alignment_confidence"] == 0.9
    assert result["quality_score"] == 0.0


@pytest.mark.unit
def test_lesson_row_converts_latency_ms_safely():
    """Verify _lesson_row converts generation_latency_ms to int safely."""
    lesson = {
        "lesson_id": "lesson-123",
        "grade": 4,
        "subject": "Mathematics",
        "topic": "Numbers",
        "caps_ref": "4.M.1.1",
        "generation_latency_ms": "1500",  # string that should convert
    }

    result = _lesson_row(lesson, "learner-456")

    assert result["generation_latency_ms"] == 1500


@pytest.mark.unit
def test_lesson_row_serializes_content_as_json():
    """Verify _lesson_row serializes the lesson dict as JSON in content field."""
    lesson = {
        "lesson_id": "lesson-123",
        "grade": 4,
        "subject": "Mathematics",
        "topic": "Numbers",
        "caps_ref": "4.M.1.1",
        "custom_field": "custom_value",
    }

    result = _lesson_row(lesson, "learner-456")

    assert "content" in result
    assert '"custom_field": "custom_value"' in result["content"]
