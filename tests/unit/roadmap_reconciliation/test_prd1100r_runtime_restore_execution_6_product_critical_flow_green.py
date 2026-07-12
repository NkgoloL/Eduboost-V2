from __future__ import annotations

from tests.support.governance_state import assert_archival_or_current_valid, assert_current_execution_state
from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_6_product_critical_flow_green import audit


def test_prd1100r_execution_6_authority_valid_before_capture() -> None:
    result = audit(require_green=False)
    assert_archival_or_current_valid(result)
    assert result["product_flow_green_contract_valid"] is True
    assert result["product_critical_flow_green_authority_recorded"] is True
    assert result["product_critical_flow_green_evidence_recorded"] is True
    assert_current_execution_state(result)


def test_prd1100r_execution_6_preserves_release_boundaries() -> None:
    result = audit(require_green=False)
    assert result["false_boundaries_locked"] is True
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["live_payment_processing_authorised"] is False
