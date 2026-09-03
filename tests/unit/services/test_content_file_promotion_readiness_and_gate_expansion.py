"""Batch 207: Unit tests for content_file_promotion_readiness and content_production_promotion_gate dataclasses and logic."""
import pytest
import uuid
from pathlib import Path
from unittest.mock import MagicMock

from app.domain.content_scope import ContentScopeStatus
from app.services.content_file_promotion_readiness import (
    PromotionReadinessResult,
    ContentFilePromotionReadinessService,
    _LAYER_PATH_KEYS,
)
from app.services.content_production_promotion_gate import (
    ProductionGateStatus,
    ProductionGateBlocker,
    ProductionGateReport,
)


# ─────────────────────────────────────────────
# ProductionGate Dataclasses & Enums
# ─────────────────────────────────────────────


class TestProductionGateEnumsAndDataclasses:
    def test_production_gate_status_values(self):
        assert ProductionGateStatus.PROMOTABLE.value == "promotable"
        assert ProductionGateStatus.BLOCKED_BY_COVERAGE.value == "blocked_by_coverage"
        assert ProductionGateStatus.BLOCKED_BY_REVIEW.value == "blocked_by_review"
        assert ProductionGateStatus.BLOCKED_BY_VALIDATION.value == "blocked_by_validation"
        assert ProductionGateStatus.BLOCKED_BY_STAGING.value == "blocked_by_staging"
        assert ProductionGateStatus.BLOCKED_BY_LICENSE.value == "blocked_by_license"

    def test_production_gate_blocker_fields(self):
        uid = uuid.uuid4()
        blocker = ProductionGateBlocker(
            type="license_missing",
            message="License not attached",
            artifact_id=uid,
            caps_ref="4.M.1.1",
        )
        assert blocker.type == "license_missing"
        assert blocker.message == "License not attached"
        assert blocker.artifact_id == uid
        assert blocker.caps_ref == "4.M.1.1"

    def test_production_gate_report_structure(self):
        report = ProductionGateReport(
            scope_id="scope-01",
            status=ProductionGateStatus.PROMOTABLE,
            blockers=[],
        )
        assert report.scope_id == "scope-01"
        assert report.status == ProductionGateStatus.PROMOTABLE
        assert len(report.blockers) == 0


# ─────────────────────────────────────────────
# PromotionReadinessResult & Service
# ─────────────────────────────────────────────


class TestPromotionReadinessResult:
    def test_promotion_readiness_result_immutability(self):
        res = PromotionReadinessResult(
            scope_id="scope-1",
            learner_visible=True,
            source_ready=True,
            staging_eligible=True,
            production_eligible=True,
            blockers=[],
            manifest={"schema": "1.0"},
        )
        assert res.scope_id == "scope-1"
        assert res.staging_eligible is True
        with pytest.raises(Exception):
            res.staging_eligible = False


class TestContentFilePromotionReadinessService:
    def test_layer_path_keys_mapping(self):
        assert "topic_map" in _LAYER_PATH_KEYS
        assert "diagnostic_items" in _LAYER_PATH_KEYS
        assert "lessons" in _LAYER_PATH_KEYS
        assert "assessment_blueprints" in _LAYER_PATH_KEYS
        assert "study_plan_templates" in _LAYER_PATH_KEYS

    def test_evaluate_scope_basic_flow_with_mocks(self):
        mock_registry = MagicMock()
        mock_scope = MagicMock()
        mock_scope.scope_id = "test-scope"
        mock_scope.status = ContentScopeStatus.ACTIVE
        mock_scope.grade = 4
        mock_scope.phase = "Intermediate"
        mock_scope.subject_code = "MATH"
        mock_scope.subject = "Mathematics"
        mock_scope.language = "en"
        mock_scope.topic_map_path = "data/topic_map.json"
        mock_scope.artifact_paths = {
            "diagnostic_items": "data/diag.json",
            "lessons": "data/lessons.json",
            "assessment_blueprints": "data/blueprints.json",
            "study_plan_templates": "data/plans.json",
        }
        mock_registry.get_scope.return_value = mock_scope

        mock_review = MagicMock()
        mock_review_status = MagicMock()
        mock_review_status.stage_unlocked = True
        mock_review_status.stage_blockers = []
        mock_review_status.production_blockers = []
        mock_review.review_status.return_value = mock_review_status

        mock_quality = MagicMock()
        mock_audit = MagicMock()
        mock_audit.quarantined = False
        mock_audit.blockers = []
        mock_quality.audit_scope.return_value = mock_audit

        service = ContentFilePromotionReadinessService(
            registry=mock_registry,
            review_service=mock_review,
            lesson_quality_service=mock_quality,
        )

        # Mock the file system methods on service
        service._layer_manifest = MagicMock(return_value={"exists": True, "record_count": 10, "path": "p", "sha256": "abc"})

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("app.services.content_file_promotion_readiness.generation_ready", lambda *a, **kw: True)
            res = service.evaluate_scope("test-scope")

        assert isinstance(res, PromotionReadinessResult)
        assert res.scope_id == "test-scope"
        assert res.learner_visible is True
        assert res.source_ready is True
        assert res.staging_eligible is True
        assert res.production_eligible is True
        assert len(res.blockers) == 0

    def test_evaluate_scope_blocked_when_quarantined(self):
        mock_registry = MagicMock()
        mock_scope = MagicMock()
        mock_scope.scope_id = "test-scope"
        mock_scope.status = ContentScopeStatus.ACTIVE
        mock_scope.grade = 4
        mock_scope.phase = "Intermediate"
        mock_scope.subject_code = "MATH"
        mock_scope.subject = "Mathematics"
        mock_scope.language = "en"
        mock_scope.topic_map_path = "data/topic_map.json"
        mock_scope.artifact_paths = {}
        mock_registry.get_scope.return_value = mock_scope

        mock_review = MagicMock()
        mock_quality = MagicMock()
        mock_audit = MagicMock()
        mock_audit.quarantined = True
        mock_audit.blockers = ["Lesson quality below acceptable threshold"]
        mock_quality.audit_scope.return_value = mock_audit

        service = ContentFilePromotionReadinessService(
            registry=mock_registry,
            review_service=mock_review,
            lesson_quality_service=mock_quality,
        )
        service._layer_manifest = MagicMock(return_value={"exists": True, "record_count": 10})

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("app.services.content_file_promotion_readiness.generation_ready", lambda *a, **kw: True)
            res = service.evaluate_scope("test-scope")

        assert res.staging_eligible is False
        assert res.production_eligible is False
        assert "Lesson quality below acceptable threshold" in res.blockers

    def test_evaluate_scope_review_and_draft_statuses(self):
        mock_registry = MagicMock()
        mock_scope_rev = MagicMock(
            scope_id="rev-scope",
            status=ContentScopeStatus.REVIEW,
            grade=4,
            phase="Intermediate",
            subject_code="MATH",
            subject="Mathematics",
            language="en",
            topic_map_path="data/topic_map.json",
            artifact_paths={},
            caps_refs=["4.MATH.1.1"],
        )
        mock_registry.get_scope.return_value = mock_scope_rev

        mock_review = MagicMock()
        mock_review_status = MagicMock(
            stage_unlocked=False,
            stage_blockers=["Decision pending"],
            production_blockers=["Educator approval required"],
        )
        mock_review.review_status.return_value = mock_review_status

        mock_quality = MagicMock()
        mock_quality.audit_scope.return_value = MagicMock(quarantined=False, blockers=[])

        service = ContentFilePromotionReadinessService(
            registry=mock_registry,
            review_service=mock_review,
            lesson_quality_service=mock_quality,
        )
        service._layer_manifest = MagicMock(return_value={"exists": True, "record_count": 10})

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("app.services.content_file_promotion_readiness.generation_ready", lambda *a, **kw: False)
            res = service.evaluate_scope("rev-scope")

        assert res.source_ready is False
        assert res.staging_eligible is False
        assert any("requires dev_approved or educator approval" in b for b in res.blockers)
        assert any("Scope source material is not generation-ready" in b for b in res.blockers)

    def test_build_all_and_write_manifests(self, tmp_path: Path):
        mock_registry = MagicMock()
        mock_scope = MagicMock(scope_id="s1")
        mock_registry.list_scopes.return_value = [mock_scope]

        service = ContentFilePromotionReadinessService(registry=mock_registry)
        mock_res = PromotionReadinessResult(
            scope_id="s1",
            learner_visible=True,
            source_ready=True,
            staging_eligible=True,
            production_eligible=True,
            blockers=[],
            manifest={"scope_id": "s1", "lesson_quality": {"quarantined": False}},
        )
        service.evaluate_scope = MagicMock(return_value=mock_res)

        all_summary = service.build_all()
        assert all_summary["summary"]["scope_count"] == 1
        assert all_summary["summary"]["staging_eligible"] == 1

        written = service.write_manifests(output_dir=tmp_path)
        assert (tmp_path / "s1_promotion_readiness.json").exists()
        assert (tmp_path / "all_scopes_promotion_readiness_summary.json").exists()

    def test_layer_manifest_and_counts(self, tmp_path: Path):
        service = ContentFilePromotionReadinessService(project_root=tmp_path)

        # 1. No relative path
        m_none = service._layer_manifest("s1", "lessons", None)
        assert m_none["exists"] is False

        # 2. File not existing
        m_missing = service._layer_manifest("s1", "lessons", "missing.json")
        assert m_missing["exists"] is False

        # 3. File exists with valid json
        import json
        lessons_file = tmp_path / "lessons.json"
        lessons_file.write_text(json.dumps({"lessons": [{"status": "approved"}, {"status": "pending"}]}))
        m_valid = service._layer_manifest("s1", "lessons", "lessons.json")
        assert m_valid["exists"] is True
        assert m_valid["record_count"] == 2
        assert m_valid["approved_count"] == 1
        assert m_valid["idempotency_key"] is not None

        # 4. _counts_for_layer for other types
        from app.services.content_file_promotion_readiness import _counts_for_layer

        # topic_map
        tmap = {"terms": [{"topics": [{"caps_ref": "4.MATH.1.1", "subtopics": [{"caps_ref": "4.MATH.1.2"}]}]}]}
        assert _counts_for_layer("topic_map", tmap) == (2, 2, 2)

        # blueprints
        bps = {"blueprints": [{"review_status": "review_ready"}]}
        assert _counts_for_layer("assessment_blueprints", bps) == (1, 0, 1)

        # study plans
        plans = {"topic_sequence": [{"status": "approved"}]}
        assert _counts_for_layer("study_plan_templates", plans) == (1, 1, 1)

        # unknown
        assert _counts_for_layer("unknown_layer", {}) == (0, 0, 0)
