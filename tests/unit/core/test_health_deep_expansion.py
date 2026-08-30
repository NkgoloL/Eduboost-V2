"""Comprehensive unit tests for app/core/health.py."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.core.health import (
    _google_model_name,
    check_postgres,
    check_redis,
    check_llm_provider,
)


def test_google_model_name():
    with patch("app.core.health.settings.GOOGLE_MODEL", "models/gemini-2.0-flash"):
        assert _google_model_name() == "gemini-2.0-flash"


@pytest.mark.asyncio
async def test_check_postgres_error():
    with patch("app.core.health.AsyncSessionLocal") as mock_session:
        mock_session.return_value.__aenter__.side_effect = RuntimeError("DB connection refused")
        res = await check_postgres()
        assert res["status"] == "error"
        assert "RuntimeError" in res["detail"]


@pytest.mark.asyncio
async def test_check_redis_error():
    with patch("app.core.health.get_redis") as mock_get_redis:
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = RuntimeError("Redis connection refused")
        mock_get_redis.return_value = mock_redis

        res = await check_redis()
        assert res["status"] == "error"
        assert "RuntimeError" in res["detail"]


@pytest.mark.asyncio
async def test_check_llm_provider_skipped():
    with patch("app.core.health.settings.GOOGLE_API_KEY", None), \
         patch("app.core.health.settings.GROQ_API_KEY", None), \
         patch("app.core.health.settings.ANTHROPIC_API_KEY", None):
        res = await check_llm_provider()
        assert res["status"] == "skipped"
