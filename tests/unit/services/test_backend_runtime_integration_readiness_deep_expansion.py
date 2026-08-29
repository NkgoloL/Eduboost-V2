"""Comprehensive unit tests for backend runtime integration readiness and targets."""
from __future__ import annotations

import pytest

from app.services.backend_runtime_integration_readiness import (
    IntegrationArea,
    RuntimeIntegrationTarget,
    RuntimeIntegrationDryRunResult,
)


class TestBackendRuntimeIntegrationReadiness:
    def test_integration_area_enums(self):
        assert IntegrationArea.AUDIT == "audit"
        assert IntegrationArea.CONSENT == "consent"
        assert IntegrationArea.DEEP_READINESS == "deep_readiness"

    def test_runtime_integration_target_dataclass(self):
        target = RuntimeIntegrationTarget(
            id="target-1",
            area=IntegrationArea.AUDIT,
            candidate_id="cand-1",
            target_kind="service",
            dry_run_supported=True,
            runtime_wiring_allowed=False,
            requires_route_registration=False,
            requires_schema_change=False,
            destructive=False,
        )
        assert target.id == "target-1"
        assert target.area == IntegrationArea.AUDIT
        assert target.dry_run_supported is True

    def test_runtime_integration_dry_run_result_dataclass(self):
        res = RuntimeIntegrationDryRunResult(
            target_id="target-1",
            area=IntegrationArea.AUDIT,
            passed=True,
            message="Target ready",
            details={"status": "ok"},
        )
        assert res.target_id == "target-1"
        assert res.passed is True
        assert res.message == "Target ready"
