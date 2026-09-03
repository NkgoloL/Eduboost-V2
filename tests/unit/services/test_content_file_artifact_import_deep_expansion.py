"""Comprehensive unit tests for ContentFileArtifactImport data models, batch plans, and service methods."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentLayer,
)
from app.services.content_file_artifact_import import (
    _LAYER_SPECS,
    ContentFileArtifactImportService,
    FileArtifactImportBatchPlan,
    FileArtifactImportPlan,
    FileArtifactImportRecord,
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

    def test_file_artifact_import_batch_plan_to_manifest_and_rollback(self):
        rec = FileArtifactImportRecord(
            artifact_id=uuid.uuid4(),
            scope_id="term_1_maths",
            layer="diagnostic_items",
            artifact_type="diagnostic_item",
            caps_ref="4.M.1.1",
            artifact_hash="hash_123",
            status="approved",
            source_document_id="doc-1",
            payload_json={"item": 1},
        )
        plan = FileArtifactImportPlan(
            scope_id="term_1_maths",
            review_status="approved",
            db_status="approved",
            records=[rec],
            errors=[],
        )
        batch_plan = FileArtifactImportBatchPlan(
            scope_count=1,
            stage_unlocked=1,
            production_unlocked=0,
            total_records=1,
            scopes_with_errors=0,
            plans=[plan],
        )
        manifest = batch_plan.to_manifest()
        assert manifest["schema_version"] == "1.0"
        summary = manifest["summary"]
        assert summary["scope_count"] == 1
        assert summary["stage_unlocked"] == 1
        assert summary["total_records"] == 1

        rb_manifest = batch_plan.to_rollback_manifest(source_import_manifest_path="/tmp/manifest.json")
        assert rb_manifest["source_import_manifest_path"] == "/tmp/manifest.json"
        assert rb_manifest["summary"]["rollback_supported"] is True


class TestContentFileArtifactImportServicePlanning:
    def test_plan_scope_import_branches(self, tmp_path: Path):
        mock_registry = MagicMock()
        mock_review_svc = MagicMock()
        mock_lesson_quality = MagicMock()

        service = ContentFileArtifactImportService(
            project_root=tmp_path,
            registry=mock_registry,
            review_service=mock_review_svc,
            lesson_quality_service=mock_lesson_quality,
        )

        # 1. Unknown scope_ids in plan_scope_imports -> LookupError
        mock_registry.list_scopes.return_value = [
            SimpleNamespace(scope_id="term_1_maths", status=SimpleNamespace(value="active"))
        ]
        with pytest.raises(LookupError, match="Unknown content scopes"):
            service.plan_scope_imports(scope_ids=["invalid_scope"])

        # 2. plan_scope_import with missing files & quarantined lessons
        mock_registry.get_scope.return_value = SimpleNamespace(
            scope_id="term_1_maths",
            grade=4,
            subject_code="MATH",
            language="en",
            source_documents=["doc-1"],
            artifact_paths={
                "diagnostic_items": "artifacts/items.json",
                "lessons": "artifacts/lessons.json",
                "assessment_blueprints": "artifacts/missing_blueprints.json",
            },
        )
        mock_review_svc.review_status.return_value = SimpleNamespace(
            status="in_review",
            stage_unlocked=False,
            production_unlocked=False,
            stage_blockers=["blocker-1"],
        )
        mock_lesson_quality.audit_scope.return_value = SimpleNamespace(
            quarantined=True,
            blockers=["bad_readability"],
        )

        items_path = tmp_path / "artifacts" / "items.json"
        items_path.parent.mkdir(parents=True, exist_ok=True)
        items_path.write_text(json.dumps({
            "items": [
                {"caps_ref": "4.M.1.1", "stem": "2+2=?"},
                {"caps_ref": "4.M.1.1", "stem": "3+3=?"},
            ]
        }), encoding="utf-8")

        plan = service.plan_scope_import("term_1_maths", max_records_per_layer=1)
        assert plan.scope_id == "term_1_maths"
        assert plan.db_status == ContentArtifactStatus.PENDING_REVIEW.value
        assert len(plan.records) == 1
        assert any("study_plan_templates path is missing" in e for e in plan.errors)
        assert any("missing: artifacts/missing_blueprints.json" in e for e in plan.errors)
        assert any("bad_readability" in e for e in plan.errors)


class TestContentFileArtifactImportServiceExecution:
    @pytest.mark.asyncio
    async def test_import_scope_files_execution(self, tmp_path: Path):
        mock_registry = MagicMock()
        mock_review_svc = MagicMock()
        mock_lesson_quality = MagicMock()

        service = ContentFileArtifactImportService(
            project_root=tmp_path,
            registry=mock_registry,
            review_service=mock_review_svc,
            lesson_quality_service=mock_lesson_quality,
        )

        mock_registry.get_scope.return_value = SimpleNamespace(
            scope_id="term_1_maths",
            grade=4,
            subject_code="MATH",
            language="en",
            source_documents=["doc-1"],
            artifact_paths={"diagnostic_items": "artifacts/items.json"},
        )
        mock_review_svc.review_status.return_value = SimpleNamespace(
            status="approved",
            stage_unlocked=True,
            production_unlocked=True,
            stage_blockers=[],
        )
        mock_lesson_quality.audit_scope.return_value = SimpleNamespace(quarantined=False, blockers=[])

        items_path = tmp_path / "artifacts" / "items.json"
        items_path.parent.mkdir(parents=True, exist_ok=True)
        items_path.write_text(json.dumps({"items": [{"caps_ref": "4.M.1.1", "stem": "1+1=?"}]}), encoding="utf-8")

        session = AsyncMock()

        # 1. dry_run = True
        dry_plan = await service.import_scope_files(session, "term_1_maths", actor_id="admin", dry_run=True)
        assert dry_plan.created_count == 0
        assert len(dry_plan.records) == 1

        # 2. dry_run = False (new artifact creation)
        with patch.object(service, "_existing_artifact", return_value=None):
            with patch.object(service, "_has_source", return_value=False):
                with patch.object(service, "_has_validation_report", return_value=False):
                    exec_plan = await service.import_scope_files(
                        session, "term_1_maths", actor_id="admin", dry_run=False
                    )
                    assert exec_plan.created_count == 1
                    assert exec_plan.source_count == 1
                    assert exec_plan.validation_report_count == 1
                    session.flush.assert_called()

        # 3. dry_run = False (existing artifact update)
        mock_existing = SimpleNamespace(
            status=ContentArtifactStatus.PENDING_REVIEW,
            artifact_json={},
            source_snapshot_hash="",
            provider="",
            model="",
            prompt_version="",
            quality_score=0.0,
            safety_status="",
            answer_key_verified=True,
            caps_alignment_score=0.0,
        )
        with patch.object(service, "_existing_artifact", return_value=mock_existing):
            with patch.object(service, "_has_source", return_value=True):
                with patch.object(service, "_has_validation_report", return_value=True):
                    upd_plan = await service.import_scope_files(
                        session, "term_1_maths", actor_id="admin", dry_run=False
                    )
                    assert upd_plan.updated_count == 1
                    assert upd_plan.created_count == 0
