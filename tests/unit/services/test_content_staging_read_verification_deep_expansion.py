"""Comprehensive unit tests for ContentStagingReadVerificationService models and reports."""
from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.content_factory import ContentArtifactStatus
from app.services.content_staging_read_verification import (
    ContentStagingReadVerificationService,
    ScopeStagingReadReport,
    StagingReadVerificationReport,
)


class TestStagingReadVerificationModels:
    def test_staging_read_verification_report(self):
        srid = uuid.uuid4()
        report = StagingReadVerificationReport(
            seed_run_id=srid,
            passed=True,
            verified_count=40,
            errors=[],
        )
        assert report.seed_run_id == srid
        assert report.passed is True
        assert report.verified_count == 40
        assert len(report.errors) == 0

    def test_scope_staging_read_report(self):
        report = ScopeStagingReadReport(
            scope_id="grade4_mathematics_en",
            passed=True,
            staged_artifacts_count=48,
            errors=[],
        )
        assert report.scope_id == "grade4_mathematics_en"
        assert report.passed is True
        assert report.staged_artifacts_count == 48


class TestContentStagingReadVerificationExecution:
    @pytest.mark.asyncio
    async def test_verify_seed_run_branches(self):
        service = ContentStagingReadVerificationService()
        session = AsyncMock()
        srid = uuid.uuid4()
        art1, art2, art3, art4 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

        # Seed items
        item_missing = SimpleNamespace(artifact_id=art1, scope_id="s1", caps_ref="4.M.1.1", layer="lessons")
        item_multi = SimpleNamespace(artifact_id=art2, scope_id="s1", caps_ref="4.M.1.1", layer="lessons")
        item_mismatch = SimpleNamespace(artifact_id=art3, scope_id="s1", caps_ref="4.M.1.1", layer="lessons")
        item_valid = SimpleNamespace(artifact_id=art4, scope_id="s1", caps_ref="4.M.1.1", layer="lessons")

        # 1. Execute responses:
        # call 1: select seeded items
        mock_items_res = MagicMock()
        mock_items_res.scalars.return_value.all.return_value = [
            item_missing,
            item_multi,
            item_mismatch,
            item_valid,
        ]

        # call 2 (item_missing): matches = []
        mock_stage_missing = MagicMock()
        mock_stage_missing.scalars.return_value.all.return_value = []

        # call 3 (item_multi): matches = [row1, row2]
        staged_multi_1 = SimpleNamespace(
            staging_status="inactive",
            scope_id="s1",
            caps_ref="4.M.1.1",
            layer="lessons",
        )
        staged_multi_2 = SimpleNamespace(
            staging_status="inactive",
            scope_id="s1",
            caps_ref="4.M.1.1",
            layer="lessons",
        )
        mock_stage_multi = MagicMock()
        mock_stage_multi.scalars.return_value.all.return_value = [staged_multi_1, staged_multi_2]

        # call 4 (item_mismatch): matches = [row_mismatch]
        staged_mismatch = SimpleNamespace(
            staging_status="active",
            scope_id="s_wrong",
            caps_ref="4.M.1.2",
            layer="diagnostic_items",
        )
        mock_stage_mismatch = MagicMock()
        mock_stage_mismatch.scalars.return_value.all.return_value = [staged_mismatch]

        # call 5 (item_valid): matches = [row_valid]
        staged_valid = SimpleNamespace(
            staging_status="active",
            scope_id="s1",
            caps_ref="4.M.1.1",
            layer="lessons",
        )
        mock_stage_valid = MagicMock()
        mock_stage_valid.scalars.return_value.all.return_value = [staged_valid]

        # call 6 (active_rows count):
        mock_active_res = MagicMock()
        mock_active_res.scalars.return_value.all.return_value = [staged_valid]

        session.execute.side_effect = [
            mock_items_res,
            mock_stage_missing,
            mock_stage_multi,
            mock_stage_mismatch,
            mock_stage_valid,
            mock_active_res,
        ]

        # session.get for source artifact status:
        # art2: None (deleted)
        # art3: PENDING_REVIEW
        # art4: APPROVED
        session.get.side_effect = [
            None,
            SimpleNamespace(status=ContentArtifactStatus.PENDING_REVIEW),
            SimpleNamespace(status=ContentArtifactStatus.APPROVED),
        ]

        rep = await service.verify_seed_run(session, srid)
        assert rep.passed is False
        assert any("Missing staging record" in e for e in rep.errors)
        assert any("Multiple staging records" in e for e in rep.errors)
        assert any("is not active" in e for e in rep.errors)
        assert any("mismatched scope" in e for e in rep.errors)
        assert any("mismatched caps_ref" in e for e in rep.errors)
        assert any("mismatched layer" in e for e in rep.errors)
        assert any("deleted" in e for e in rep.errors)
        assert any("status invalid for staging" in e for e in rep.errors)
        assert any("does not match active staging count" in e for e in rep.errors)

    @pytest.mark.asyncio
    async def test_verify_scope_staging_branches(self):
        service = ContentStagingReadVerificationService()
        session = AsyncMock()
        art1, art2, art3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

        staged1 = SimpleNamespace(artifact_id=art1)
        staged2 = SimpleNamespace(artifact_id=art2)
        staged3 = SimpleNamespace(artifact_id=art3)

        mock_staged_res = MagicMock()
        mock_staged_res.scalars.return_value.all.return_value = [staged1, staged2, staged3]
        session.execute.return_value = mock_staged_res

        # art1: source missing
        # art2: source REJECTED
        # art3: source APPROVED
        session.get.side_effect = [
            None,
            SimpleNamespace(status=ContentArtifactStatus.REJECTED),
            SimpleNamespace(status=ContentArtifactStatus.APPROVED),
        ]

        rep = await service.verify_scope_staging(session, "term_1_maths", layers=["lessons"])
        assert rep.passed is False
        assert rep.staged_artifacts_count == 2
        assert any("source missing" in e for e in rep.errors)
        assert any("status is rejected" in e for e in rep.errors)
