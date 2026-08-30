"""Comprehensive unit tests for launch content seed constants and staging seed executor models."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.services.launch_content_seed import (
    LAUNCH_SCOPE_ID,
    DEFAULT_ITEM_TARGET,
    DEFAULT_LESSON_TARGET,
    SEED_OWNER_EMAIL,
    SEED_LEARNER_NAME,
    SEED_LEARNER_GRADE,
    ADVISORY_LOCK,
)
from app.services.content_staging_seed_executor import (
    SeedableArtifact,
    SkippedArtifact,
    MissingForeignKeyError,
    _maybe_await,
    _session_flush,
    _session_commit,
    _session_rollback,
)


class TestLaunchContentSeedConstants:
    def test_constants_values(self):
        assert LAUNCH_SCOPE_ID == "grade4_mathematics_en"
        assert DEFAULT_ITEM_TARGET == 40
        assert DEFAULT_LESSON_TARGET == 8
        assert SEED_LEARNER_GRADE == 4
        assert "Launch Content Seed" in SEED_LEARNER_NAME
        assert "@example.invalid" in SEED_OWNER_EMAIL
        assert isinstance(ADVISORY_LOCK, tuple)
        assert len(ADVISORY_LOCK) == 2


class TestContentStagingSeedExecutorDataclasses:
    def test_seedable_artifact_dataclass(self):
        aid = uuid.uuid4()
        art = SeedableArtifact(
            artifact_id=aid,
            scope_id="grade4_maths",
            caps_ref="4.M.1.1",
            layer="diagnostic_items",
            artifact_type="diagnostic_item",
            payload_json={"question": "2+2"},
            artifact_hash="hash123",
        )
        assert art.artifact_id == aid
        assert art.scope_id == "grade4_maths"
        assert art.artifact_hash == "hash123"

    def test_skipped_artifact_dataclass(self):
        aid = uuid.uuid4()
        art = SkippedArtifact(
            artifact_id=aid,
            reason="missing_validation_report",
        )
        assert art.artifact_id == aid
        assert art.reason == "missing_validation_report"

    def test_missing_foreign_key_error(self):
        err = MissingForeignKeyError("Referenced run does not exist")
        assert "Referenced run" in str(err)

    @pytest.mark.asyncio
    async def test_session_helpers(self):
        mock_session = AsyncMock()

        await _session_flush(mock_session)
        mock_session.flush.assert_called_once()

        await _session_commit(mock_session)
        mock_session.commit.assert_called_once()

        await _session_rollback(mock_session)
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_maybe_await_with_sync_and_async(self):
        # Sync value
        assert await _maybe_await(42) == 42

        # Async coroutine
        async def sample_coro():
            return "async_value"

        assert await _maybe_await(sample_coro()) == "async_value"
