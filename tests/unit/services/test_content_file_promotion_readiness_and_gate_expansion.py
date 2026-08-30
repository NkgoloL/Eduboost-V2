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
