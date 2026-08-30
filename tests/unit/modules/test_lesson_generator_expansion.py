import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.lessons.lesson_generator import (
    LessonGenerator,
    LessonGenerationError,
    VerificationResult,
)
from app.modules.lessons.llm_gateway import LLMResponse


def test_verification_result_dataclass():
    res = VerificationResult(
        agrees_on_all=True,
        disagreements=[],
        verifier_notes="All answers verified",
        raw_response="{}",
    )
    assert res.agrees_on_all is True
    assert res.disagreements == []


def test_parse_and_validate_schema_markdown_cleanup():
    db = AsyncMock()
    generator = LessonGenerator(db)

    raw_json_with_fences = """```json
    {
        "title": "Grade 4 Fractions",
        "subject": "Mathematics",
        "grade": 4,
        "caps_ref": "4.M.1.1",
        "difficulty": "on_level",
        "explanation": "Understanding basic fractions...",
        "worked_examples": [],
        "practice_questions": []
    }
    ```"""

    llm_resp = LLMResponse(
        content=raw_json_with_fences,
        provider="groq",
        model="llama3-70b",
        prompt_tokens=100,
        completion_tokens=200,
    )

    with patch("app.modules.lessons.lesson_schema_v1.LessonCreate.model_validate") as mock_validate:
        mock_validate.return_value = MagicMock()
        res = generator._parse_and_validate_schema(
            raw_json=raw_json_with_fences,
            caps_ref="4.M.1.1",
            llm_response=llm_resp,
        )
        assert res is not None
        mock_validate.assert_called_once()


def test_parse_and_validate_schema_invalid_json():
    db = AsyncMock()
    generator = LessonGenerator(db)

    llm_resp = LLMResponse(
        content="Invalid Not A JSON",
        provider="groq",
        model="llama3-70b",
        prompt_tokens=10,
        completion_tokens=10,
    )

    with pytest.raises(LessonGenerationError, match="LLM returned malformed JSON"):
        generator._parse_and_validate_schema(
            raw_json="Invalid Not A JSON",
            caps_ref="4.M.1.1",
            llm_response=llm_resp,
        )


@pytest.mark.asyncio
async def test_generate_caps_not_found():
    db = AsyncMock()
    generator = LessonGenerator(db)
    generator._caps_service.get_topic_context = MagicMock(return_value=None)

    with pytest.raises(LessonGenerationError, match="CAPS reference 'INVALID.REF' not found"):
        await generator.generate("INVALID.REF")
