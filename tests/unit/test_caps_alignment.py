from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from app.core.llm_gateway import ExecutiveService
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
