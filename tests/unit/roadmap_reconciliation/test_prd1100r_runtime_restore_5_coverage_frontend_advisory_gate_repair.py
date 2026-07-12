from __future__ import annotations

from tests.support.governance_state import assert_archival_or_current_valid
from scripts.production_readiness.audit_prd1100r_runtime_restore_5_coverage_frontend_advisory_gate_repair import audit


def test_prd1100r_runtime_restore_5_authority_is_valid_before_capture() -> None:
    result = audit()
    assert_archival_or_current_valid(result)
    assert result["coverage_frontend_advisory_gate_contract_valid"] is True
    assert result["coverage_execution_gate_recorded"] is True
    assert result["frontend_quality_gate_recorded"] is True
    assert result["advisory_static_gate_recorded"] is True


def test_prd1100r_runtime_restore_5_does_not_claim_green_release_state() -> None:
    result = audit()
    assert result["runtime_baseline_green"] is False
    assert result["coverage_gate_green"] is False
    assert result["frontend_quality_green"] is False
    assert result["advisory_static_gate_green"] is False
    assert result["false_boundaries_locked"] is True
