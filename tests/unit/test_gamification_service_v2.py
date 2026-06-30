"""tests/unit/test_gamification_service_v2.py
Unit tests for GamificationServiceV2.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.gamification_service_v2 import (
    GamificationServiceV2,
    _EmptyGamificationRepository,
    _read_field,
)


@pytest.mark.unit
def test_gamification_service_init_with_default_repo():
    """Verify constructor uses default repository when None provided."""
    service = GamificationServiceV2()
    assert service.repository is not None
    assert isinstance(service.repository, _EmptyGamificationRepository)


@pytest.mark.unit
def test_gamification_service_init_with_custom_repo():
    """Verify constructor uses provided repository."""
    mock_repo = AsyncMock()
    service = GamificationServiceV2(repository=mock_repo)
    assert service.repository is mock_repo


@pytest.mark.unit
async def test_get_profile_raises_when_learner_not_found():
    """Verify get_profile raises ValueError when learner not found."""
    mock_repo = AsyncMock()
    mock_repo.get_profile_rows = AsyncMock(return_value=(None, []))
    service = GamificationServiceV2(repository=mock_repo)

    with pytest.raises(ValueError, match="Learner not found"):
        await service.get_profile("learner-123")


@pytest.mark.unit
async def test_get_profile_calculates_level_from_xp():
    """Verify get_profile calculates level correctly from total_xp."""
    mock_learner = MagicMock()
    mock_learner.learner_id = "learner-123"
    mock_learner.total_xp = 250

    mock_repo = AsyncMock()
    mock_repo.get_profile_rows = AsyncMock(return_value=(mock_learner, []))
    service = GamificationServiceV2(repository=mock_repo)

    with patch("app.services.gamification_service_v2.AuditService") as mock_audit:
        mock_audit.return_value.log_event = AsyncMock()
        result = await service.get_profile("learner-123")

        assert result["total_xp"] == 250
        assert result["level"] == 3  # 250 // 100 + 1
        mock_audit.return_value.log_event.assert_called_once()


@pytest.mark.unit
async def test_get_profile_uses_xp_fallback_when_total_xp_missing():
    """Verify get_profile uses xp field when total_xp is missing."""
    mock_learner = MagicMock()
    mock_learner.learner_id = "learner-123"
    mock_learner.xp = 150
    delattr(mock_learner, "total_xp")

    mock_repo = AsyncMock()
    mock_repo.get_profile_rows = AsyncMock(return_value=(mock_learner, []))
    service = GamificationServiceV2(repository=mock_repo)

    result = await service.get_profile("learner-123")

    assert result["total_xp"] == 150
    assert result["level"] == 2  # 150 // 100 + 1


@pytest.mark.unit
async def test_get_profile_builds_badges():
    """Verify get_profile builds badge list from badge rows."""
    mock_learner = MagicMock()
    mock_learner.learner_id = "learner-123"
    mock_learner.total_xp = 100

    mock_badge = MagicMock()
    mock_badge.badge_key = "first_lesson"
    mock_badge.name = "First Lesson"

    mock_learner_badge = MagicMock()
    mock_learner_badge.earned_at = "2024-01-01T00:00:00Z"

    mock_repo = AsyncMock()
    mock_repo.get_profile_rows = AsyncMock(return_value=(mock_learner, [(mock_learner_badge, mock_badge)]))
    service = GamificationServiceV2(repository=mock_repo)

    result = await service.get_profile("learner-123")

    assert len(result["badges"]) == 1
    assert result["badges"][0]["badge_key"] == "first_lesson"
    assert result["badges"][0]["name"] == "First Lesson"
    assert result["badges"][0]["earned_at"] == "2024-01-01T00:00:00Z"


@pytest.mark.unit
async def test_get_profile_uses_defaults_for_missing_fields():
    """Verify get_profile uses defaults when fields are missing."""
    mock_learner = MagicMock()
    mock_learner.id = "learner-123"
    delattr(mock_learner, "learner_id")
    delattr(mock_learner, "total_xp")
    delattr(mock_learner, "xp")
    delattr(mock_learner, "streak_days")

    mock_repo = AsyncMock()
    mock_repo.get_profile_rows = AsyncMock(return_value=(mock_learner, []))
    service = GamificationServiceV2(repository=mock_repo)

    result = await service.get_profile("learner-123")

    assert result["learner_id"] == "learner-123"
    assert result["total_xp"] == 0
    assert result["streak_days"] == 0
    assert result["level"] == 1


@pytest.mark.unit
async def test_leaderboard_returns_empty_list():
    """Verify leaderboard returns empty list when no rows."""
    mock_repo = AsyncMock()
    mock_repo.get_leaderboard_rows = AsyncMock(return_value=[])
    service = GamificationServiceV2(repository=mock_repo)

    result = await service.leaderboard()

    assert result == []


@pytest.mark.unit
async def test_leaderboard_builds_leaderboard():
    """Verify leaderboard builds leaderboard from rows."""
    mock_row = MagicMock()
    mock_row.learner_id = "learner-123"
    mock_row.total_xp = 500
    mock_row.streak_days = 7

    mock_repo = AsyncMock()
    mock_repo.get_leaderboard_rows = AsyncMock(return_value=[mock_row])
    service = GamificationServiceV2(repository=mock_repo)

    result = await service.leaderboard()

    assert len(result) == 1
    assert result[0]["learner_id"] == "learner-123"
    assert result[0]["total_xp"] == 500
    assert result[0]["streak_days"] == 7


@pytest.mark.unit
async def test_leaderboard_uses_xp_fallback():
    """Verify leaderboard uses xp field when total_xp is missing."""
    mock_row = MagicMock()
    mock_row.id = "learner-123"
    mock_row.xp = 300
    delattr(mock_row, "total_xp")

    mock_repo = AsyncMock()
    mock_repo.get_leaderboard_rows = AsyncMock(return_value=[mock_row])
    service = GamificationServiceV2(repository=mock_repo)

    result = await service.leaderboard()

    assert result[0]["total_xp"] == 300


@pytest.mark.unit
async def test_leaderboard_uses_defaults_for_missing_fields():
    """Verify leaderboard uses defaults when fields are missing."""
    mock_row = MagicMock()
    mock_row.id = "learner-123"
    delattr(mock_row, "learner_id")
    delattr(mock_row, "total_xp")
    delattr(mock_row, "xp")
    delattr(mock_row, "streak_days")

    mock_repo = AsyncMock()
    mock_repo.get_leaderboard_rows = AsyncMock(return_value=[mock_row])
    service = GamificationServiceV2(repository=mock_repo)

    result = await service.leaderboard()

    assert result[0]["learner_id"] == "learner-123"
    assert result[0]["total_xp"] == 0
    assert result[0]["streak_days"] == 0


@pytest.mark.unit
async def test_leaderboard_respects_limit():
    """Verify leaderboard passes limit parameter to repository."""
    mock_repo = AsyncMock()
    mock_repo.get_leaderboard_rows = AsyncMock(return_value=[])
    service = GamificationServiceV2(repository=mock_repo)

    await service.leaderboard(limit=5)

    mock_repo.get_leaderboard_rows.assert_called_once_with(limit=5)


@pytest.mark.unit
def test_read_field_from_dict():
    """Verify _read_field extracts value from dict."""
    source = {"key": "value", "number": 42}
    assert _read_field(source, "key") == "value"
    assert _read_field(source, "number") == 42


@pytest.mark.unit
def test_read_field_from_dict_with_default():
    """Verify _read_field returns default when key missing from dict."""
    source = {"key": "value"}
    assert _read_field(source, "missing", "default") == "default"


@pytest.mark.unit
def test_read_field_from_object():
    """Verify _read_field extracts value from object attribute."""
    class TestObj:
        def __init__(self):
            self.key = "value"
            self.number = 42

    obj = TestObj()
    assert _read_field(obj, "key") == "value"
    assert _read_field(obj, "number") == 42


@pytest.mark.unit
def test_read_field_from_object_with_default():
    """Verify _read_field returns default when attribute missing from object."""
    class TestObj:
        def __init__(self):
            self.key = "value"

    obj = TestObj()
    assert _read_field(obj, "missing", "default") == "default"


@pytest.mark.unit
async def test_empty_repository_get_profile_rows():
    """Verify _EmptyGamificationRepository returns None and empty list."""
    repo = _EmptyGamificationRepository()
    learner, badges = await repo.get_profile_rows("learner-123")
    assert learner is None
    assert badges == []


@pytest.mark.unit
async def test_empty_repository_get_leaderboard_rows():
    """Verify _EmptyGamificationRepository returns empty list."""
    repo = _EmptyGamificationRepository()
    rows = await repo.get_leaderboard_rows(limit=10)
    assert rows == []
