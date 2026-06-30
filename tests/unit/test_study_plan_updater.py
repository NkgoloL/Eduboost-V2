"""tests/unit/test_study_plan_updater.py
Unit tests for StudyPlanUpdater diagnostic result application.
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest

from app.services.study_plan_updater import (
    PRIORITY_GAP_THRESHOLD,
    STRONG_GAP_THRESHOLD,
    StudyPlanUpdater,
)


@pytest.mark.unit
def test_study_plan_updater_init_stores_repo():
    """Verify constructor stores repository reference."""
    mock_repo = AsyncMock()
    updater = StudyPlanUpdater(mock_repo)
    assert updater._repo is mock_repo


@pytest.mark.unit
async def test_apply_diagnostic_result_updates_topic_entry():
    """Verify apply_diagnostic_result builds and persists topic entry."""
    mock_repo = AsyncMock()
    mock_repo.get_plan = AsyncMock(return_value={"topics": []})
    updater = StudyPlanUpdater(mock_repo)

    session_result = {
        "caps_ref": "CAPS.4.MAT.1.1",
        "theta": -0.5,
        "standard_error": 0.2,
        "below_grade_level": True,
        "misconception_tags": ["place_value"],
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    learner_id = UUID("12345678-1234-5678-1234-567812345678")

    with patch("app.services.study_plan_updater.logger") as mock_logger:
        await updater.apply_diagnostic_result(learner_id, session_result)

        mock_repo.upsert_topic_entry.assert_called_once()
        call_args = mock_repo.upsert_topic_entry.call_args
        assert call_args[0][0] == learner_id
        assert call_args[0][1]["caps_ref"] == "CAPS.4.MAT.1.1"
        assert call_args[0][1]["theta"] == -0.5
        assert call_args[0][1]["priority"] == "high"
        assert call_args[0][1]["needs_lesson"] is True
        mock_logger.info.assert_called_once()


@pytest.mark.unit
async def test_apply_diagnostic_result_reorders_plan():
    """Verify apply_diagnostic_result triggers plan reordering."""
    mock_repo = AsyncMock()
    mock_repo.get_plan = AsyncMock(return_value={
        "topics": [{"caps_ref": "CAPS.4.MAT.1.1", "priority": "high"}]
    })
    updater = StudyPlanUpdater(mock_repo)

    session_result = {
        "caps_ref": "CAPS.4.MAT.1.1",
        "theta": -0.5,
        "standard_error": 0.2,
        "below_grade_level": True,
    }

    learner_id = UUID("12345678-1234-5678-1234-567812345678")

    await updater.apply_diagnostic_result(learner_id, session_result)

    mock_repo.reorder_topics.assert_called_once()


@pytest.mark.unit
async def test_get_prioritised_topics_returns_empty_when_no_plan():
    """Verify get_prioritised_topics returns empty list when no plan exists."""
    mock_repo = AsyncMock()
    mock_repo.get_plan = AsyncMock(return_value=None)
    updater = StudyPlanUpdater(mock_repo)

    learner_id = UUID("12345678-1234-5678-1234-567812345678")
    topics = await updater.get_prioritised_topics(learner_id)

    assert topics == []


@pytest.mark.unit
async def test_get_prioritised_topics_sorts_by_priority():
    """Verify get_prioritised_topics sorts topics by priority order."""
    mock_repo = AsyncMock()
    mock_repo.get_plan = AsyncMock(return_value={
        "topics": [
            {"caps_ref": "ref1", "priority": "medium"},
            {"caps_ref": "ref2", "priority": "urgent"},
            {"caps_ref": "ref3", "priority": "high"},
            {"caps_ref": "ref4", "priority": "low"},
        ]
    })
    updater = StudyPlanUpdater(mock_repo)

    learner_id = UUID("12345678-1234-5678-1234-567812345678")
    topics = await updater.get_prioritised_topics(learner_id)

    assert topics[0]["priority"] == "urgent"
    assert topics[1]["priority"] == "high"
    assert topics[2]["priority"] == "medium"
    assert topics[3]["priority"] == "low"


@pytest.mark.unit
async def test_get_prioritised_topics_handles_missing_priority():
    """Verify get_prioritised_topics treats missing priority as low."""
    mock_repo = AsyncMock()
    mock_repo.get_plan = AsyncMock(return_value={
        "topics": [
            {"caps_ref": "ref1", "priority": "high"},
            {"caps_ref": "ref2"},  # No priority
        ]
    })
    updater = StudyPlanUpdater(mock_repo)

    learner_id = UUID("12345678-1234-5678-1234-567812345678")
    topics = await updater.get_prioritised_topics(learner_id)

    assert topics[0]["priority"] == "high"
    assert topics[1]["caps_ref"] == "ref2"


@pytest.mark.unit
def test_compute_priority_urgent():
    """Verify _compute_priority returns urgent for theta < -1.0."""
    assert StudyPlanUpdater._compute_priority(-1.5) == "urgent"


@pytest.mark.unit
def test_compute_priority_high():
    """Verify _compute_priority returns high for -1.0 <= theta < 0.0."""
    assert StudyPlanUpdater._compute_priority(-0.5) == "high"


@pytest.mark.unit
def test_compute_priority_medium():
    """Verify _compute_priority returns medium for theta >= 0.0."""
    assert StudyPlanUpdater._compute_priority(0.0) == "medium"
    assert StudyPlanUpdater._compute_priority(0.5) == "medium"


@pytest.mark.unit
def test_compute_priority_threshold_constants():
    """Verify threshold constants are defined correctly."""
    assert PRIORITY_GAP_THRESHOLD == 0.0
    assert STRONG_GAP_THRESHOLD == -1.0


@pytest.mark.unit
async def test_reorder_plan_skips_when_no_topics():
    """Verify _reorder_plan skips reordering when no topics exist."""
    mock_repo = AsyncMock()
    mock_repo.get_plan = AsyncMock(return_value={"topics": []})
    updater = StudyPlanUpdater(mock_repo)

    learner_id = UUID("12345678-1234-5678-1234-567812345678")
    await updater._reorder_plan(learner_id)

    mock_repo.reorder_topics.assert_not_called()


@pytest.mark.unit
async def test_reorder_plan_logs_debug():
    """Verify _reorder_plan logs debug message when reordering."""
    mock_repo = AsyncMock()
    mock_repo.get_plan = AsyncMock(return_value={
        "topics": [{"caps_ref": "ref1", "priority": "high"}]
    })
    updater = StudyPlanUpdater(mock_repo)

    learner_id = UUID("12345678-1234-5678-1234-567812345678")

    with patch("app.services.study_plan_updater.logger") as mock_logger:
        await updater._reorder_plan(learner_id)
        mock_logger.debug.assert_called_once()
