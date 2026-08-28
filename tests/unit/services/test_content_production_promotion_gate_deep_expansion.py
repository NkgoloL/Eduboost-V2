"""Comprehensive unit tests for ContentProductionPromotionGate enums, blockers, and reports."""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock
import pytest

from app.services.content_production_promotion_gate import (
    ProductionGateStatus,
    ProductionGateBlocker,
    ProductionGateReport,
    ContentProductionPromotionGate,
)


class TestProductionGateModels:
    def test_gate_status_enums(self):
        assert ProductionGateStatus.PROMOTABLE == "promotable"
        assert ProductionGateStatus.BLOCKED_BY_COVERAGE == "blocked_by_coverage"
        assert ProductionGateStatus.BLOCKED_BY_REVIEW == "blocked_by_review"
        assert ProductionGateStatus.BLOCKED_BY_VALIDATION == "blocked_by_validation"
        assert ProductionGateStatus.BLOCKED_BY_PROVENANCE == "blocked_by_provenance"
        assert ProductionGateStatus.BLOCKED_BY_STAGING == "blocked_by_staging"
        assert ProductionGateStatus.BLOCKED_BY_SOURCE_QUALITY == "blocked_by_source_quality"
        assert ProductionGateStatus.BLOCKED_BY_LICENSE == "blocked_by_license"
        assert ProductionGateStatus.BLOCKED_BY_CONFIGURATION == "blocked_by_configuration"

    def test_gate_blocker_dataclass(self):
        aid = uuid.uuid4()
        blocker = ProductionGateBlocker(
            type="coverage",
            message="Minimum item threshold not met",
            artifact_id=aid,
            caps_ref="4.M.1.1",
        )
        assert blocker.type == "coverage"
        assert blocker.artifact_id == aid
        assert blocker.caps_ref == "4.M.1.1"

    def test_gate_report_dataclass(self):
        report = ProductionGateReport(
            scope_id="grade4_maths",
            status=ProductionGateStatus.PROMOTABLE,
            blockers=[],
            coverage_summary={"ratio": 1.0},
            staging_summary={"verified": True},
        )
        assert report.scope_id == "grade4_maths"
        assert report.status == ProductionGateStatus.PROMOTABLE
        assert len(report.blockers) == 0

    def test_gate_init(self):
        mock_coverage = MagicMock()
        gate = ContentProductionPromotionGate(coverage_service=mock_coverage)
        assert gate.coverage_service == mock_coverage
