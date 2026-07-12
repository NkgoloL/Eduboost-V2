from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from scripts.production_readiness.audit_prd505_509_popia_final_assurance_handoff import audit


def test_prd505_509_authority_and_archival_state_are_valid():
    result = audit()

    assert_archival_or_current_valid(result)
    assert result["previous_prd5_foundation_valid"] is True
    assert result["privacy_final_assurance_valid"] is True
    assert result["prd6_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    assert_historical_next_with_current_execution(result, "PRD-6")
    assert result["privacy_final_assurance_evidence_recorded"] is True
    assert result["audit_2026_07_09_crosswalk_reconciled"] is True
    assert result["prd5_sequence_complete"] is True
    assert result["prd6_handoff_authorised"] is True
