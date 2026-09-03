"""Comprehensive unit tests for ContentStagingPreview data models and preview service."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.content_staging_preview_service import (
    ContentStagingPreviewService,
    StagingArtifactPreview,
    StagingCapsRefPreview,
    StagingPreviewReport,
)


class TestContentStagingPreviewModels:
    def test_staging_artifact_preview_dataclass(self):
        preview = StagingArtifactPreview(
            artifact_id="art-123",
            scope_id="grade4_mathematics_en",
            caps_ref="4.M.1.1",
            layer="diagnostic_items",
            artifact_type="diagnostic_item",
            staging_status="active",
            learner_visible=False,
            seed_run_id="run-456",
            seed_run_status="passed",
            verification_passed=True,
            payload={"question": "What is 2+2?"},
            source_artifact_hash="hash-abc",
            created_at="2026-08-28T00:00:00Z",
        )
        assert preview.artifact_id == "art-123"
        assert preview.learner_visible is False
        assert preview.verification_passed is True

    def test_staging_preview_report_dataclass(self):
        report = StagingPreviewReport(
            scope_id="grade4_mathematics_en",
            layers=["diagnostic_items", "lessons"],
            total_artifacts_count=80,
            active_artifacts_count=80,
            pending_artifacts_count=0,
            learner_visible_count=0,
            artifacts=[],
        )
        assert report.scope_id == "grade4_mathematics_en"
        assert report.total_artifacts_count == 80
        assert report.learner_visible_count == 0

    def test_staging_caps_ref_preview_dataclass(self):
        caps_preview = StagingCapsRefPreview(
            scope_id="grade4_mathematics_en",
            caps_ref="4.M.1.1",
            layers=["diagnostic_items"],
            total_artifacts_count=40,
            active_artifacts_count=40,
            learner_visible_count=0,
            artifacts=[],
        )
        assert caps_preview.caps_ref == "4.M.1.1"
        assert caps_preview.active_artifacts_count == 40


class TestContentStagingPreviewServiceExecution:
    @pytest.mark.asyncio
    async def test_preview_scope_and_caps_ref_execution(self):
        service = ContentStagingPreviewService()
        session = AsyncMock()

        art_id1 = uuid.uuid4()
        art_id2 = uuid.uuid4()
        seed_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        staged_active = SimpleNamespace(
            artifact_id=art_id1,
            scope_id="term_1_maths",
            caps_ref="4.M.1.1",
            layer="lessons",
            artifact_type="lesson",
            staging_status="active",
            created_by_seed_run_id=seed_id,
            payload_json={"title": "Lesson 1"},
            source_artifact_hash="hash_1",
            created_at=now,
        )
        gen_art1 = SimpleNamespace(artifact_id=art_id1)

        staged_pending = SimpleNamespace(
            artifact_id=art_id2,
            scope_id="term_1_maths",
            caps_ref="4.M.1.1",
            layer="diagnostic_items",
            artifact_type="diagnostic_item",
            staging_status="pending",
            created_by_seed_run_id=None,
            payload_json={"title": "Item 1"},
            source_artifact_hash="hash_2",
            created_at=now,
        )
        gen_art2 = SimpleNamespace(artifact_id=art_id2)

        mock_res = MagicMock()
        mock_res.__iter__.return_value = [
            (staged_active, gen_art1),
            (staged_pending, gen_art2),
        ]
        session.execute.return_value = mock_res

        # Mock helper scalar lookups for seed run status and verification
        session.scalar.side_effect = ["completed", "completed"]

        # 1. preview_scope
        report = await service.preview_scope(session, "term_1_maths", layers=["lessons", "diagnostic_items"])
        assert report.scope_id == "term_1_maths"
        assert report.total_artifacts_count == 2
        assert report.active_artifacts_count == 1
        assert report.pending_artifacts_count == 1
        assert report.learner_visible_count == 0
        assert len(report.artifacts) == 2
        assert report.artifacts[0].seed_run_status == "completed"
        assert report.artifacts[0].verification_passed is True

        # 2. preview_caps_ref
        session.scalar.side_effect = ["completed", "completed"]
        caps_rep = await service.preview_caps_ref(session, "term_1_maths", "4.M.1.1", layers=["lessons"])
        assert caps_rep.scope_id == "term_1_maths"
        assert caps_rep.caps_ref == "4.M.1.1"
        assert caps_rep.total_artifacts_count == 2
        assert caps_rep.active_artifacts_count == 1
        assert caps_rep.learner_visible_count == 0
