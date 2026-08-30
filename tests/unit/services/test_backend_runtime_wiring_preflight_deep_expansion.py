"""Comprehensive unit tests for backend runtime wiring preflight checks."""
from __future__ import annotations

import pytest

from app.services.backend_runtime_wiring_preflight import (
    PreflightArea,
    RuntimeWiringPreflightResult,
    check_audit_wiring_preflight,
    check_consent_wiring_preflight,
    check_deep_readiness_wiring_preflight,
)


class TestBackendRuntimeWiringPreflight:
    def test_preflight_area_enums(self):
        assert PreflightArea.AUDIT == "audit"
        assert PreflightArea.CONSENT == "consent"
        assert PreflightArea.DEEP_READINESS == "deep_readiness"
        assert PreflightArea.SCHEMA_DRIFT == "schema_drift"

    def test_runtime_wiring_preflight_result_dataclass(self):
        res = RuntimeWiringPreflightResult(
            area=PreflightArea.AUDIT,
            passed=True,
            message="all checks passed",
            details={"key": "val"},
        )
        assert res.area == PreflightArea.AUDIT
        assert res.passed is True
        assert res.message == "all checks passed"

    def test_check_audit_wiring_preflight(self):
        res = check_audit_wiring_preflight()
        assert res.passed is True
        assert res.area == PreflightArea.AUDIT

    def test_check_consent_wiring_preflight(self):
        res = check_consent_wiring_preflight()
        assert res.passed is True
        assert res.area == PreflightArea.CONSENT

    def test_check_deep_readiness_wiring_preflight(self):
        res = check_deep_readiness_wiring_preflight()
        assert res.passed is True
        assert res.area == PreflightArea.DEEP_READINESS
