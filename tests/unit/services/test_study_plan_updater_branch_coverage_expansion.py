"""Batch 233 — app/services/study_plan_updater.py comprehensive branch coverage expansion.

Tests:
- _compute_priority across all threshold boundaries (urgent < -1.0, high < 0.0, medium >= 0.0)
- apply_diagnostic_result:
  - full result ingestion
  - upsert_topic_entry verification
  - reorder_topics invocation
  - returned entry shape
- get_prioritised_topics:
  - plan is None -> returns empty list
  - multi-priority sorting (urgent, high, medium, low/unknown)
- _reorder_plan: empty vs populated topic list
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.study_plan_updater import (
    PRIORITY_GAP_THRESHOLD,
    STRONG_GAP_THRESHOLD,
    StudyPlanUpdater,
)


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.upsert_topic_entry = AsyncMock()
    repo.reorder_topics = AsyncMock()
    repo.get_plan = AsyncMock()
    return repo


@pytest.fixture
def updater(mock_repo):
    return StudyPlanUpdater(study_plan_repo=mock_repo)


# ---------------------------------------------------------------------------
# Priority Computation
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_compute_priority_boundaries():
    assert StudyPlanUpdater._compute_priority(-1.5) == "urgent"
    assert StudyPlanUpdater._compute_priority(-1.0) == "high"
    assert StudyPlanUpdater._compute_priority(-0.5) == "high"
    assert StudyPlanUpdater._compute_priority(0.0) == "medium"
    assert StudyPlanUpdater._compute_priority(1.2) == "medium"


# ---------------------------------------------------------------------------
# Apply Diagnostic Result
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_apply_diagnostic_result_flow(updater, mock_repo):
    learner_id = uuid.uuid4()
    session_result = {
        "caps_ref": "4.M.1.1",
        "theta": -1.2,
        "standard_error": 0.35,
        "below_grade_level": True,
        "misconception_tags": ["place_value_confusion"],
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_repo.get_plan.return_value = {
        "topics": [
            {"caps_ref": "4.M.1.1", "priority": "urgent"},
            {"caps_ref": "4.M.1.2", "priority": "medium"},
        ]
    }

    entry = await updater.apply_diagnostic_result(learner_id, session_result)

    assert entry["caps_ref"] == "4.M.1.1"
    assert entry["theta"] == -1.2
    assert entry["priority"] == "urgent"
    assert entry["needs_lesson"] is True
    assert entry["misconception_tags"] == ["place_value_confusion"]

    mock_repo.upsert_topic_entry.assert_called_once_with(learner_id, entry)
    mock_repo.reorder_topics.assert_called_once_with(learner_id, ["4.M.1.1", "4.M.1.2"])


# ---------------------------------------------------------------------------
# Get Prioritised Topics & Reorder
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_prioritised_topics_sorting_and_none(updater, mock_repo):
    learner_id = uuid.uuid4()

    # 1. Plan is None -> returns empty list
    mock_repo.get_plan.return_value = None
    assert await updater.get_prioritised_topics(learner_id) == []

    # 2. Multi-priority sorting
    mock_repo.get_plan.return_value = {
        "topics": [
            {"caps_ref": "ref-low", "priority": "low"},
            {"caps_ref": "ref-med", "priority": "medium"},
            {"caps_ref": "ref-urg", "priority": "urgent"},
            {"caps_ref": "ref-high", "priority": "high"},
            {"caps_ref": "ref-none"},  # default to low/3
        ]
    }

    topics = await updater.get_prioritised_topics(learner_id)
    ordered_priorities = [t.get("priority", "low") for t in topics]
    assert ordered_priorities == ["urgent", "high", "medium", "low", "low"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_reorder_plan_empty(updater, mock_repo):
    learner_id = uuid.uuid4()
    mock_repo.get_plan.return_value = {"topics": []}

    await updater._reorder_plan(learner_id)
    mock_repo.reorder_topics.assert_not_called()
