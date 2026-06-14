"""
Phase 1 — EC-01, EC-02: Content validator tests.
Every invalid or unsafe output must be rejected and cannot be published.
"""
from __future__ import annotations

import json

import pytest

from app.services.content_validator import ContentValidator, ValidationResult
from tests.phase01.conftest import VALID_DIAGNOSTIC_ITEM, VALID_LESSON


@pytest.fixture()
def validator() -> ContentValidator:
    return ContentValidator()


# ---------------------------------------------------------------------------
# Diagnostic item validation
# ---------------------------------------------------------------------------


class TestDiagnosticItemValidation:
    def test_valid_item_passes(self, validator):
        raw = json.dumps([VALID_DIAGNOSTIC_ITEM])
        result = validator.validate(raw, "diagnostic_item")
        assert result.passed is True
        assert result.validated_payload is not None
        assert len(result.validated_payload.items) == 1

    def test_valid_batch_multiple_items(self, validator):
        items = [VALID_DIAGNOSTIC_ITEM, {**VALID_DIAGNOSTIC_ITEM, "question": "What is 2 + 2? A simple addition question."}]
        raw = json.dumps(items)
        result = validator.validate(raw, "diagnostic_item")
        assert result.passed is True
        assert len(result.validated_payload.items) == 2

    def test_missing_question_fails(self, validator):
        bad = {**VALID_DIAGNOSTIC_ITEM}
        del bad["question"]
        result = validator.validate(json.dumps([bad]), "diagnostic_item")
        assert result.passed is False
        assert any("question" in e for e in result.errors)

    def test_question_too_short_fails(self, validator):
        bad = {**VALID_DIAGNOSTIC_ITEM, "question": "Short?"}
        result = validator.validate(json.dumps([bad]), "diagnostic_item")
        assert result.passed is False

    def test_correct_answer_index_out_of_range_fails(self, validator):
        bad = {**VALID_DIAGNOSTIC_ITEM, "correct_answer_index": 10}
        result = validator.validate(json.dumps([bad]), "diagnostic_item")
        assert result.passed is False
        assert any("correct_answer_index" in e or "out of range" in e for e in result.errors)

    def test_invalid_bloom_level_fails(self, validator):
        bad = {**VALID_DIAGNOSTIC_ITEM, "bloom_level": "memorization"}
        result = validator.validate(json.dumps([bad]), "diagnostic_item")
        assert result.passed is False

    def test_invalid_difficulty_band_fails(self, validator):
        bad = {**VALID_DIAGNOSTIC_ITEM, "difficulty_band": "trivial"}
        result = validator.validate(json.dumps([bad]), "diagnostic_item")
        assert result.passed is False

    def test_too_few_options_fails(self, validator):
        bad = {**VALID_DIAGNOSTIC_ITEM, "options": ["only one"]}
        result = validator.validate(json.dumps([bad]), "diagnostic_item")
        assert result.passed is False

    def test_invalid_caps_ref_pattern_fails(self, validator):
        bad = {**VALID_DIAGNOSTIC_ITEM, "caps_ref": "NOT-A-CAPS-REF"}
        result = validator.validate(json.dumps([bad]), "diagnostic_item")
        assert result.passed is False

    def test_caps_ref_mismatch_with_expected_fails(self, validator):
        raw = json.dumps([VALID_DIAGNOSTIC_ITEM])  # caps_ref = "4.M.1.1"
        result = validator.validate(raw, "diagnostic_item", caps_ref="4.M.2.1")
        assert result.passed is False
        assert any("4.M.1.1" in e or "caps_ref" in e for e in result.errors)

    def test_empty_array_fails(self, validator):
        result = validator.validate("[]", "diagnostic_item")
        assert result.passed is False
        assert any("empty" in e.lower() or "refused" in e.lower() for e in result.errors)

    def test_wrong_json_type_fails(self, validator):
        """LLM returning object instead of array must fail."""
        result = validator.validate(json.dumps(VALID_DIAGNOSTIC_ITEM), "diagnostic_item")
        assert result.passed is False
        assert any("array" in e.lower() for e in result.errors)


# ---------------------------------------------------------------------------
# Lesson validation
# ---------------------------------------------------------------------------


class TestLessonValidation:
    def test_valid_lesson_passes(self, validator):
        raw = json.dumps(VALID_LESSON)
        result = validator.validate(raw, "lesson")
        assert result.passed is True
        assert result.validated_payload is not None

    def test_missing_title_fails(self, validator):
        bad = {**VALID_LESSON}
        del bad["title"]
        result = validator.validate(json.dumps(bad), "lesson")
        assert result.passed is False
        assert any("title" in e for e in result.errors)

    def test_body_too_short_fails(self, validator):
        bad = {**VALID_LESSON, "body_markdown": "Too short."}
        result = validator.validate(json.dumps(bad), "lesson")
        assert result.passed is False

    def test_grade_out_of_range_fails(self, validator):
        bad = {**VALID_LESSON, "grade": 15}
        result = validator.validate(json.dumps(bad), "lesson")
        assert result.passed is False

    def test_no_learning_objectives_fails(self, validator):
        bad = {**VALID_LESSON, "learning_objectives": []}
        result = validator.validate(json.dumps(bad), "lesson")
        assert result.passed is False

    def test_null_response_fails(self, validator):
        result = validator.validate("null", "lesson")
        assert result.passed is False
        assert any("null" in e.lower() or "refused" in e.lower() for e in result.errors)


# ---------------------------------------------------------------------------
# JSON parsing edge cases
# ---------------------------------------------------------------------------


class TestJsonParsing:
    def test_markdown_fence_stripped_before_validation(self, validator):
        raw = "```json\n" + json.dumps([VALID_DIAGNOSTIC_ITEM]) + "\n```"
        result = validator.validate(raw, "diagnostic_item")
        assert result.passed is True

    def test_uppercase_json_fence_stripped(self, validator):
        raw = "```JSON\n" + json.dumps([VALID_DIAGNOSTIC_ITEM]) + "\n```"
        result = validator.validate(raw, "diagnostic_item")
        assert result.passed is True

    def test_plain_fence_stripped(self, validator):
        raw = "```\n" + json.dumps([VALID_DIAGNOSTIC_ITEM]) + "\n```"
        result = validator.validate(raw, "diagnostic_item")
        assert result.passed is True

    def test_malformed_json_fails(self, validator):
        result = validator.validate("{not valid json}", "diagnostic_item")
        assert result.passed is False
        assert any("JSON" in e or "parse" in e.lower() for e in result.errors)

    def test_empty_string_fails(self, validator):
        result = validator.validate("", "diagnostic_item")
        assert result.passed is False

    def test_unknown_content_type_fails(self, validator):
        result = validator.validate("{}", "rubric_unknown_type")
        assert result.passed is False
        assert any("Unknown content type" in e or "No validator" in e for e in result.errors)


# ---------------------------------------------------------------------------
# ValidationResult helpers
# ---------------------------------------------------------------------------


class TestValidationResult:
    def test_error_summary_joins_errors(self):
        result = ValidationResult(
            passed=False,
            content_type="diagnostic_item",
            schema_version="1.0",
            errors=["field A: missing", "field B: too short"],
        )
        assert "field A" in result.error_summary
        assert "field B" in result.error_summary

    def test_passed_result_has_no_errors(self):
        result = ValidationResult(
            passed=True,
            content_type="lesson",
            schema_version="1.0",
        )
        assert result.error_summary == ""
        assert result.errors == []
