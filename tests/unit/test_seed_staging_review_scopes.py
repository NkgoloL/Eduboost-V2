"""Unit tests for seed_staging_review_scopes script and executor batching behaviors."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError

from app.services.content_staging_seed_executor import (
    ContentStagingSeedExecutor,
    SeedableArtifact,
    StagingSeedPlan,
)
from scripts.curriculum.seed_staging_review_scopes import run_seeding


class MockSession:
    def __init__(self):
        self.commit_count = 0
        self.rollback_count = 0
        self.added = []

    async def execute(self, stmt):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        return mock_result

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        pass

    async def rollback(self):
        self.rollback_count += 1

    async def commit(self):
        self.commit_count += 1


def _seedable(artifact_id=None):
    return SeedableArtifact(
        artifact_id=artifact_id or uuid.uuid4(),
        scope_id="some_scope",
        caps_ref="test",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        payload_json={},
        artifact_hash="hash",
    )


@pytest.mark.asyncio
async def test_staging_executor_batch_size_respected():
    # 5 items with batch_size=2 should commit 3 times
    session = MockSession()
    executor = ContentStagingSeedExecutor()

    plan = StagingSeedPlan(
        scope_id="some_scope",
        layers=["diagnostic_items"],
        seedable=[_seedable() for _ in range(5)],
        skipped=[],
    )

    with patch.object(executor, "_plan_seed", return_value=plan):
        res = await executor.seed_staging(session, "some_scope", actor_id="admin", batch_size=2)
        assert res.seeded_count == 5
        assert session.commit_count == 3


@pytest.mark.asyncio
async def test_staging_executor_constraint_violation_retry_record_by_record():
    session = MockSession()
    executor = ContentStagingSeedExecutor()

    plan = StagingSeedPlan(
        scope_id="some_scope",
        layers=["diagnostic_items"],
        seedable=[_seedable() for _ in range(3)],
        skipped=[],
    )

    # We want the first batch commit to fail with IntegrityError
    original_commit = session.commit

    async def mock_commit():
        if session.commit_count == 0:
            session.commit_count += 1
            # Raise integrity error to trigger item-by-item retry
            raise IntegrityError("mock uniqueness violation", params=None, orig=None)
        else:
            await original_commit()

    session.commit = mock_commit

    with patch.object(executor, "_plan_seed", return_value=plan):
        res = await executor.seed_staging(session, "some_scope", actor_id="admin", batch_size=5)
        # Should rollback the batch and commit successfully record-by-record
        assert res.seeded_count == 3
        assert session.rollback_count == 1
        assert session.commit_count == 4  # 1 failed batch commit + 3 successful item commits


@pytest.mark.asyncio
async def test_staging_executor_timeout_retry_with_backoff():
    session = MockSession()
    executor = ContentStagingSeedExecutor()

    plan = StagingSeedPlan(
        scope_id="some_scope",
        layers=["diagnostic_items"],
        seedable=[_seedable()],
        skipped=[],
    )

    async def mock_commit():
        # Raise operational error to simulate timeout/pool exhaustion
        session.commit_count += 1
        raise OperationalError("mock timeout", params=None, orig=None)

    session.commit = mock_commit

    with patch.object(executor, "_plan_seed", return_value=plan), \
         patch("asyncio.sleep", return_value=None) as mock_sleep, \
         patch.dict(os.environ, {"SEED_RETRY_BACKOFF_BASE": "1"}):
        with pytest.raises(OperationalError):
            await executor.seed_staging(session, "some_scope", actor_id="admin", batch_size=5)

        # Should try 3 times, sleeping in between, then raise
        assert session.commit_count == 3
        assert session.rollback_count == 3
        assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_seed_staging_script_dry_run(capsys):
    args = argparse.Namespace(
        scope_id=["grade5_mathematics_en"],
        dry_run=True,
        batch_size=None,
        reviewer_id="dev-content-review-2026-06-03",
    )

    plan = StagingSeedPlan(
        scope_id="grade5_mathematics_en",
        layers=["diagnostic_items"],
        seedable=[_seedable()],
        skipped=[],
    )

    with patch("scripts.curriculum.seed_staging_review_scopes.AsyncSessionLocal"), \
         patch("app.services.content_staging_seed_executor.ContentStagingSeedExecutor.dry_run_seed", return_value=plan):
        code = await run_seeding(args)
        assert code == 0
        captured = capsys.readouterr()
        # Verify JSON stdout
        data = json.loads(captured.out)
        assert data["dry_run"] is True
        assert data["summary"]["total_scopes"] == 1
        assert data["summary"]["total_records"] == 1


@pytest.mark.asyncio
async def test_seed_staging_script_summary_written():
    args = argparse.Namespace(
        scope_id=["grade5_mathematics_en"],
        dry_run=False,
        batch_size=100,
        reviewer_id="dev-content-review-2026-06-03",
    )

    res = MagicMock()
    res.status = "seeded_staging"
    res.errors = []
    res.seeded_count = 5
    res.skipped_count = 0
    res.seed_run_id = uuid.uuid4()

    with patch("scripts.curriculum.seed_staging_review_scopes.AsyncSessionLocal"), \
         patch("app.services.content_staging_seed_executor.ContentStagingSeedExecutor.seed_staging", return_value=res):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("scripts.curriculum.seed_staging_review_scopes.ROOT", Path(tmpdir)):
                code = await run_seeding(args)
                assert code == 0

                # Check summary file
                logs_dir = Path(tmpdir) / "logs"
                log_files = list(logs_dir.glob("seed_run_*.json"))
                assert len(log_files) == 1

                log_data = json.loads(log_files[0].read_text(encoding="utf-8"))
                assert log_data["dry_run"] is False
                assert log_data["summary"]["total_scopes_succeeded"] == 1
                assert log_data["summary"]["total_records_upserted"] == 5
                assert log_data["scopes"]["grade5_mathematics_en"] == str(res.seed_run_id)
