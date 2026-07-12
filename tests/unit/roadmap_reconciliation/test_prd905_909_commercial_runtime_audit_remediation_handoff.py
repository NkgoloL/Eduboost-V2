from __future__ import annotations

from tests.support.governance_state import assert_archival_or_current_valid, assert_current_execution_state
from scripts.production_readiness.audit_prd905_909_commercial_runtime_audit_remediation_handoff import audit


def test_prd905_909_authority_state_is_valid_after_evidence_capture():
    result = audit()

    assert_archival_or_current_valid(result)
    assert_archival_or_current_valid(result)
    assert result["prd_id"] == "PRD-9.5-9.9"
    assert result["runtime_code_contracts_valid"] is True
    assert result["dependency_remediation_valid"] is True
    assert result["repository_hygiene_valid"] is True
    assert result["audit_crosswalk_valid"] is True
    assert result["next_authorised_item"] == "PRD-10"
    assert_current_execution_state(result)
    assert result["billing_launch_authorised"] is False
    assert result["live_payment_processing_authorised"] is False
    assert result["prd10_implementation_authorised"] is False
