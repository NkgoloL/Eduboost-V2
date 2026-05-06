from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from app.core.llm_gateway import ExecutiveService, _coerce_lesson_json, _extract_json_object, _strip_generation_artifacts, settings
from app.services.caps_validator import CAPSAlignmentValidator


def test_caps_validator_accepts_in_scope_topic() -> None:
    validator = CAPSAlignmentValidator()
    result = validator.validate(4, "Mathematics", "Fractions", "This lesson explains fractions with pizza slices.")
    assert result.caps_aligned is True


def test_caps_validator_suggests_nearest_allowed_topic() -> None:
    validator = CAPSAlignmentValidator()
    result = validator.validate(4, "Mathematics", "Probability", "This lesson is about dice.")
    assert result.caps_aligned is False
    assert result.canonical_topic in {"fractions", "problem solving", "measurement", "geometry", "decimals"}


def test_extract_json_object_from_local_model_text() -> None:
    text = 'Here is the lesson:\n{"title": "Fractions", "introduction": "Start"}\nDone.'

    assert _extract_json_object(text) == '{"title": "Fractions", "introduction": "Start"}'


def test_coerce_section_lesson_text_to_json_payload() -> None:
    raw = """
    Title: Grade 4 Mathematics - Fractions
    CAPS alignment: Uses South African CAPS expectations.
    Lesson objective: Learners explain equivalent fractions.
    Teaching activity: Use paper strips to compare halves and quarters.
    Worked example: Two quarters equal one half.
    Assessment evidence: Learners explain one equivalent pair.
    Support and extension: Use local shopping examples with rands.
    """

    payload = json.loads(_coerce_lesson_json(raw))

    assert payload["title"] == "Grade 4 Mathematics - Fractions"
    assert "equivalent fractions" in payload["introduction"]
    assert "paper strips" in payload["main_content"]
    assert "rands" in payload["cultural_hook"]


def test_coerce_incomplete_json_to_required_lesson_payload() -> None:
    raw = json.dumps(
        {
            "title": "Grade 4 Mathematics - Fractions",
            "lesson objective": "Learners explain equivalent fractions.",
            "teaching activity": "Use paper strips to compare fractions.",
        }
    )

    payload = json.loads(_coerce_lesson_json(raw))

    assert payload["title"] == "Grade 4 Mathematics - Fractions"
    assert payload["practice_question"]
    assert payload["answer"]


def test_strip_generation_artifacts_removes_synthetic_chat_turns() -> None:
    raw = "Title: Fractions\nSupport and extension: Use rands.\n<|user|>\nIgnore this"

    assert _strip_generation_artifacts(raw).endswith("Use rands.")


@pytest.mark.asyncio
async def test_executive_uses_local_hf_provider_when_configured(monkeypatch) -> None:
    service = ExecutiveService()
    monkeypatch.setattr(settings, "LLM_PROVIDER", "local_hf")
    local_call = AsyncMock(return_value='{"title": "Local"}')
    monkeypatch.setattr(service, "_call_local_hf", local_call)

    response = await service._call_with_fallback("Prompt", operation="lesson_generation")

    assert response == '{"title": "Local"}'
    local_call.assert_awaited_once_with("Prompt", operation="lesson_generation")


@pytest.mark.asyncio
async def test_executive_retries_when_caps_validation_fails(monkeypatch) -> None:
    service = ExecutiveService()

    first = json.dumps(
        {
            "title": "Maths",
            "introduction": "Today we will talk about plant growth.",
            "main_content": "Plant growth uses sunlight and water.",
            "worked_example": "A plant grows 2cm.",
            "practice_question": "What does a plant need?",
            "answer": "Sunlight",
            "cultural_hook": "A school garden in Limpopo.",
        }
    )
    second = json.dumps(
        {
            "title": "Fractions",
            "introduction": "Today we learn fractions with oranges.",
            "main_content": "Fractions show equal parts of a whole.",
            "worked_example": "Two of four orange slices is one half.",
            "practice_question": "What fraction is 1 out of 4?",
            "answer": "One quarter",
            "cultural_hook": "A fruit stall in Durban.",
        }
    )

    side_effect = AsyncMock(side_effect=[first, second])
    monkeypatch.setattr(service, "_call_with_fallback", side_effect)
    monkeypatch.setattr("app.core.llm_gateway.cache_get", AsyncMock(return_value=None))
    monkeypatch.setattr("app.core.llm_gateway.cache_set", AsyncMock())
    monkeypatch.setattr("app.core.llm_gateway.check_and_consume_quota", AsyncMock())

    payload, from_cache = await service.generate_lesson(
        pseudonym_id="pseudo-1",
        grade=4,
        subject="Mathematics",
        topic="Fractions",
        language="en",
        archetype="Keter",
        user_id="guardian-1",
        tier="free",
    )

    assert from_cache is False
    assert payload.title == "Fractions"
    assert side_effect.await_count == 2
