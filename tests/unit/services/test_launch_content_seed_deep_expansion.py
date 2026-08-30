import json
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.launch_content_seed import (
    seed_launch_content_if_needed,
    _try_advisory_lock,
    _release_advisory_lock,
    _lesson_row,
    _target_for,
    DEFAULT_ITEM_TARGET,
    DEFAULT_LESSON_TARGET,
)


def test_lesson_row_mapping():
    lesson_data = {
        "lesson_id": str(uuid.uuid4()),
        "grade": 4,
        "subject": "mathematics",
        "topic": "fractions",
        "caps_ref": "4.M.1.1",
        "difficulty_level": "on_level",
        "explanation": "Test explanation",
        "worked_examples": [],
        "practice_questions": [],
        "answer_key_verified": True,
        "quality_score": 0.9,
    }
    row = _lesson_row(lesson_data, learner_id="learner-1")
    assert row["id"] == lesson_data["lesson_id"]
    assert row["learner_id"] == "learner-1"
    assert row["grade"] == 4
    assert row["answer_key_verified"] is True
    assert row["quality_score"] == 0.9


def test_target_for_defaults():
    scope = MagicMock()
    scope.scope_id = "scope-1"
    mock_registry = MagicMock()
    mock_registry.get_scope_targets.return_value = []
    target = _target_for(scope, "diagnostic_items.approved", DEFAULT_ITEM_TARGET, registry=mock_registry)
    assert target == DEFAULT_ITEM_TARGET


@pytest.mark.asyncio
async def test_seed_launch_content_disabled():
    with patch("app.services.launch_content_seed.settings") as mock_settings:
        mock_settings.CONTENT_STARTUP_SEED_ENABLED = False
        # Should return immediately without doing anything
        await seed_launch_content_if_needed()


@pytest.mark.asyncio
async def test_advisory_lock_non_postgres():
    session = AsyncMock()
    with patch("app.services.launch_content_seed.settings") as mock_settings:
        mock_settings.DATABASE_URL = "sqlite+aiosqlite:///:memory:"
        locked = await _try_advisory_lock(session)
        assert locked is True

        # Release should no-op
        await _release_advisory_lock(session)
        session.execute.assert_not_called()
