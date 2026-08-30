"""Comprehensive unit tests for ContentStagingReadiness models, enums, and summaries."""
from __future__ import annotations

import pytest

from app.services.content_staging_readiness import (
    StagingReadinessStatus,
    BlockerSeverity,
    ScopeBlocker,
    LayerReadinessSummary,
)


class TestStagingReadinessModels:
    def test_staging_readiness_status_enums(self):
        assert StagingReadinessStatus.READY_FOR_STAGING == "ready_for_staging"
        assert StagingReadinessStatus.PARTIALLY_STAGEABLE == "partially_stageable"
        assert StagingReadinessStatus.BLOCKED_BY_COVERAGE == "blocked_by_coverage"
        assert StagingReadinessStatus.BLOCKED_BY_REVIEW == "blocked_by_review"
        assert StagingReadinessStatus.BLOCKED_BY_PROVENANCE == "blocked_by_provenance"
        assert StagingReadinessStatus.BLOCKED_BY_VALIDATION == "blocked_by_validation"
        assert StagingReadinessStatus.BLOCKED_BY_SOURCE_QUALITY == "blocked_by_source_quality"
        assert StagingReadinessStatus.BLOCKED_BY_LICENSE == "blocked_by_license"
        assert StagingReadinessStatus.BLOCKED_BY_MISSING_TARGETS == "blocked_by_missing_targets"
        assert StagingReadinessStatus.BLOCKED_BY_MISSING_SCOPE == "blocked_by_missing_scope"
        assert StagingReadinessStatus.NOT_CONFIGURED == "not_configured"

    def test_blocker_severity_enums(self):
        assert BlockerSeverity.INFO == "info"
        assert BlockerSeverity.WARNING == "warning"
        assert BlockerSeverity.BLOCKING == "blocking"

    def test_scope_blocker_model(self):
        blocker = ScopeBlocker(
            code="INSUFFICIENT_APPROVED_ITEMS",
            severity=BlockerSeverity.BLOCKING,
            layer="diagnostic_items",
            caps_ref="4.M.1.1",
            required=40,
            approved=25,
            message="Scope requires 40 approved items, found 25",
        )
        assert blocker.code == "INSUFFICIENT_APPROVED_ITEMS"
        assert blocker.severity == BlockerSeverity.BLOCKING
        assert blocker.required == 40
        assert blocker.approved == 25

    def test_layer_readiness_summary_model(self):
        summary = LayerReadinessSummary(
            layer="diagnostic_items",
            caps_ref="4.M.1.1",
            target=40,
            approved=40,
            stageable=40,
            status=StagingReadinessStatus.READY_FOR_STAGING,
        )
        assert summary.layer == "diagnostic_items"
        assert summary.target == 40
        assert summary.approved == 40
        assert summary.status == StagingReadinessStatus.READY_FOR_STAGING
