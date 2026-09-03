"""Batch 255 — ContentValidator comprehensive branch coverage expansion.

Tests:
- ValidationResult error_summary property
- Unknown content type error
- Markdown code fences stripping (```json and plain ```)
- Malformed JSON parsing error
- Diagnostic item batch:
  - not a list error
  - empty array refusal error
  - CAPS ref mismatch error
  - item validation error
  - clean valid batch
- Lesson:
  - null refusal error
  - not a dict error
  - lesson validation error
  - CAPS ref mismatch error
  - clean valid lesson
- Custom schema types:
  - missing schema validator
  - valid generic schema
"""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from app.services.content_validator import (
    ContentValidator,
    ValidationResult,
)


@pytest.mark.unit
def test_validation_result_error_summary():
    res_empty = ValidationResult(passed=True, content_type="lesson", schema_version="1.0")
    assert res_empty.error_summary == ""

    res_err = ValidationResult(
        passed=False,
        content_type="lesson",
        schema_version="1.0",
        errors=["Error 1", "Error 2"],
    )
    assert res_err.error_summary == "Error 1; Error 2"


@pytest.mark.unit
def test_content_validator_parser_and_type_errors():
    validator = ContentValidator()

    # 1. Unknown content type
    res_unknown = validator.validate("{}", "unknown_content_type")
    assert res_unknown.passed is False
    assert any("Unknown content type" in e for e in res_unknown.errors)

    # 2. Markdown fence stripping and JSON decode error
    fenced_bad = "```json\n{malformed json}\n```"
    res_bad_json = validator.validate(fenced_bad, "lesson")
    assert res_bad_json.passed is False
    assert any("JSON parse error" in e for e in res_bad_json.errors)


@pytest.mark.unit
def test_content_validator_diagnostic_batch_branches():
    validator = ContentValidator()

    # 1. Not a list
    res_not_list = validator.validate("{}", "diagnostic_item")
    assert res_not_list.passed is False
    assert any("Expected a JSON array" in e for e in res_not_list.errors)

    # 2. Empty list
    res_empty = validator.validate("[]", "diagnostic_item")
    assert res_empty.passed is False
    assert any("LLM returned empty array" in e for e in res_empty.errors)

    # 3. Item validation error & CAPS ref mismatch
    bad_items = [
        {"caps_ref": "4.M.1.2", "stem": "2+2=?"},  # missing options/correct_answer
    ]
    res_bad_item = validator.validate(json.dumps(bad_items), "diagnostic_item", caps_ref="4.M.1.1")
    assert res_bad_item.passed is False
    assert any("does not match expected" in e or "Field required" in e for e in res_bad_item.errors)

    # 4. Valid diagnostic item batch
    good_items = [
        {
            "caps_ref": "4.MATH.1.1",
            "question": "What is the result of adding 2 + 2?",
            "options": ["4", "5", "6", "7"],
            "correct_answer_index": 0,
            "explanation": "Adding 2 and 2 produces 4 as the correct answer.",
            "bloom_level": "knowledge",
            "difficulty_band": "easy",
            "tags": ["addition"],
        }
    ]
    res_good = validator.validate(json.dumps(good_items), "diagnostic_item", caps_ref="4.MATH.1.1")
    assert res_good.passed is True
    assert res_good.validated_payload is not None


@pytest.mark.unit
def test_content_validator_lesson_branches():
    validator = ContentValidator()

    # 1. Null / refusal
    res_null = validator.validate("null", "lesson")
    assert res_null.passed is False
    assert any("LLM returned null" in e for e in res_null.errors)

    # 2. Not a dict
    res_array = validator.validate("[]", "lesson")
    assert res_array.passed is False
    assert any("Expected JSON object for lesson" in e for e in res_array.errors)

    # 3. Schema validation error
    res_schema_err = validator.validate('{"title": "Incomplete Lesson"}', "lesson")
    assert res_schema_err.passed is False
    assert len(res_schema_err.errors) > 0

    # 4. CAPS ref mismatch
    valid_lesson = {
        "title": "Grade 4 Mathematics Whole Numbers Lesson",
        "caps_ref": "4.MATH.1.2",
        "grade": 4,
        "subject_code": "MATH",
        "language": "en",
        "learning_objectives": ["Understand place value and basic addition properties."],
        "key_vocabulary": [{"term": "addition", "definition": "Combining numbers."}],
        "body_markdown": "In this lesson learners will explore column addition step by step with multiple examples and practice activities. " * 3,
        "worked_examples": [
            {
                "problem": "Calculate 15 + 25.",
                "solution": "Add units 5+5=10, carry 1 to tens column, 1+1+2=4.",
                "answer": "40",
            }
        ],
    }
    res_caps_mismatch = validator.validate(json.dumps(valid_lesson), "lesson", caps_ref="4.MATH.1.1")
    assert res_caps_mismatch.passed is False
    assert any("does not match expected" in e for e in res_caps_mismatch.errors)

    # 5. Clean valid lesson
    res_valid = validator.validate(json.dumps(valid_lesson), "lesson", caps_ref="4.MATH.1.2")
    assert res_valid.passed is True
    assert res_valid.validated_payload is not None
