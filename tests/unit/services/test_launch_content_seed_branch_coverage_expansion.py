"""Batch 218 — app/services/launch_content_seed.py branch coverage expansion.

Tests comprehensive execution paths:
- seed_launch_content_if_needed: disabled flag, non-production, missing artifacts, lock busy, targets already met, active seeding with commit, error rollback
- _try_advisory_lock & _release_advisory_lock (postgres lock acquisition/release and non-postgres bypass)
- _approved_item_counts & _approved_lesson_counts
- _seed_items & _seed_lessons (validation failure, new vs existing lesson updates)
- _seed_learner_id (creates guardian/learner if absent, reuses existing)
- _lesson_row, _artifact_path, _target_for helpers
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.models import Guardian, LearnerProfile, Lesson
from app.models.diagnostic_item import DiagnosticItem, ReviewStatusEnum
from app.services.launch_content_seed import (
    _approved_item_counts,
    _approved_lesson_counts,
    _artifact_path,
    _lesson_row,
    _release_advisory_lock,
    _seed_items,
    _seed_learner_id,
    _seed_lessons,
    _target_for,
    _try_advisory_lock,
    seed_launch_content_if_needed,
)


# ---------------------------------------------------------------------------
# seed_launch_content_if_needed
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_seed_launch_content_disabled_returns_early():
    with patch("app.services.launch_content_seed.settings") as mock_settings:
        mock_settings.CONTENT_STARTUP_SEED_ENABLED = False
        # Should return immediately without querying DB
        await seed_launch_content_if_needed()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_seed_launch_content_non_production_returns_early():
    with patch("app.services.launch_content_seed.settings") as mock_settings:
        mock_settings.CONTENT_STARTUP_SEED_ENABLED = True
        mock_settings.is_production.return_value = False
        await seed_launch_content_if_needed()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_seed_launch_content_missing_artifacts_returns_early(tmp_path):
    with patch("app.services.launch_content_seed.settings") as mock_settings:
        mock_settings.CONTENT_STARTUP_SEED_ENABLED = True
        mock_settings.is_production.return_value = True

        mock_scope = MagicMock()
        mock_scope.caps_refs = ["MATH.4.1"]
        mock_scope.artifact_paths = {}

        with patch("app.services.launch_content_seed.ContentScopeRegistry") as mock_reg_cls:
            mock_reg = MagicMock()
            mock_reg.get_scope.return_value = mock_scope
            mock_reg_cls.return_value = mock_reg

            with patch("app.services.launch_content_seed._artifact_path") as mock_path:
                mock_path.return_value = tmp_path / "non_existent.json"
                await seed_launch_content_if_needed()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_seed_launch_content_lock_busy_returns_early(tmp_path):
    item_file = tmp_path / "items.json"
    item_file.write_text(json.dumps({"items": []}))
    lesson_file = tmp_path / "lessons.json"
    lesson_file.write_text(json.dumps({"lessons": []}))

    with patch("app.services.launch_content_seed.settings") as mock_settings:
        mock_settings.CONTENT_STARTUP_SEED_ENABLED = True
        mock_settings.is_production.return_value = True
        mock_settings.DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"

        mock_scope = MagicMock()
        mock_scope.caps_refs = ["MATH.4.1"]

        mock_session = AsyncMock()

        with (
            patch("app.services.launch_content_seed.ContentScopeRegistry"),
            patch("app.services.launch_content_seed._artifact_path", side_effect=[item_file, lesson_file]),
            patch("app.services.launch_content_seed.AsyncSessionLocal", return_value=mock_session),
            patch("app.services.launch_content_seed._try_advisory_lock", return_value=False),
        ):
            mock_session.__aenter__.return_value = mock_session
            await seed_launch_content_if_needed()
            # Session commit shouldn't be called if lock was busy
            mock_session.commit.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_seed_launch_content_already_complete_skips_seeding(tmp_path):
    item_file = tmp_path / "items.json"
    item_file.write_text(json.dumps({"items": []}))
    lesson_file = tmp_path / "lessons.json"
    lesson_file.write_text(json.dumps({"lessons": []}))

    with patch("app.services.launch_content_seed.settings") as mock_settings:
        mock_settings.CONTENT_STARTUP_SEED_ENABLED = True
        mock_settings.is_production.return_value = True

        mock_scope = MagicMock()
        mock_scope.caps_refs = ["MATH.4.1"]

        mock_session = AsyncMock()

        with (
            patch("app.services.launch_content_seed.ContentScopeRegistry"),
            patch("app.services.launch_content_seed._artifact_path", side_effect=[item_file, lesson_file]),
            patch("app.services.launch_content_seed.AsyncSessionLocal", return_value=mock_session),
            patch("app.services.launch_content_seed._try_advisory_lock", return_value=True),
            patch("app.services.launch_content_seed._release_advisory_lock") as mock_rel,
            patch("app.services.launch_content_seed._approved_item_counts", return_value={"MATH.4.1": 50}),
            patch("app.services.launch_content_seed._approved_lesson_counts", return_value={"MATH.4.1": 10}),
            patch("app.services.launch_content_seed._target_for", return_value=5),
        ):
            mock_session.__aenter__.return_value = mock_session
            await seed_launch_content_if_needed()
            mock_rel.assert_called_once()
            mock_session.commit.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_seed_launch_content_executes_seeding_and_commits(tmp_path):
    item_file = tmp_path / "items.json"
    item_file.write_text(json.dumps({"items": []}))
    lesson_file = tmp_path / "lessons.json"
    lesson_file.write_text(json.dumps({"lessons": []}))

    with patch("app.services.launch_content_seed.settings") as mock_settings:
        mock_settings.CONTENT_STARTUP_SEED_ENABLED = True
        mock_settings.is_production.return_value = True

        mock_scope = MagicMock()
        mock_scope.caps_refs = ["MATH.4.1"]

        mock_session = AsyncMock()

        with (
            patch("app.services.launch_content_seed.ContentScopeRegistry") as mock_reg_cls,
            patch("app.services.launch_content_seed._artifact_path", side_effect=[item_file, lesson_file]),
            patch("app.services.launch_content_seed.AsyncSessionLocal", return_value=mock_session),
            patch("app.services.launch_content_seed._try_advisory_lock", return_value=True),
            patch("app.services.launch_content_seed._release_advisory_lock") as mock_rel,
            patch("app.services.launch_content_seed._approved_item_counts", return_value={"MATH.4.1": 0}),
            patch("app.services.launch_content_seed._approved_lesson_counts", return_value={"MATH.4.1": 0}),
            patch("app.services.launch_content_seed._target_for", return_value=10),
            patch("app.services.launch_content_seed._seed_items", return_value=10) as mock_si,
            patch("app.services.launch_content_seed._seed_lessons", return_value=5) as mock_sl,
        ):
            mock_reg = MagicMock()
            mock_reg.get_scope.return_value = mock_scope
            mock_reg_cls.return_value = mock_reg

            mock_session.__aenter__.return_value = mock_session
            await seed_launch_content_if_needed()
            mock_si.assert_called_once()
            mock_sl.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_rel.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_seed_launch_content_exception_triggers_rollback(tmp_path):
    item_file = tmp_path / "items.json"
    item_file.write_text(json.dumps({"items": []}))
    lesson_file = tmp_path / "lessons.json"
    lesson_file.write_text(json.dumps({"lessons": []}))

    with patch("app.services.launch_content_seed.settings") as mock_settings:
        mock_settings.CONTENT_STARTUP_SEED_ENABLED = True
        mock_settings.is_production.return_value = True

        mock_scope = MagicMock()
        mock_scope.caps_refs = ["MATH.4.1"]

        mock_session = AsyncMock()

        with (
            patch("app.services.launch_content_seed.ContentScopeRegistry"),
            patch("app.services.launch_content_seed._artifact_path", side_effect=[item_file, lesson_file]),
            patch("app.services.launch_content_seed.AsyncSessionLocal", return_value=mock_session),
            patch("app.services.launch_content_seed._try_advisory_lock", return_value=True),
            patch("app.services.launch_content_seed._release_advisory_lock"),
            patch("app.services.launch_content_seed._approved_item_counts", side_effect=RuntimeError("DB dead")),
        ):
            mock_session.__aenter__.return_value = mock_session
            await seed_launch_content_if_needed()
            mock_session.rollback.assert_called_once()


# ---------------------------------------------------------------------------
# Advisory Lock Helpers
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_advisory_lock_non_postgres():
    mock_session = AsyncMock()
    with patch("app.services.launch_content_seed.settings") as mock_settings:
        mock_settings.DATABASE_URL = "sqlite+aiosqlite:///test.db"
        assert await _try_advisory_lock(mock_session) is True
        # Should be a no-op
        await _release_advisory_lock(mock_session)
        mock_session.execute.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_advisory_lock_postgres_acquire_and_release():
    mock_session = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar.return_value = 1
    mock_session.execute.return_value = mock_res

    with patch("app.services.launch_content_seed.settings") as mock_settings:
        mock_settings.DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"
        assert await _try_advisory_lock(mock_session) is True

        # Release handles SQLAlchemyError safely
        mock_session.execute.side_effect = SQLAlchemyError("Lock error")
        await _release_advisory_lock(mock_session)


# ---------------------------------------------------------------------------
# Seed Items & Lessons
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_seed_items_upserts_approved_items(tmp_path):
    item_file = tmp_path / "items.json"
    item_file.write_text(
        json.dumps({
            "items": [
                {"item_id": "item-1", "review_status": "approved"},
                {"item_id": "item-2", "review_status": "rejected"},
            ]
        })
    )

    mock_session = AsyncMock()
    with patch("app.services.launch_content_seed.ItemBankRepository") as mock_repo_cls:
        mock_repo = MagicMock()
        mock_repo.upsert = AsyncMock()
        mock_repo_cls.return_value = mock_repo

        count = await _seed_items(mock_session, item_file)
        assert count == 1
        mock_repo.upsert.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_seed_lessons_validation_failure_raises_runtime_error(tmp_path):
    lesson_file = tmp_path / "lessons.json"
    lesson_file.write_text(
        json.dumps({
            "lessons": [
                {"lesson_id": "l-1", "review_status": "approved"},
            ]
        })
    )

    mock_session = AsyncMock()
    with patch("app.services.launch_content_seed.LessonValidator") as mock_val_cls:
        mock_val = MagicMock()
        val_res = MagicMock(passed=False, failures=["Missing answer key"])
        mock_val.validate.return_value = val_res
        mock_val_cls.return_value = mock_val

        with pytest.raises(RuntimeError, match="failed validation"):
            await _seed_lessons(mock_session, lesson_file)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_seed_lessons_creates_and_updates_lesson_records(tmp_path):
    lesson_file = tmp_path / "lessons.json"
    lesson_file.write_text(
        json.dumps({
            "lessons": [
                {
                    "lesson_id": "l-1",
                    "grade": 4,
                    "subject": "Mathematics",
                    "topic": "Addition",
                    "caps_ref": "MATH.4.1",
                    "review_status": "approved",
                },
                {
                    "lesson_id": "l-2",
                    "grade": 4,
                    "subject": "Mathematics",
                    "topic": "Subtraction",
                    "caps_ref": "MATH.4.2",
                    "review_status": "approved",
                },
            ]
        })
    )

    mock_session = AsyncMock()

    # l-1 exists, l-2 does not
    existing_l1 = MagicMock(spec=Lesson)
    mock_session.get.side_effect = [existing_l1, None]

    with (
        patch("app.services.launch_content_seed.LessonValidator") as mock_val_cls,
        patch("app.services.launch_content_seed._seed_learner_id", return_value="learner-123"),
    ):
        mock_val = MagicMock()
        mock_val.validate.return_value = MagicMock(passed=True)
        mock_val_cls.return_value = mock_val

        count = await _seed_lessons(mock_session, lesson_file)
        assert count == 2
        mock_session.add.assert_called_once()  # l-2 was added


# ---------------------------------------------------------------------------
# _seed_learner_id
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_seed_learner_id_creates_new_guardian_and_learner():
    mock_session = AsyncMock()

    # Guardian not found, learner not found
    res_guardian = MagicMock()
    res_guardian.scalar_one_or_none.return_value = None

    res_learner = MagicMock()
    res_learner.scalar_one_or_none.return_value = None

    mock_session.execute.side_effect = [res_guardian, res_learner]

    # session.add will be called with Guardian, then LearnerProfile
    async def fake_flush():
        # Set an id on added objects if not set
        pass

    mock_session.flush.side_effect = fake_flush

    learner_id = await _seed_learner_id(mock_session)
    assert mock_session.add.call_count == 2  # guardian + learner


@pytest.mark.asyncio
@pytest.mark.unit
async def test_seed_learner_id_reuses_existing():
    mock_session = AsyncMock()

    existing_guardian = MagicMock(spec=Guardian, id="g-1")
    existing_learner = MagicMock(spec=LearnerProfile, id="learner-existing")

    res_guardian = MagicMock()
    res_guardian.scalar_one_or_none.return_value = existing_guardian

    res_learner = MagicMock()
    res_learner.scalar_one_or_none.return_value = existing_learner

    mock_session.execute.side_effect = [res_guardian, res_learner]

    learner_id = await _seed_learner_id(mock_session)
    assert learner_id == "learner-existing"
    mock_session.add.assert_not_called()


# ---------------------------------------------------------------------------
# Count and Target Helpers
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_approved_counts():
    mock_session = AsyncMock()
    res_items = MagicMock()
    res_items.all.return_value = [("MATH.4.1", 15), ("MATH.4.2", 20)]
    mock_session.execute.return_value = res_items

    item_counts = await _approved_item_counts(mock_session, ("MATH.4.1", "MATH.4.2"))
    assert item_counts == {"MATH.4.1": 15, "MATH.4.2": 20}

    res_lessons = MagicMock()
    res_lessons.all.return_value = [("MATH.4.1", 3)]
    mock_session.execute.return_value = res_lessons

    lesson_counts = await _approved_lesson_counts(mock_session, ("MATH.4.1",))
    assert lesson_counts == {"MATH.4.1": 3}


@pytest.mark.unit
def test_target_for_and_artifact_path():
    mock_registry = MagicMock()
    target_obj = MagicMock()
    target_obj.targets = {"diagnostic_items.approved": 35}
    mock_registry.get_scope_targets.return_value = [target_obj]

    mock_scope = MagicMock(scope_id="scope-1", artifact_paths={"lessons": "data/custom.json"})

    target_val = _target_for(mock_scope, "diagnostic_items.approved", 40, registry=mock_registry)
    assert target_val == 35

    default_val = _target_for(mock_scope, "missing.key", 50, registry=mock_registry)
    assert default_val == 50

    custom_path = _artifact_path(mock_scope, "lessons", "data/fallback.json")
    assert "data/custom.json" in str(custom_path)

    fallback_path = _artifact_path(mock_scope, "other_layer", "data/fallback.json")
    assert "data/fallback.json" in str(fallback_path)


@pytest.mark.unit
def test_lesson_row_mapping():
    raw_lesson = {
        "lesson_id": "lesson-123",
        "grade": 4,
        "subject": "Mathematics",
        "topic": "Fractions",
        "caps_ref": "MATH.4.3",
        "reviewer_id": str(uuid.uuid4()),
        "alignment_confidence": 0.95,
    }
    row = _lesson_row(raw_lesson, learner_id="learner-abc")
    assert row["id"] == "lesson-123"
    assert row["learner_id"] == "learner-abc"
    assert row["caps_ref"] == "MATH.4.3"
    assert row["alignment_confidence"] == 0.95
    assert row["safety_classification"] == "safe"
