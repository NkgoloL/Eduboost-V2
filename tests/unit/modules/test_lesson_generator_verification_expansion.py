import pytest
from unittest.mock import MagicMock

from app.modules.lessons.lesson_generator import (
    LessonGenerationError,
    VerificationResult,
    LessonGenerator,
)


def test_verification_result_model():
    res = VerificationResult(
        agrees_on_all=True,
        disagreements=[],
        verifier_notes="All answers match derived keys",
        raw_response='{"verified": true}',
    )
    assert res.agrees_on_all is True
    assert len(res.disagreements) == 0


def test_lesson_generation_error():
    err = LessonGenerationError("Failed to render prompt")
    assert err.status_code == 502
    assert err.error_code == "lesson_generation_failed"
