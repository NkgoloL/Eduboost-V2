"""Batch 210: Unit tests for content_staging_seed_executor.py covering StagingSeedPlan, StagingSeedRunResult, dry_run_seed, seed_staging, and rollback behaviors."""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.content_factory import ContentArtifactStatus
from app.services.content_staging_seed_executor import (
    ContentStagingSeedExecutor,
    SeedableArtifact,
    SkippedArtifact,
    StagingSeedPlan,
    StagingSeedRunResult,
    StagingRollbackResult,
    MissingForeignKeyError,
)


class TestStagingSeedDataclasses:
    def test_seedable_artifact_fields(self):
        uid = uuid.uuid4()
        art = SeedableArtifact(
            artifact_id=uid,
            scope_id="math-g4",
            caps_ref="4.M.1.1",
            layer="lessons",
            artifact_type="lesson",
            payload_json={"title": "Fractions"},
            artifact_hash="hash123",
        )
        assert art.artifact_id == uid
        assert art.layer == "lessons"

    def test_staging_seed_run_result(self):
        uid = uuid.uuid4()
        res = StagingSeedRunResult(
            seed_run_id=uid,
            scope_id="math-g4",
            status="seeded_staging",
            seeded_count=10,
            skipped_count=0,
            errors=[],
        )
        assert res.seed_run_id == uid
        assert res.seeded_count == 10

    def test_staging_rollback_result(self):
        uid = uuid.uuid4()
        roll = StagingRollbackResult(
            seed_run_id=uid,
            status="rolled_back",
            rolled_back_count=5,
        )
        assert roll.rolled_back_count == 5


class TestContentStagingSeedExecutorLogic:
    @pytest.mark.asyncio
    async def test_dry_run_seed_delegation(self):
        executor = ContentStagingSeedExecutor()
        plan_mock = StagingSeedPlan(
            scope_id="scope-01",
            layers=["lessons"],
            seedable=[
                SeedableArtifact(
                    artifact_id=uuid.uuid4(),
                    scope_id="scope-01",
                    caps_ref="4.M.1",
                    layer="lessons",
                    artifact_type="lesson",
                    payload_json={},
                    artifact_hash="abc",
                )
            ],
            skipped=[],
        )
        executor._plan_seed = AsyncMock(return_value=plan_mock)
        
        session = MagicMock()
        result = await executor.dry_run_seed(session, "scope-01", layers=["lessons"])
        assert result.scope_id == "scope-01"
        assert len(result.seedable) == 1
        assert len(result.skipped) == 0

    @pytest.mark.asyncio
    async def test_seed_staging_disallow_partial_with_skips(self):
        executor = ContentStagingSeedExecutor()
        plan_mock = StagingSeedPlan(
            scope_id="scope-01",
            layers=["lessons"],
            seedable=[],
            skipped=[SkippedArtifact(artifact_id=uuid.uuid4(), reason="Validation report failed")],
        )
        executor._plan_seed = AsyncMock(return_value=plan_mock)
        
        session = MagicMock()
        result = await executor.seed_staging(session, "scope-01", actor_id="admin", allow_partial=False)
        assert result.status == "failed"
        assert result.seeded_count == 0
        assert result.skipped_count == 1
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_seed_staging_happy_path(self):
        executor = ContentStagingSeedExecutor()
        art_id = uuid.uuid4()
        plan_mock = StagingSeedPlan(
            scope_id="scope-01",
            layers=["lessons"],
            seedable=[
                SeedableArtifact(
                    artifact_id=art_id,
                    scope_id="scope-01",
                    caps_ref="4.M.1",
                    layer="lessons",
                    artifact_type="lesson",
                    payload_json={"title": "Test"},
                    artifact_hash="hash-123",
                )
            ],
            skipped=[],
        )
        executor._plan_seed = AsyncMock(return_value=plan_mock)

        # Mock session with async execution
        session = MagicMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        
        exec_res = MagicMock()
        exec_res.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=exec_res)

        result = await executor.seed_staging(session, "scope-01", actor_id="admin", allow_partial=True)
        assert result.status == "seeded_staging"
        assert result.seeded_count == 1
        assert result.skipped_count == 0
