"""Comprehensive unit tests for Lesson validation errors, result models, and generation errors."""
from __future__ import annotations

import pytest

from app.modules.lessons.lesson_generator import (
    LessonGenerationError,
    VerificationResult,
    PROMPT_TEMPLATE_VERSION,
)
from app.modules.lessons.lesson_validator import (
    LessonValidationError,
    ValidationResult,
)


class TestLessonGeneratorAndValidatorModels:
    def test_lesson_generation_error(self):
        err = LessonGenerationError("Failed to render prompt template")
        assert err.status_code == 502
        assert err.error_code == "lesson_generation_failed"
        assert "Failed to render" in str(err)

    def test_lesson_validation_error(self):
        err = LessonValidationError("Validation rules failed", failures=["Rule 1 failed", "Rule 2 failed"])
        assert err.status_code == 422
        assert err.error_code == "lesson_validation_failed"
        assert len(err.failures) == 2
        assert "Rule 1 failed" in err.failures

    def test_validation_result_bool_and_fields(self):
        res_pass = ValidationResult(passed=True, failures=[], warnings=[], readability_grade=4.5)
        assert bool(res_pass) is True
        assert res_pass.readability_grade == 4.5

        res_fail = ValidationResult(passed=False, failures=["Rule 3: PII detected"])
        assert bool(res_fail) is False
        assert len(res_fail.failures) == 1

    def test_verification_result_dataclass(self):
        vr = VerificationResult(
            agrees_on_all=True,
            disagreements=[],
            verifier_notes="All answers agree with canonical working",
            raw_response='{"agrees": true}',
        )
        assert vr.agrees_on_all is True
        assert len(vr.disagreements) == 0
        assert "agree" in vr.verifier_notes

    def test_prompt_template_version_constant(self):
        assert PROMPT_TEMPLATE_VERSION == "v1"
