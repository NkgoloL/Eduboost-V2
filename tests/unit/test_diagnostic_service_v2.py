"""tests/unit/test_diagnostic_service_v2.py
Unit tests for DiagnosticServiceV2.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.diagnostic_service_v2 import DiagnosticServiceV2


@pytest.mark.unit
def test_diagnostic_service_v2_init():
    """Verify DiagnosticServiceV2 initializes with repositories."""
    mock_learner_repo = MagicMock()
    mock_quota_service = MagicMock()
    mock_diagnostic_repo = MagicMock()

    service = DiagnosticServiceV2(mock_learner_repo, mock_quota_service, mock_diagnostic_repo)

    assert service.learner_repository == mock_learner_repo
    assert service.quota_service == mock_quota_service
    assert service.diagnostic_repository == mock_diagnostic_repo


@pytest.mark.unit
async def test_run_diagnostic_returns_cached_result():
    """Verify run_diagnostic returns cached result when available."""
    mock_learner_repo = AsyncMock()
    mock_quota_service = AsyncMock()
    mock_diagnostic_repo = AsyncMock()

    mock_learner = MagicMock()
    mock_learner_repo.get_by_id.return_value = mock_learner

    cached_result = {"session_id": "cached-123", "learner_id": "learner-456"}
    mock_quota_service.get_cached.return_value = cached_result

    service = DiagnosticServiceV2(mock_learner_repo, mock_quota_service, mock_diagnostic_repo)

    result = await service.run_diagnostic("learner-456", "MAT")

    assert result == cached_result
    mock_quota_service.get_cached.assert_called_once_with("diagnostic:learner-456:MAT")
    mock_diagnostic_repo.create_session.assert_not_called()


@pytest.mark.unit
async def test_run_diagnostic_creates_session_when_not_cached():
    """Verify run_diagnostic creates session when no cache hit."""
    mock_learner_repo = AsyncMock()
    mock_quota_service = AsyncMock()
    mock_diagnostic_repo = AsyncMock()

    mock_learner = MagicMock()
    mock_learner_repo.get_by_id.return_value = mock_learner

    mock_quota_service.get_cached.return_value = None

    mock_session = MagicMock()
    mock_session.session_id = "session-123"
    mock_diagnostic_repo.create_session.return_value = mock_session

    service = DiagnosticServiceV2(mock_learner_repo, mock_quota_service, mock_diagnostic_repo)

    result = await service.run_diagnostic("learner-456", "MAT")

    assert result["session_id"] == "session-123"
    assert result["learner_id"] == "learner-456"
    assert result["subject_code"] == "MAT"
    mock_diagnostic_repo.create_session.assert_called_once_with(learner_id="learner-456", subject_code="MAT")


@pytest.mark.unit
async def test_run_diagnostic_raises_when_learner_not_found():
    """Verify run_diagnostic raises ValueError when learner not found."""
    mock_learner_repo = AsyncMock()
    mock_quota_service = AsyncMock()
    mock_diagnostic_repo = AsyncMock()

    mock_learner_repo.get_by_id.return_value = None

    service = DiagnosticServiceV2(mock_learner_repo, mock_quota_service, mock_diagnostic_repo)

    with pytest.raises(ValueError, match="Learner not found"):
        await service.run_diagnostic("learner-456", "MAT")


@pytest.mark.unit
async def test_run_diagnostic_handles_session_without_session_id():
    """Verify run_diagnostic handles session without session_id attribute."""
    mock_learner_repo = AsyncMock()
    mock_quota_service = AsyncMock()
    mock_diagnostic_repo = AsyncMock()

    mock_learner = MagicMock()
    mock_learner_repo.get_by_id.return_value = mock_learner

    mock_quota_service.get_cached.return_value = None

    mock_session = MagicMock(spec=[])  # Empty spec means no attributes
    mock_diagnostic_repo.create_session.return_value = mock_session

    service = DiagnosticServiceV2(mock_learner_repo, mock_quota_service, mock_diagnostic_repo)

    result = await service.run_diagnostic("learner-456", "MAT")

    assert result["session_id"] is None
    assert result["learner_id"] == "learner-456"
