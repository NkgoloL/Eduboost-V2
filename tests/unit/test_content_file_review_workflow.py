from __future__ import annotations

from pathlib import Path

import pytest

from app.services.content_file_artifact_import import ContentFileArtifactImportService
from app.services.content_file_promotion_readiness import ContentFilePromotionReadinessService
from app.services.content_file_review_workflow import ContentFileReviewWorkflowService

pytestmark = pytest.mark.unit
REPO_ROOT = Path(__file__).resolve().parents[2]


def test_pilot_review_packet_defaults_to_pending_educator_approval(tmp_path: Path) -> None:
    service = ContentFileReviewWorkflowService(project_root=REPO_ROOT, manifest_dir=tmp_path)

    packet = service.build_review_packet("grade5_mathematics_en")
    status = service.review_status("grade5_mathematics_en")

    assert packet["decision"] == "pending"
    assert status.approved is False
    assert "Review decision is not dev_approved or approved." in status.blockers
    assert packet["layer_review"]["diagnostic_items"]["record_count"] == 640


def test_dev_approved_review_packet_unlocks_staging_but_not_production(tmp_path: Path) -> None:
    service = ContentFileReviewWorkflowService(project_root=REPO_ROOT, manifest_dir=tmp_path)

    service.build_review_packet(
        "grade5_mathematics_en",
        reviewer_id="dev-reviewer",
        decision="dev_approved",
        evidence_url="dev-reviewed-generated-artifacts",
    )
    status = service.review_status("grade5_mathematics_en")

    assert status.status == "dev_approved"
    assert status.stage_unlocked is True
    assert status.production_unlocked is False
    assert status.stage_blockers == []
    assert "Educator approval is required for production." in status.production_blockers
    assert "Legal approval is required for production." in status.production_blockers


def test_educator_and_legal_approval_unlocks_production_review_evidence(tmp_path: Path) -> None:
    service = ContentFileReviewWorkflowService(project_root=REPO_ROOT, manifest_dir=tmp_path)

    service.build_review_packet(
        "grade5_mathematics_en",
        reviewer_id="educator-1",
        decision="approved",
        evidence_url="https://evidence.eduboost.co.za/grade5-maths",
        legal_decision="approved",
        legal_evidence_url="https://legal.eduboost.co.za/grade5-maths",
    )
    status = service.review_status("grade5_mathematics_en")

    assert status.approved is True
    assert status.stage_unlocked is True
    assert status.production_unlocked is True
    assert status.blockers == []


def test_placeholder_approval_urls_do_not_unlock_production(tmp_path: Path) -> None:
    service = ContentFileReviewWorkflowService(project_root=REPO_ROOT, manifest_dir=tmp_path)

    service.build_review_packet(
        "grade5_mathematics_en",
        reviewer_id="educator-1",
        decision="approved",
        evidence_url="https://eduboost.example.com/evidence/educator-signoff-grade5-math.pdf",
        legal_decision="approved",
        legal_evidence_url="https://eduboost.example.com/evidence/legal-clearance-grade5-math.pdf",
    )
    status = service.review_status("grade5_mathematics_en")

    assert status.approved is True
    assert status.stage_unlocked is True
    assert status.production_unlocked is False
    assert "Educator approval evidence_url must be a real non-placeholder HTTPS URL." in status.production_blockers
    assert "Legal approval evidence_url must be a real non-placeholder HTTPS URL." in status.production_blockers


def test_import_plan_uses_pending_review_until_educator_approval(tmp_path: Path) -> None:
    review_service = ContentFileReviewWorkflowService(project_root=REPO_ROOT, manifest_dir=tmp_path)
    review_service.build_review_packet("grade5_mathematics_en")
    importer = ContentFileArtifactImportService(project_root=REPO_ROOT, review_service=review_service)

    plan = importer.plan_scope_import("grade5_mathematics_en", max_records_per_layer=2)

    assert plan.db_status == "pending_review"
    assert len(plan.records) == 8
    assert {record.layer for record in plan.records} == {
        "diagnostic_items",
        "lessons",
        "assessment_blueprints",
        "study_plan_templates",
    }


def test_import_plan_switches_to_approved_with_dev_approval(tmp_path: Path) -> None:
    review_service = ContentFileReviewWorkflowService(project_root=REPO_ROOT, manifest_dir=tmp_path)
    review_service.build_review_packet(
        "grade5_mathematics_en",
        reviewer_id="dev-reviewer",
        decision="dev_approved",
        evidence_url="dev-reviewed-generated-artifacts",
    )
    importer = ContentFileArtifactImportService(project_root=REPO_ROOT, review_service=review_service)

    plan = importer.plan_scope_import("grade5_mathematics_en", max_records_per_layer=1)

    assert plan.db_status == "approved"
    assert len(plan.records) == 4
    assert not plan.errors


def test_batch_import_plan_summarizes_dev_approved_review_scopes() -> None:
    importer = ContentFileArtifactImportService(project_root=REPO_ROOT)

    batch = importer.plan_scope_imports(statuses={"review"}, max_records_per_layer=1)
    manifest = batch.to_manifest()

    assert manifest["summary"]["scope_count"] == 50
    assert manifest["summary"]["stage_unlocked"] == 50
    assert manifest["summary"]["production_unlocked"] == 0
    assert manifest["summary"]["total_records"] == 200
    assert manifest["summary"]["scopes_with_errors"] == 0
    grade5 = next(row for row in manifest["scopes"] if row["scope_id"] == "grade5_mathematics_en")
    assert grade5["db_status"] == "approved"
    assert grade5["layers"] == {
        "diagnostic_items": 1,
        "lessons": 1,
        "assessment_blueprints": 1,
        "study_plan_templates": 1,
    }


def test_batch_import_plan_builds_rollback_manifest() -> None:
    importer = ContentFileArtifactImportService(project_root=REPO_ROOT)

    batch = importer.plan_scope_imports(statuses={"review"}, max_records_per_layer=1)
    manifest = batch.to_rollback_manifest(
        source_import_manifest_path="data/generated/import_manifests/all_scopes_file_artifact_import_plan.json"
    )

    assert manifest["summary"]["scope_count"] == 50
    assert manifest["summary"]["artifact_count"] == 200
    assert manifest["summary"]["rollback_supported"] is True
    assert manifest["production_guard"]["production_rollback_applicable"] is False
    grade5 = next(row for row in manifest["scopes"] if row["scope_id"] == "grade5_mathematics_en")
    assert len(grade5["layers"]["diagnostic_items"]) == 1
    assert "delete_content_generation_artifacts_by_artifact_id" in manifest["rollback_actions"]


def test_promotion_readiness_reports_pilot_review_evidence() -> None:
    readiness = ContentFilePromotionReadinessService(project_root=REPO_ROOT).evaluate_scope("grade5_mathematics_en")

    assert readiness.staging_eligible is True
    assert readiness.production_eligible is False
    assert readiness.manifest["review_evidence"]["status"] in {"pending", "dev_approved", "educator_approved"}
    assert any("non-placeholder HTTPS URL" in blocker for blocker in readiness.manifest["review_evidence"]["production_blockers"])
    assert readiness.manifest["review_evidence"]["manifest_path"] == "data/generated/review_manifests/grade5_mathematics_en_educator_review.json"


class _ScalarResult:
    def __init__(self, value=None):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class _ImportSession:
    def __init__(self):
        self.artifacts = {}
        self.sources = {}
        self.reports = {}
        self.added = []
        self.flush_count = 0

    async def get(self, model, key):
        return self.artifacts.get(key)

    async def execute(self, stmt):
        return _ScalarResult(None)

    def has_source_for_import(self, record):
        return (record.artifact_id, record.artifact_hash) in self.sources

    def has_validation_report_for_import(self, record):
        return record.artifact_id in self.reports

    def add(self, obj):
        self.added.append(obj)
        name = obj.__class__.__name__
        if name == "ContentGenerationArtifact":
            self.artifacts[obj.artifact_id] = obj
        elif name == "ContentArtifactSource":
            self.sources[(obj.artifact_id, obj.source_hash)] = obj
        elif name == "ContentValidationReport":
            self.reports[obj.artifact_id] = obj

    async def flush(self):
        self.flush_count += 1


@pytest.mark.asyncio
async def test_file_artifact_import_is_idempotent_for_pilot_scope(tmp_path: Path) -> None:
    review_service = ContentFileReviewWorkflowService(project_root=REPO_ROOT, manifest_dir=tmp_path)
    review_service.build_review_packet("grade5_mathematics_en")
    importer = ContentFileArtifactImportService(project_root=REPO_ROOT, review_service=review_service)
    session = _ImportSession()

    first = await importer.import_scope_files(
        session,
        "grade5_mathematics_en",
        actor_id="admin-1",
        max_records_per_layer=1,
        dry_run=False,
    )
    second = await importer.import_scope_files(
        session,
        "grade5_mathematics_en",
        actor_id="admin-1",
        max_records_per_layer=1,
        dry_run=False,
    )

    assert first.created_count == 4
    assert first.source_count == 4
    assert first.validation_report_count == 4
    assert second.created_count == 0
    assert second.updated_count == 4
    assert second.source_count == 0
    assert second.validation_report_count == 0
    assert len(session.artifacts) == 4
    assert len(session.sources) == 4
    assert len(session.reports) == 4
