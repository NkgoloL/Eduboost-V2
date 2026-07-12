from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from scripts.production_readiness.audit_prd805_809_performance_scale_cost_final_handoff import audit


def test_prd805_809_authority_and_evidence_state_are_valid():
    result = audit()

    assert_archival_or_current_valid(result)
    assert result["previous_prd8_foundation_valid"] is True
    assert result["performance_final_assurance_valid"] is True
    assert result["prd9_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["live_payment_processing_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    assert result["performance_final_assurance_evidence_recorded"] is True
    assert result["scale_cost_reconciliation_recorded"] is True
    assert result["performance_signoff_recorded"] is True
    assert result["prd8_sequence_complete"] is True
    assert result["prd9_handoff_authorised"] is True
    assert_historical_next_with_current_execution(result, "PRD-9")
