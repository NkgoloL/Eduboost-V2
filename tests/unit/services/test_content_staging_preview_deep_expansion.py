"""Comprehensive unit tests for ContentStagingPreview data models and preview service."""
from __future__ import annotations

import pytest

from app.services.content_staging_preview_service import (
    StagingArtifactPreview,
    StagingPreviewReport,
    StagingCapsRefPreview,
    ContentStagingPreviewService,
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

    def test_content_staging_preview_service_init(self):
        service = ContentStagingPreviewService()
        assert service is not None
