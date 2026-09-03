import pytest

from app.services.content_safety.lesson_contracts import (
    CAPS_TOPIC_MAP,
    LessonOutput,
    LessonValidationResult,
    arithmetic_expression_is_correct,
    caps_topic_exists,
    validate_lesson_output,
)


def _build_valid_lesson(**kwargs) -> LessonOutput:
    data = {
        "topic": "Numbers, operations and relationships",
        "grade": 4,
        "subject": "Mathematics",
        "caps_reference": "CAPS.MATH.G4.NUM.01",
        "objectives": ["Learn fractions"],
        "explanation": "Fractions represent parts of a whole.",
        "worked_examples": ["1/2 + 1/2 = 1"],
        "practice_questions": ["What is 1/2 of 4?"],
        "answer_key": ["2"],
        "remediation_hints": ["Think of sharing a pizza."],
        "difficulty": "medium",
        "language_level": "intermediate",
        "safety_classification": "safe",
        "alignment_confidence": 0.95,
        "quality_score": 0.90,
    }
    data.update(kwargs)
    return LessonOutput(**data)


def test_caps_topic_exists_and_arithmetic():
    assert caps_topic_exists(grade=4, subject="Mathematics", topic="Numbers, operations and relationships")
    assert not caps_topic_exists(grade=4, subject="Mathematics", topic="Nonexistent Topic")
    assert not caps_topic_exists(grade=9, subject="Math", topic="Algebra")

    # arithmetic validator
    assert arithmetic_expression_is_correct("2 + 3", "5")
    assert arithmetic_expression_is_correct("10 / 2", "5.0")
    assert not arithmetic_expression_is_correct("2 + 3", "6")
    assert not arithmetic_expression_is_correct("invalid_chars!", "5")
    assert not arithmetic_expression_is_correct("1 / 0", "0")


def test_validate_lesson_output_all_branches():
    # 1. Valid lesson
    valid = _build_valid_lesson()
    res = validate_lesson_output(valid)
    assert res.accepted is True
    assert res.reasons == ()

    # 2. Missing topic & invalid caps
    res_topic = validate_lesson_output(_build_valid_lesson(topic=""))
    assert "topic missing" in res_topic.reasons
    assert "CAPS alignment invalid" in res_topic.reasons

    # 3. Unsafe content (classification != safe and unsafe regex)
    res_unsafe = validate_lesson_output(_build_valid_lesson(safety_classification="unsafe"))
    assert "unsafe content" in res_unsafe.reasons

    res_regex = validate_lesson_output(_build_valid_lesson(explanation="This involves weapon creation."))
    assert "unsafe content" in res_regex.reasons

    # 4. PII detected
    res_pii = validate_lesson_output(_build_valid_lesson(explanation="Contact me at john.doe@example.com"))
    assert "PII detected" in res_pii.reasons

    # 5. Missing explanation (whitespace only)
    res_empty_exp = validate_lesson_output(_build_valid_lesson(explanation="   "))
    assert "explanation missing" in res_empty_exp.reasons

    # 6. Inconsistent answer key
    res_bad_ans = validate_lesson_output(_build_valid_lesson(practice_questions=["Q1", "Q2"], answer_key=["A1"]))
    assert "answer key missing or inconsistent" in res_bad_ans.reasons

    res_no_ans = validate_lesson_output(_build_valid_lesson(answer_key=[]))
    assert "answer key missing or inconsistent" in res_no_ans.reasons

    # 7. Low confidence and low quality score
    res_low = validate_lesson_output(_build_valid_lesson(alignment_confidence=0.5, quality_score=0.4))
    assert "low alignment confidence" in res_low.reasons
    assert "low quality score" in res_low.reasons
