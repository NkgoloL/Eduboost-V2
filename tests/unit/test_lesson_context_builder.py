"""tests/unit/test_lesson_context_builder.py
Unit tests for LessonContextBuilder.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from app.services.lesson_context_builder import (
    GRADE_LEVEL_THRESHOLD,
    LessonContext,
    LessonContextBuilder,
)


@pytest.mark.unit
def test_lesson_context_to_prompt_dict():
    """Verify LessonContext.to_prompt_dict serializes all fields."""
    context = LessonContext(
        learner_id="learner-123",
        caps_ref="4.M.1.1",
        grade=4,
        subject="Mathematics",
        term=1,
        topic="Whole Numbers",
        subtopic="Counting",
        language="en",
        theta=0.5,
        below_grade_level=False,
        severity="mild",
        misconception_tags=["place_value_confusion"],
        gap_topics=["4.M.1.2"],
        remediation_focus="Focus on Whole Numbers",
        suggested_examples=["Order 1, 2, 3"],
        prior_correct_count=8,
        prior_attempted=10,
    )

    result = context.to_prompt_dict()

    assert result["learner_id"] == "learner-123"
    assert result["caps_ref"] == "4.M.1.1"
    assert result["theta"] == 0.5
    assert result["below_grade_level"] is False
    assert result["severity"] == "mild"
    assert result["misconception_tags"] == ["place_value_confusion"]
    assert result["accuracy_pct"] == 80.0


@pytest.mark.unit
def test_lesson_context_to_prompt_dict_zero_attempts():
    """Verify accuracy_pct is 0 when prior_attempted is 0."""
    context = LessonContext(
        learner_id="learner-123",
        caps_ref="4.M.1.1",
        grade=4,
        subject="Mathematics",
        term=1,
        topic="Whole Numbers",
        subtopic="Counting",
        prior_correct_count=0,
        prior_attempted=0,
    )

    result = context.to_prompt_dict()
    assert result["accuracy_pct"] == 0.0


@pytest.mark.unit
def test_lesson_context_defaults():
    """Verify LessonContext has sensible defaults."""
    context = LessonContext(
        learner_id="learner-123",
        caps_ref="4.M.1.1",
        grade=4,
        subject="Mathematics",
        term=1,
        topic="Whole Numbers",
        subtopic="Counting",
    )

    assert context.language == "en"
    assert context.theta == 0.0
    assert context.below_grade_level is False
    assert context.severity == "moderate"
    assert context.misconception_tags == []
    assert context.gap_topics == []
    assert context.remediation_focus == ""
    assert context.suggested_examples == []
    assert context.prior_correct_count == 0
    assert context.prior_attempted == 0


@pytest.mark.unit
def test_lesson_context_builder_init():
    """Verify LessonContextBuilder stores caps_topic_map."""
    map_data = {"4.M.1.1": {"grade": 4, "subject": "Mathematics"}}
    builder = LessonContextBuilder(map_data)
    assert builder._map == map_data


@pytest.mark.unit
def test_lesson_context_builder_build_full_session():
    """Verify build creates LessonContext from full session result."""
    map_data = {
        "4.M.1.1": {
            "grade": 4,
            "subject": "Mathematics",
            "term": 1,
            "topic": "Whole Numbers",
            "subtopic": "Counting",
            "suggested_examples": ["Order 1, 2, 3"],
        }
    }
    builder = LessonContextBuilder(map_data)

    session_result = {
        "learner_id": "learner-123",
        "caps_ref": "4.M.1.1",
        "theta": 0.5,
        "below_grade_level": False,
        "misconception_tags": ["place_value_confusion"],
        "gap_topics": ["4.M.1.2"],
        "items_correct": 8,
        "items_attempted": 10,
    }

    context = builder.build(session_result, learner_language="en")

    assert context.learner_id == "learner-123"
    assert context.caps_ref == "4.M.1.1"
    assert context.theta == 0.5
    assert context.grade == 4
    assert context.subject == "Mathematics"
    assert context.topic == "Whole Numbers"
    assert context.misconception_tags == ["place_value_confusion"]
    assert context.prior_correct_count == 8
    assert context.prior_attempted == 10


@pytest.mark.unit
def test_lesson_context_builder_build_missing_caps_ref():
    """Verify build handles missing caps_ref with defaults."""
    builder = LessonContextBuilder({})

    session_result = {
        "learner_id": "learner-123",
        "caps_ref": "unknown-ref",
        "theta": 0.5,
    }

    with patch("app.services.lesson_context_builder.logger") as mock_logger:
        context = builder.build(session_result)
        mock_logger.warning.assert_called_once()

    assert context.caps_ref == "unknown-ref"
    assert context.grade == 4  # default
    assert context.subject == "Mathematics"  # default
    assert context.topic == "unknown-ref"  # fallback to caps_ref


@pytest.mark.unit
def test_classify_severity_mild():
    """Verify _classify_severity returns 'mild' for theta >= threshold."""
    assert LessonContextBuilder._classify_severity(0.0) == "mild"
    assert LessonContextBuilder._classify_severity(0.5) == "mild"
    assert LessonContextBuilder._classify_severity(1.0) == "mild"


@pytest.mark.unit
def test_classify_severity_moderate():
    """Verify _classify_severity returns 'moderate' for -1.0 <= theta < threshold."""
    assert LessonContextBuilder._classify_severity(-0.5) == "moderate"
    assert LessonContextBuilder._classify_severity(-0.9) == "moderate"
    assert LessonContextBuilder._classify_severity(-1.0) == "moderate"


@pytest.mark.unit
def test_classify_severity_severe():
    """Verify _classify_severity returns 'severe' for theta < -1.0."""
    assert LessonContextBuilder._classify_severity(-1.1) == "severe"
    assert LessonContextBuilder._classify_severity(-2.0) == "severe"
    assert LessonContextBuilder._classify_severity(-3.5) == "severe"


@pytest.mark.unit
def test_build_remediation_focus_basic():
    """Verify _build_remediation_focus creates basic focus string."""
    result = LessonContextBuilder._build_remediation_focus(
        topic="Whole Numbers",
        subtopic="Counting",
        misconception_tags=[],
        severity="mild",
    )

    assert "Whole Numbers" in result
    assert "(Counting)" in result
    assert "Light reinforcement" in result


@pytest.mark.unit
def test_build_remediation_focus_with_misconceptions():
    """Verify _build_remediation_focus includes misconception tags."""
    result = LessonContextBuilder._build_remediation_focus(
        topic="Whole Numbers",
        subtopic="Counting",
        misconception_tags=["place_value_confusion", "borrowing_error"],
        severity="moderate",
    )

    assert "place_value_confusion" in result
    assert "borrowing_error" in result
    assert "Targeted practice" in result


@pytest.mark.unit
def test_build_remediation_focus_limits_misconceptions():
    """Verify _build_remediation_focus limits to top 3 misconceptions."""
    tags = ["tag1", "tag2", "tag3", "tag4", "tag5"]
    result = LessonContextBuilder._build_remediation_focus(
        topic="Whole Numbers",
        subtopic="",
        misconception_tags=tags,
        severity="severe",
    )

    assert "tag1" in result
    assert "tag2" in result
    assert "tag3" in result
    assert "tag4" not in result  # Should be limited to top 3


@pytest.mark.unit
def test_build_remediation_focus_severe():
    """Verify _build_remediation_focus includes severe guidance."""
    result = LessonContextBuilder._build_remediation_focus(
        topic="Whole Numbers",
        subtopic="",
        misconception_tags=[],
        severity="severe",
    )

    assert "foundational re-teaching" in result
    assert "first principles" in result


@pytest.mark.unit
def test_build_remediation_focus_no_subtopic():
    """Verify _build_remediation_focus works without subtopic."""
    result = LessonContextBuilder._build_remediation_focus(
        topic="Whole Numbers",
        subtopic="",
        misconception_tags=[],
        severity="mild",
    )

    assert "Whole Numbers" in result
    assert "(Counting)" not in result  # No subtopic


@pytest.mark.unit
def test_build_remediation_focus_unknown_severity():
    """Verify _build_remediation_focus handles unknown severity gracefully."""
    result = LessonContextBuilder._build_remediation_focus(
        topic="Whole Numbers",
        subtopic="",
        misconception_tags=[],
        severity="unknown",
    )

    assert "Whole Numbers" in result
    # Should not include any severity-specific guidance


@pytest.mark.unit
def test_lesson_context_builder_build_with_language():
    """Verify build respects learner_language parameter."""
    map_data = {
        "4.M.1.1": {
            "grade": 4,
            "subject": "Mathematics",
            "term": 1,
            "topic": "Whole Numbers",
            "subtopic": "Counting",
        }
    }
    builder = LessonContextBuilder(map_data)

    session_result = {
        "learner_id": "learner-123",
        "caps_ref": "4.M.1.1",
        "theta": 0.5,
    }

    context = builder.build(session_result, learner_language="zu")
    assert context.language == "zu"


@pytest.mark.unit
def test_lesson_context_builder_build_uses_defaults():
    """Verify build uses defaults when session_result missing fields."""
    map_data = {
        "4.M.1.1": {
            "grade": 4,
            "subject": "Mathematics",
            "term": 1,
            "topic": "Whole Numbers",
            "subtopic": "Counting",
        }
    }
    builder = LessonContextBuilder(map_data)

    session_result = {"caps_ref": "4.M.1.1"}  # Minimal session result

    context = builder.build(session_result)

    assert context.learner_id == ""
    assert context.theta == 0.0
    assert context.below_grade_level is False
    assert context.misconception_tags == []
    assert context.gap_topics == []
    assert context.prior_correct_count == 0
    assert context.prior_attempted == 0


@pytest.mark.unit
def test_grade_level_threshold_constant():
    """Verify GRADE_LEVEL_THRESHOLD is defined."""
    assert GRADE_LEVEL_THRESHOLD == 0.0


@pytest.mark.unit
def test_lesson_context_builder_logs_info():
    """Verify build logs info message with context details."""
    map_data = {
        "4.M.1.1": {
            "grade": 4,
            "subject": "Mathematics",
            "term": 1,
            "topic": "Whole Numbers",
            "subtopic": "Counting",
        }
    }
    builder = LessonContextBuilder(map_data)

    session_result = {
        "learner_id": "learner-123",
        "caps_ref": "4.M.1.1",
        "theta": 0.5,
        "misconception_tags": ["place_value_confusion"],
    }

    with patch("app.services.lesson_context_builder.logger") as mock_logger:
        builder.build(session_result)
        mock_logger.info.assert_called_once()
        # Verify the logger was called (format string is in call_args[0][0])
        assert mock_logger.info.call_args[0][0].startswith("Built lesson context")
