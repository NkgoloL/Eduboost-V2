import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.content_staging_seed_executor import (
    _maybe_await,
    _session_flush,
    _session_commit,
    _session_rollback,
    MissingForeignKeyError,
    SeedableArtifact,
    SkippedArtifact,
    StagingSeedPlan,
    StagingSeedRunResult,
    ContentStagingSeedExecutor,
)


@pytest.mark.asyncio
async def test_session_helpers_async_and_sync():
    mock_session = AsyncMock()
    await _session_flush(mock_session)
    mock_session.flush.assert_awaited_once()

    await _session_commit(mock_session)
    mock_session.commit.assert_awaited_once()

    await _session_rollback(mock_session)
    mock_session.rollback.assert_awaited_once()

    # Sync double
    sync_session = MagicMock()
    sync_session.flush.return_value = None
    await _session_flush(sync_session)


def test_dataclasses():
    art_id = uuid.uuid4()
    seedable = SeedableArtifact(
        artifact_id=art_id,
        scope_id="scope-1",
        caps_ref="4.M.1.1",
        layer="lesson_content",
        artifact_type="lesson",
        payload_json={"title": "Test"},
        artifact_hash="hash123",
    )
    assert seedable.artifact_id == art_id

    skipped = SkippedArtifact(artifact_id=art_id, reason="Not approved")
    assert skipped.reason == "Not approved"

    plan = StagingSeedPlan(
        scope_id="scope-1",
        layers=["lesson_content"],
        seedable=[seedable],
        skipped=[skipped],
    )
    assert len(plan.seedable) == 1
    assert len(plan.skipped) == 1


@pytest.mark.asyncio
async def test_staging_seed_executor_init():
    service = ContentStagingSeedExecutor()
    assert service is not None
