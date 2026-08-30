"""Comprehensive unit tests for ContentFileArtifactImport data models and batch plans."""
from __future__ import annotations

import uuid
import pytest

from app.services.content_file_artifact_import import (
    _LAYER_SPECS,
    FileArtifactImportRecord,
    FileArtifactImportPlan,
    FileArtifactImportBatchPlan,
)


class TestContentFileArtifactImportModels:
    def test_layer_specs_mapping(self):
        assert "diagnostic_items" in _LAYER_SPECS
        assert "lessons" in _LAYER_SPECS
        assert "assessment_blueprints" in _LAYER_SPECS
        assert "study_plan_templates" in _LAYER_SPECS

    def test_file_artifact_import_record_dataclass(self):
        aid = uuid.uuid4()
        rec = FileArtifactImportRecord(
            artifact_id=aid,
            scope_id="grade4_mathematics_en",
            layer="diagnostic_items",
            artifact_type="diagnostic_item",
            caps_ref="4.M.1.1",
            artifact_hash="hash-1234",
            status="pending_review",
            source_document_id="doc-001",
            payload_json={"question": "Test question"},
        )
        assert rec.artifact_id == aid
        assert rec.scope_id == "grade4_mathematics_en"
        assert rec.artifact_hash == "hash-1234"

    def test_file_artifact_import_plan_dataclass(self):
        plan = FileArtifactImportPlan(
            scope_id="grade4_mathematics_en",
            review_status="approved",
            db_status="synced",
            records=[],
            errors=[],
            created_count=40,
            updated_count=0,
            validation_report_count=40,
            source_count=40,
        )
        assert plan.scope_id == "grade4_mathematics_en"
        assert plan.created_count == 40
        assert len(plan.errors) == 0

    def test_file_artifact_import_batch_plan_to_manifest(self):
        batch_plan = FileArtifactImportBatchPlan(
            scope_count=3,
            stage_unlocked=2,
            production_unlocked=1,
            total_records=120,
            scopes_with_errors=0,
            plans=[],
        )
        manifest = batch_plan.to_manifest()
        assert manifest["schema_version"] == "1.0"
        summary = manifest["summary"]
        assert summary["scope_count"] == 3
        assert summary["stage_unlocked"] == 2
        assert summary["total_records"] == 120
