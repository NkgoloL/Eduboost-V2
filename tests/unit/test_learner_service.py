"""tests/unit/test_learner_service.py
Unit tests for LearnerService.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.learner_service import LearnerService


@pytest.mark.unit
async def test_get_learner_summary_returns_learner():
    """Verify get_learner_summary returns learner from repository."""
    mock_learner = MagicMock()
    mock_learner.id = "learner-123"
    mock_learner.name = "Test Learner"

    mock_repo = AsyncMock()
    mock_repo.get_by_id = AsyncMock(return_value=mock_learner)
    service = LearnerService(mock_repo)

    result = await service.get_learner_summary("learner-123")

    assert result.id == "learner-123"
    assert result.name == "Test Learner"
    mock_repo.get_by_id.assert_called_once_with("learner-123")


@pytest.mark.unit
async def test_get_learner_summary_returns_none_when_not_found():
    """Verify get_learner_summary returns None when learner not found."""
    mock_repo = AsyncMock()
    mock_repo.get_by_id = AsyncMock(return_value=None)
    service = LearnerService(mock_repo)

    result = await service.get_learner_summary("nonexistent-learner")

    assert result is None


@pytest.mark.unit
async def test_get_learner_summary_propagates_repository_exception():
    """Verify repository exceptions are not caught by the service."""
    mock_repo = AsyncMock()
    mock_repo.get_by_id = AsyncMock(side_effect=RuntimeError("DB error"))
    service = LearnerService(mock_repo)

    with pytest.raises(RuntimeError, match="DB error"):
        await service.get_learner_summary("learner-123")


@pytest.mark.unit
def test_learner_service_init_stores_repository():
    """Verify constructor stores the repository reference."""
    mock_repo = MagicMock()
    service = LearnerService(mock_repo)
    assert service.repository is mock_repo
