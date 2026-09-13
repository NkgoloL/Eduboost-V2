"""Comprehensive unit tests covering file artifact import, lesson quality, and promotion readiness services."""
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.content_scope import ContentScopeStatus
from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentLayer,
    ContentValidationReport,
)
from app.services.content_file_artifact_import import (
    ContentFileArtifactImportService,
    FileArtifactImportBatchPlan,
    FileArtifactImportPlan,
    FileArtifactImportRecord,
    _batch_manifest_id,
    _caps_ref_for,
    _layer_artifact_ids,
    _layer_counts,
)
from app.services.content_file_lesson_quality import (
    ContentFileLessonQualityService,
    LessonFileQualityResult,
    _now_utc as quality_now_utc,
    _write_json as quality_write_json,
)
from app.services.content_file_promotion_readiness import (
    ContentFilePromotionReadinessService,
    PromotionReadinessResult,
    _counts_for_layer,
    _now_utc as readiness_now_utc,
    _sha256,
    _write_json as readiness_write_json,
)


# ============================================================================
# ContentFileLessonQualityService Tests
# ============================================================================
def test_content_file_lesson_quality_service(tmp_path: Path):
    registry = MagicMock()
    validator = MagicMock()

    service = ContentFileLessonQualityService(
        project_root=tmp_path,
        registry=registry,
        validator=validator,
    )

    # 1. Unconfigured lessons path
    scope_no_path = MagicMock(scope_id="scope_empty", artifact_paths={})
    registry.get_scope.return_value = scope_no_path
    res_no_path = service.audit_scope("scope_empty")
    assert isinstance(res_no_path, LessonFileQualityResult)
    assert res_no_path.exists is False
    assert res_no_path.quarantined is True
    assert "not configured" in res_no_path.blockers[0]

    # 2. Missing file on disk
    scope_missing = MagicMock(
        scope_id="scope_missing",
        artifact_paths={"lessons": "data/missing_lessons.json"},
    )
    registry.get_scope.return_value = scope_missing
    res_missing = service.audit_scope("scope_missing")
    assert res_missing.exists is False
    assert "missing" in res_missing.blockers[0]

    # 3. Existing file - validation failure
    lessons_rel = "data/lessons.json"
    lessons_file = tmp_path / lessons_rel
    lessons_file.parent.mkdir(parents=True, exist_ok=True)
    lessons_file.write_text(json.dumps({"lessons": [{"id": 1}]}), encoding="utf-8")

    scope_ok = MagicMock(
        scope_id="scope_math",
        subject_code="MATH",
        subject="Mathematics",
        source_documents=["doc1"],
        artifact_paths={"lessons": lessons_rel},
    )
    registry.get_scope.return_value = scope_ok

    mock_issue = MagicMock(lesson_id="L1", caps_ref="4.M.1", field="body", reason="short")
    fail_report = MagicMock(
        passed=False,
        lesson_count=5,
        failed_lesson_count=2,
        aggregate={"short_body": 2},
        issues=[mock_issue],
    )
    validator.validate_file_payload.return_value = fail_report

    res_fail = service.audit_scope("scope_math")
    assert res_fail.passed is False
    assert res_fail.quarantined is True
    assert res_fail.failed_lesson_count == 2
    assert "failed quality audit" in res_fail.blockers[0]
    assert len(res_fail.issues) == 1
    assert res_fail.issues[0]["lesson_id"] == "L1"

    # 4. Existing file - validation success
    pass_report = MagicMock(
        passed=True,
        lesson_count=5,
        failed_lesson_count=0,
        aggregate={},
        issues=[],
    )
    validator.validate_file_payload.return_value = pass_report
    res_pass = service.audit_scope("scope_math")
    assert res_pass.passed is True
    assert res_pass.quarantined is False
    assert len(res_pass.blockers) == 0

    # 5. build_all and write_manifests
    registry.list_scopes.return_value = [scope_ok]
    manifest_out = tmp_path / "out_manifests"
    summary = service.write_manifests(output_dir=manifest_out)
    assert summary["summary"]["scope_count"] == 1
    assert summary["summary"]["lesson_files_present"] == 1
    assert (manifest_out / "scope_math_lesson_quality.json").exists()
    assert (manifest_out / "all_scopes_lesson_quality_summary.json").exists()

    assert isinstance(quality_now_utc(), str)
    p = tmp_path / "test.json"
    quality_write_json(p, {"k": "v"})
    assert json.loads(p.read_text())["k"] == "v"


# ============================================================================
# ContentFilePromotionReadinessService Tests
# ============================================================================
def test_content_file_promotion_readiness_service(tmp_path: Path):
    registry = MagicMock()
    review_service = MagicMock()
    lesson_quality_service = MagicMock()

    service = ContentFilePromotionReadinessService(
        project_root=tmp_path,
        registry=registry,
        review_service=review_service,
        lesson_quality_service=lesson_quality_service,
    )

    # 1. Helpers
    t_map = {
        "terms": [
            {
                "topics": [
                    {
                        "caps_ref": "4.M.1",
                        "subtopics": [{"caps_ref": "4.M.1.1"}, {"caps_ref": None}],
                    }
                ]
            }
        ]
    }
    assert _counts_for_layer("topic_map", t_map) == (2, 2, 2)
    assert _counts_for_layer("diagnostic_items", {"items": [{"status": "approved"}, {"status": "pending"}]}) == (2, 1, 1)
    assert _counts_for_layer("lessons", {"lessons": [{"review_status": "human_reviewed"}]}) == (1, 0, 1)
    assert _counts_for_layer("assessment_blueprints", {"blueprints": []}) == (0, 0, 0)
    assert _counts_for_layer("study_plan_templates", {"topic_sequence": [{"status": "approved"}]}) == (1, 1, 1)
    assert _counts_for_layer("unknown_layer", {}) == (0, 0, 0)

    f_hash = tmp_path / "sample.txt"
    f_hash.write_bytes(b"hello eduboost")
    assert _sha256(f_hash).startswith("sha256:")
    assert isinstance(readiness_now_utc(), str)

    # 2. evaluate_scope missing files
    scope_missing = MagicMock(
        scope_id="scope_missing",
        status=ContentScopeStatus.REVIEW,
        grade=4,
        phase="intermediate",
        subject_code="MATH",
        subject="Mathematics",
        language="en",
        caps_refs=["4.M.1"],
        topic_map_path="missing_map.json",
        artifact_paths={"diagnostic_items": "missing_diag.json"},
    )
    registry.get_scope.return_value = scope_missing

    review_evidence = MagicMock(
        status="pending",
        approved=False,
        stage_unlocked=False,
        production_unlocked=False,
        manifest_path=None,
        stage_blockers=["stage blocked"],
        production_blockers=["prod blocked"],
        blockers=["stage blocked", "prod blocked"],
    )
    review_service.review_status.return_value = review_evidence

    lesson_q = MagicMock(
        passed=False,
        quarantined=True,
        lesson_count=1,
        failed_lesson_count=1,
        blockers=["Lesson audit failure"],
        aggregate={},
    )
    lesson_quality_service.audit_scope.return_value = lesson_q

    from unittest.mock import patch
    with patch("app.services.content_file_promotion_readiness.generation_ready", return_value=False):
        res_blocked = service.evaluate_scope("scope_missing")
        assert isinstance(res_blocked, PromotionReadinessResult)
        assert res_blocked.staging_eligible is False
        assert res_blocked.production_eligible is False
        assert "Scope source material is not generation-ready." in res_blocked.blockers
        assert "Lesson audit failure" in res_blocked.blockers

    # 3. evaluate_scope active & fully eligible
    t_file = tmp_path / "data" / "t_map.json"
    t_file.parent.mkdir(parents=True, exist_ok=True)
    t_file.write_text(json.dumps(t_map), encoding="utf-8")

    d_file = tmp_path / "data" / "diag.json"
    d_file.write_text(json.dumps({"items": [{"status": "approved"}]}), encoding="utf-8")

    l_file = tmp_path / "data" / "lessons.json"
    l_file.write_text(json.dumps({"lessons": [{"status": "approved"}]}), encoding="utf-8")

    b_file = tmp_path / "data" / "blueprints.json"
    b_file.write_text(json.dumps({"blueprints": [{"status": "approved"}]}), encoding="utf-8")

    s_file = tmp_path / "data" / "study.json"
    s_file.write_text(json.dumps({"topic_sequence": [{"status": "approved"}]}), encoding="utf-8")

    scope_active = MagicMock(
        scope_id="scope_active",
        status=ContentScopeStatus.ACTIVE,
        grade=4,
        phase="intermediate",
        subject_code="MATH",
        subject="Mathematics",
        language="en",
        caps_refs=["4.M.1"],
        topic_map_path="data/t_map.json",
        artifact_paths={
            "diagnostic_items": "data/diag.json",
            "lessons": "data/lessons.json",
            "assessment_blueprints": "data/blueprints.json",
            "study_plan_templates": "data/study.json",
        },
    )
    registry.get_scope.return_value = scope_active
    review_evidence_ok = MagicMock(
        status="approved",
        approved=True,
        stage_unlocked=True,
        production_unlocked=True,
        manifest_path=tmp_path / "data" / "rev.json",
        stage_blockers=[],
        production_blockers=[],
        blockers=[],
    )
    review_service.review_status.return_value = review_evidence_ok
    lesson_q_ok = MagicMock(
        passed=True,
        quarantined=False,
        lesson_count=1,
        failed_lesson_count=0,
        blockers=[],
        aggregate={},
    )
    lesson_quality_service.audit_scope.return_value = lesson_q_ok

    with patch("app.services.content_file_promotion_readiness.generation_ready", return_value=True):
        res_ok = service.evaluate_scope("scope_active")
        assert res_ok.staging_eligible is True
        assert res_ok.production_eligible is True
        assert len(res_ok.blockers) == 0

        # build_all and write_manifests
        registry.list_scopes.return_value = [scope_active]
        out_dir = tmp_path / "prom_manifests"
        summary = service.write_manifests(output_dir=out_dir)
        assert summary["summary"]["scope_count"] == 1
        assert summary["summary"]["staging_eligible"] == 1
        assert summary["summary"]["production_eligible"] == 1
        assert (out_dir / "scope_active_promotion_readiness.json").exists()


# ============================================================================
# ContentFileArtifactImportService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_file_artifact_import_service(tmp_path: Path):
    registry = MagicMock()
    review_service = MagicMock()
    lesson_quality_service = MagicMock()

    service = ContentFileArtifactImportService(
        project_root=tmp_path,
        registry=registry,
        review_service=review_service,
        lesson_quality_service=lesson_quality_service,
    )

    # 1. Helpers
    assert _caps_ref_for("items", {"caps_ref": "4.M.1"}) == "4.M.1"
    assert _caps_ref_for("blueprints", {"selection_rules": {"caps_refs": ["5.M.2"]}}) == "5.M.2"
    assert _caps_ref_for("blueprints", {}) is None

    rec1 = FileArtifactImportRecord(
        artifact_id=uuid.uuid4(),
        scope_id="scope1",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        caps_ref="4.M.1",
        artifact_hash="hash1",
        status="pending_review",
        source_document_id="doc1",
        payload_json={"q": 1},
    )
    rec2 = FileArtifactImportRecord(
        artifact_id=uuid.uuid4(),
        scope_id="scope1",
        layer="lessons",
        artifact_type="lesson",
        caps_ref="4.M.1",
        artifact_hash="hash2",
        status="pending_review",
        source_document_id="doc1",
        payload_json={"body": "text"},
    )
    assert _layer_counts([rec1, rec2]) == {"diagnostic_items": 1, "lessons": 1}
    assert str(rec1.artifact_id) in _layer_artifact_ids([rec1, rec2])["diagnostic_items"]

    plan_dummy = FileArtifactImportPlan(
        scope_id="scope1",
        review_status="approved",
        db_status="approved",
        records=[rec1, rec2],
    )
    assert isinstance(_batch_manifest_id([plan_dummy]), str)

    batch_plan = FileArtifactImportBatchPlan(
        scope_count=1,
        stage_unlocked=1,
        production_unlocked=1,
        total_records=2,
        scopes_with_errors=0,
        plans=[plan_dummy],
    )
    manifest = batch_plan.to_manifest()
    assert manifest["summary"]["total_records"] == 2
    rb_manifest = batch_plan.to_rollback_manifest(source_import_manifest_path="/data/manifest.json")
    assert rb_manifest["summary"]["rollback_supported"] is True

    # 2. plan_scope_import missing files / quarantined
    scope = MagicMock(
        scope_id="scope_math",
        grade=4,
        subject_code="MATH",
        language="en",
        source_documents=["doc1"],
        artifact_paths={
            "diagnostic_items": "data/diag.json",
            "lessons": "data/lessons.json",
            "assessment_blueprints": "data/blueprints.json",
            "study_plan_templates": "data/study.json",
        },
    )
    registry.get_scope.return_value = scope
    review_service.review_status.return_value = MagicMock(
        stage_unlocked=False,
        production_unlocked=False,
        status="pending",
        stage_blockers=["stage blocker"],
    )
    lesson_quality_service.audit_scope.return_value = MagicMock(
        quarantined=True,
        blockers=["quarantined lessons"],
    )

    # Missing json files
    plan_missing = service.plan_scope_import("scope_math")
    assert len(plan_missing.records) == 0
    assert "stage blocker" in plan_missing.errors
    assert "quarantined lessons" in plan_missing.errors

    # 3. plan_scope_import with valid files
    for key, fname in [
        ("diagnostic_items", "diag.json"),
        ("lessons", "lessons.json"),
        ("assessment_blueprints", "blueprints.json"),
        ("study_plan_templates", "study.json"),
    ]:
        p = tmp_path / "data" / fname
        p.parent.mkdir(parents=True, exist_ok=True)
        items_key = "items" if key == "diagnostic_items" else "lessons" if key == "lessons" else "blueprints" if key == "assessment_blueprints" else "topic_sequence"
        p.write_text(json.dumps({items_key: [{"caps_ref": "4.M.1"}]}), encoding="utf-8")

    review_service.review_status.return_value = MagicMock(
        stage_unlocked=True,
        production_unlocked=True,
        status="approved",
        stage_blockers=[],
    )
    lesson_quality_service.audit_scope.return_value = MagicMock(
        quarantined=False,
        blockers=[],
    )

    plan_valid = service.plan_scope_import("scope_math", max_records_per_layer=1)
    assert len(plan_valid.records) == 4
    assert plan_valid.db_status == "approved"
    assert len(plan_valid.errors) == 0

    # 4. plan_scope_imports batch
    registry.list_scopes.return_value = [scope]
    batch = service.plan_scope_imports(scope_ids=["scope_math"])
    assert batch.scope_count == 1
    assert batch.stage_unlocked == 1

    with pytest.raises(LookupError, match="Unknown content scopes"):
        service.plan_scope_imports(scope_ids=["scope_unknown"])

    # 5. import_scope_files dry run vs wet run
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    # Dry run
    res_dry = await service.import_scope_files(session, "scope_math", actor_id="lead_dev", dry_run=True)
    assert res_dry == plan_valid
    session.add.assert_not_called()

    # Wet run - new artifacts
    session.get.return_value = None
    session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    service._has_source = AsyncMock(return_value=False)
    service._has_validation_report = AsyncMock(return_value=False)

    res_wet = await service.import_scope_files(session, "scope_math", actor_id="lead_dev", dry_run=False)
    assert res_wet.created_count == 4
    assert res_wet.source_count == 4
    assert res_wet.validation_report_count == 4

    # Wet run - update existing artifacts
    service._has_source = AsyncMock(return_value=True)
    service._has_validation_report = AsyncMock(return_value=True)

    existing_art = ContentGenerationArtifact(
        artifact_id=plan_valid.records[0].artifact_id,
        artifact_hash="oldhash",
        status=ContentArtifactStatus.PENDING_REVIEW,
    )
    session.get.return_value = existing_art
    session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock()))  # has source & val report

    res_update = await service.import_scope_files(session, "scope_math", actor_id="lead_dev", dry_run=False)
    assert res_update.updated_count == 4
    assert res_update.created_count == 0

    # 6. Real query helpers on un-mocked service
    real_import = ContentFileArtifactImportService(project_root=tmp_path, registry=registry)
    clean_session = AsyncMock(spec=AsyncSession)
    clean_session.get.return_value = None
    clean_session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=existing_art))
    art_found = await real_import._existing_artifact(clean_session, plan_valid.records[0])
    assert art_found == existing_art

    clean_session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock()))
    assert await real_import._has_source(clean_session, plan_valid.records[0]) is True
    assert await real_import._has_validation_report(clean_session, plan_valid.records[0]) is True


