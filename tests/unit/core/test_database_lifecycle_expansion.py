"""Comprehensive unit tests for app/core/database.py."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.core.database import (
    get_async_engine,
    get_db,
    Base,
    engine,
)


def test_get_async_engine():
    e = get_async_engine()
    assert e == engine


def test_base_declarative_class():
    assert Base is not None
    assert hasattr(Base, "metadata")


@pytest.mark.asyncio
async def test_get_db_session_success():
    with patch("app.core.database.AsyncSessionLocal") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        db_gen = get_db()
        session = await anext(db_gen)
        assert session == mock_session

        # Finish generator normally
        try:
            await anext(db_gen)
        except StopAsyncIteration:
            pass

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_db_session_rollback_on_error():
    with patch("app.core.database.AsyncSessionLocal") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        db_gen = get_db()
        session = await anext(db_gen)
        assert session == mock_session

        with pytest.raises(RuntimeError, match="DB query failure"):
            await db_gen.athrow(RuntimeError("DB query failure"))

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
