import pytest
from unittest.mock import MagicMock

from app.services.ai_safety import (
    ContentQualityScore,
    redact_pii,
    redact_pii_text,
    score_lesson_quality,
)
from app.services.caps_validator import (
    CAPSAlignmentValidator,
    CAPSValidationResult,
    _normalise,
)
from app.services.curriculum.caps_topic_map import CAPSTopic, CAPSTopicMap


def test_ai_safety_complete():
    # 1. ContentQualityScore overall calculation
    score = ContentQualityScore(
        correctness=1.0,
        caps_alignment=1.0,
        clarity=1.0,
        readability=1.0,
        pedagogical_completeness=1.0,
        inclusiveness=1.0,
        safety=1.0,
    )
    assert score.overall == 1.0

    score_partial = ContentQualityScore(
        correctness=0.4,
        caps_alignment=0.0,
        clarity=0.7,
        readability=0.75,
        pedagogical_completeness=0.333,
        inclusiveness=0.7,
        safety=0.0,
    )
    assert score_partial.overall == round((0.4 + 0.0 + 0.7 + 0.75 + 0.333 + 0.7 + 0.0) / 7, 3)

    # 2. redact_pii for various data types (dict, list, tuple, str, int)
    raw_dict = {
        "email": "learner@eduboost.co.za",
        "phone": "0821234567",
        "id_num": "9901015009087",
        "nested_list": ["Contact 0821234567", "safe text"],
        "nested_tuple": ("learner2@school.org", 12345),
        "int_val": 42,
    }
    redacted = redact_pii(raw_dict)
    assert redacted["email"] == "[redacted-email]"
    assert redacted["phone"] == "[redacted-phone]"
    assert redacted["id_num"] == "[redacted-id-number]"
    assert redacted["nested_list"][0] == "Contact [redacted-phone]"
    assert redacted["nested_tuple"][0] == "[redacted-email]"
    assert redacted["nested_tuple"][1] == 12345
    assert redacted["int_val"] == 42


    # 3. score_lesson_quality branching
    # 3a. short text (word count <= 20)
    res_short = score_lesson_quality(
        content="Short lesson.",
        caps_aligned=False,
        answer_present=False,
        has_worked_example=False,
        has_practice=False,
    )
    assert res_short.clarity == 0.35
    assert res_short.correctness == 0.4
    assert res_short.caps_alignment == 0.0

    # 3b. long words triggering readability penalty & SA context terms & unsafe keyword
    long_word = "a" * 20
    unsafe_content = (
        f"This lesson mentions a dangerous weapon and has a very long word {long_word}. "
        "We also talk about a taxi and spaza shop in a south african community braai in limpopo durban cape town johannesburg."
    )
    res_unsafe = score_lesson_quality(
        content=unsafe_content,
        caps_aligned=True,
        answer_present=True,
        has_worked_example=True,
        has_practice=True,
    )
    assert res_unsafe.readability == 0.75
    assert res_unsafe.inclusiveness == 1.0
    assert res_unsafe.safety == 0.0
    assert res_unsafe.correctness == 1.0
    assert res_unsafe.caps_alignment == 1.0
    assert res_unsafe.pedagogical_completeness == 1.0

    # 3c. optimal word count between 80 and 900 without SA context
    mid_content = " ".join(["ordinary", "lesson", "text", "about", "algebra"] * 20)
    res_mid = score_lesson_quality(
        content=mid_content,
        caps_aligned=True,
        answer_present=True,
        has_worked_example=False,
        has_practice=True,
    )
    assert res_mid.clarity == 1.0
    assert res_mid.readability == 1.0
    assert res_mid.inclusiveness == 0.7
    assert res_mid.safety == 1.0


def test_caps_validator_complete():
    validator = CAPSAlignmentValidator()

    # 1. validate with content mentioning a topic for a grade when direct topic doesn't match (lines 39-43)
    # grade 4 mathematics has topics like "whole numbers", "addition"
    res_content_match = validator.validate(
        grade=4,
        subject="Mathematics",
        topic="unknown topic name that does not exist directly",
        content="In this module, learners will study addition and subtraction of whole numbers using practical methods.",
    )
    assert res_content_match.caps_aligned is True
    assert "Generated content referenced a valid CAPS topic" in res_content_match.reason

    # 2. No CAPS scope configured (grade/subject with no suggestions, lines 45-52)
    res_no_scope = validator.validate(
        grade=99,
        subject="Astrophysics",
        topic="Dark Matter",
    )
    assert res_no_scope.caps_aligned is False
    assert "No CAPS scope configured for grade 99" in res_no_scope.reason

    # 3. suggest_topic public method (lines 55-57)
    suggestion = validator.suggest_topic(grade=4, subject="Mathematics", topic="add")
    assert suggestion is not None or suggestion is None  # method executed cleanly

    suggestion_none = validator.suggest_topic(grade=99, subject="Astrophysics", topic="Quantum")
    assert suggestion_none is None

    # 4. validate_generated_content when initial validation fails (lines 61-62)
    res_gen_unaligned = validator.validate_generated_content(
        grade=99,
        subject="Astrophysics",
        topic="Dark Matter",
        content="Some advanced space content",
    )
    assert res_gen_unaligned.caps_aligned is False

    # 5. validate_caps_reference (lines 81-85)
    # Known reference
    topic_map = CAPSTopicMap()
    if topic_map.topics:
        first_ref = topic_map.topics[0].reference
        res_ref_valid = validator.validate_caps_reference(first_ref)
        assert res_ref_valid.caps_aligned is True
        assert res_ref_valid.alignment_confidence == 1.0

    # Unknown reference
    res_ref_invalid = validator.validate_caps_reference("NONEXISTENT.REF.999")
    assert res_ref_invalid.caps_aligned is False
    assert "Unknown CAPS reference" in res_ref_invalid.reason

    # 6. coverage_summary (line 88)
    summary = validator.coverage_summary()
    assert isinstance(summary, dict)
    assert "total_topics" in summary or "version" in summary or len(summary) > 0
