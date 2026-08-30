import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.llm import (
    ExecutiveService,
    QuotaExceededError,
    active_provider_label,
    _cache_key,
    _google_model_name,
    check_and_consume_quota,
)


def test_cache_key_generation():
    key1 = _cache_key(4, "Mathematics", "Fractions", "en", "visual")
    key2 = _cache_key(4, "Mathematics", "Fractions", "en", "visual")
    key3 = _cache_key(5, "Mathematics", "Fractions", "en", "visual")

    assert key1.startswith("lesson_cache:")
    assert key1 == key2
    assert key1 != key3


def test_active_provider_label_and_google_model():
    with patch("app.core.llm.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = "groq"
        assert active_provider_label() == "groq"

        mock_settings.LLM_PROVIDER = "auto"
        mock_settings.GOOGLE_API_KEY = "g-key"
        assert active_provider_label() == "google"

        mock_settings.GOOGLE_MODEL = "models/gemini-pro"
        assert _google_model_name() == "gemini-pro"


@pytest.mark.asyncio
async def test_check_and_consume_quota():
    with patch("app.core.llm.check_ai_quota", new_callable=AsyncMock) as mock_check:
        mock_decision = MagicMock()
        mock_decision.used = 3
        mock_check.return_value = mock_decision

        used = await check_and_consume_quota("user1", "free")
        assert used == 3


@pytest.mark.asyncio
async def test_executive_service_cache_hit():
    service = ExecutiveService()

    with patch("app.core.llm.cache_get", new_callable=AsyncMock) as mock_cache_get:
        mock_cache_get.return_value = '{"title": "Cached Lesson", "caps_reference": "4.M.1.1"}'
        service._judiciary.stamp_lesson = MagicMock(return_value=MagicMock())

        payload, from_cache = await service.generate_lesson(
            pseudonym_id="pseudo1",
            grade=4,
            subject="Mathematics",
            topic="Fractions",
            language="en",
            archetype=None,
            user_id="user1",
            tier="free",
        )
        assert from_cache is True
        assert payload is not None
