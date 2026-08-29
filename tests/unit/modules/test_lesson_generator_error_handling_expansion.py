import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.modules.lessons.lesson_generator import (
    LessonGenerationError,
    VerificationResult,
    LessonGenerator,
)


def test_lesson_generation_error_and_verification_result():
    err = LessonGenerationError("LLM failed to produce valid lesson")
    assert err.status_code == 502
    assert err.error_code == "lesson_generation_failed"

    res = VerificationResult(
        agrees_on_all=True,
        disagreements=[],
        verifier_notes="All answers match",
        raw_response='{"agreement": true}',
    )
    assert res.agrees_on_all is True
    assert len(res.disagreements) == 0


@pytest.mark.asyncio
async def test_lesson_generator_invalid_caps_ref():
    db = AsyncMock()
    generator = LessonGenerator(db)
    generator._caps_service = MagicMock()
    generator._caps_service.get_topic_context.return_value = None

    with pytest.raises(LessonGenerationError, match="CAPS reference 'invalid.ref' not found"):
        await generator.generate("invalid.ref")
