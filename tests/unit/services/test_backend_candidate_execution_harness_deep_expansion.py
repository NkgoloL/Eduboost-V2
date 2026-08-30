"""Comprehensive unit tests for backend candidate execution harnesses."""
from __future__ import annotations

import pytest

from app.services.backend_candidate_execution_harness import (
    HarnessResult,
    run_audit_candidate_execution_harness,
    run_consent_candidate_execution_harness,
    run_deep_readiness_candidate_execution_harness,
    run_all_candidate_execution_harnesses,
)


class TestBackendCandidateExecutionHarness:
    def test_harness_result_dataclass(self):
        res = HarnessResult(
            name="test_harness",
            passed=True,
            details={"key": "val"},
        )
        assert res.name == "test_harness"
        assert res.passed is True
        assert res.details["key"] == "val"

    def test_run_consent_candidate_execution_harness(self):
        res = run_consent_candidate_execution_harness()
        assert res.passed is True
        assert res.name == "consent_candidate_execution_harness"
        assert res.details["write_operation_type"] == "write"
        assert res.details["read_operation_type"] == "read"

    def test_run_deep_readiness_candidate_execution_harness(self):
        res = run_deep_readiness_candidate_execution_harness()
        assert res.passed is True
        assert res.name == "deep_readiness_candidate_execution_harness"
        assert len(res.details["unsafe_public_checks"]) == 0

    @pytest.mark.asyncio
    async def test_run_audit_candidate_execution_harness(self):
        res = await run_audit_candidate_execution_harness()
        assert res.passed is True
        assert res.name == "audit_candidate_execution_harness"
        assert res.details["result_count"] > 0

    @pytest.mark.asyncio
    async def test_run_all_candidate_execution_harnesses(self):
        results = await run_all_candidate_execution_harnesses()
        assert len(results) == 3
        assert all(r.passed for r in results)
