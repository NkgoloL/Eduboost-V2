"""Comprehensive unit tests for staging preview reports and content generation executor."""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock
import pytest

from app.services.content_staging_preview_service import (
    StagingArtifactPreview,
    StagingPreviewReport,
    StagingCapsRefPreview,
)
from app.services.content_generation_executor import (
    TaskExecutionResult,
    RunExecutionResult,
    GenerationDisabledError,
    ContentGenerationExecutor,
)


class TestStagingPreviewDataclasses:
    def test_staging_artifact_preview(self):
        p = StagingArtifactPreview(
            artifact_id="art-123",
            scope_id="grade4_maths",
            caps_ref="4.M.1.1",
            layer="diagnostic_items",
            artifact_type="diagnostic_item",
            staging_status="staged",
            learner_visible=False,
            seed_run_id="run-456",
            seed_run_status="completed",
            verification_passed=True,
            payload={"question": "2+2?"},
            source_artifact_hash="sha256:abc",
            created_at="2026-08-28T10:00:00Z",
        )
        assert p.artifact_id == "art-123"
        assert p.learner_visible is False
        assert p.verification_passed is True

    def test_staging_preview_report(self):
        report = StagingPreviewReport(
            scope_id="grade4_maths",
            layers=["diagnostic_items", "lessons"],
            total_artifacts_count=10,
            active_artifacts_count=10,
            pending_artifacts_count=0,
            learner_visible_count=0,
            artifacts=[],
        )
        assert report.scope_id == "grade4_maths"
        assert report.total_artifacts_count == 10
        assert report.learner_visible_count == 0

    def test_staging_caps_ref_preview(self):
        caps_prev = StagingCapsRefPreview(
            scope_id="grade4_maths",
            caps_ref="4.M.1.1",
            layers=["diagnostic_items"],
            total_artifacts_count=5,
            active_artifacts_count=5,
            learner_visible_count=0,
            artifacts=[],
        )
        assert caps_prev.caps_ref == "4.M.1.1"


class TestContentGenerationExecutorDataclasses:
    def test_task_execution_result(self):
        tid = uuid.uuid4()
        aid = uuid.uuid4()
        res = TaskExecutionResult(
            task_id=tid,
            status="succeeded",
            artifact_ids=[aid],
            provider="groq",
            mode="execution",
        )
        assert res.task_id == tid
        assert res.status == "succeeded"
        assert len(res.artifact_ids) == 1

    def test_run_execution_result(self):
        rid = uuid.uuid4()
        res = RunExecutionResult(
            run_id=rid,
            status="completed",
            task_results=[],
            summary={"tasks": 5, "succeeded": 5},
        )
        assert res.run_id == rid
        assert res.status == "completed"

    def test_generation_disabled_error(self):
        err = GenerationDisabledError("Content generation is disabled in this environment.")
        assert "disabled" in str(err)

    def test_generation_executor_init(self):
        mock_settings = MagicMock()
        mock_scope_reg = MagicMock()
        mock_context = MagicMock()
        mock_factory = MagicMock()
        mock_runs = MagicMock()

        executor = ContentGenerationExecutor(
            settings=mock_settings,
            scope_registry=mock_scope_reg,
            source_context_service=mock_context,
            content_factory_service=mock_factory,
            run_service=mock_runs,
        )
        assert executor.settings == mock_settings
        assert executor.scope_registry == mock_scope_reg
        assert executor.source_context_service == mock_context
        assert executor.content_factory_service == mock_factory
        assert executor.run_service == mock_runs
