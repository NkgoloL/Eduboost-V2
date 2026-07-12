from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from scripts.production_readiness.audit_prd605_609_security_final_assurance_handoff import audit


def test_prd605_609_authority_and_archival_state_are_valid():
    result = audit()

    assert_archival_or_current_valid(result)
    assert result["previous_prd6_foundation_valid"] is True
    assert result["security_final_assurance_valid"] is True
    assert result["prd7_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    assert_historical_next_with_current_execution(result, "PRD-7")
    assert result["security_final_assurance_evidence_recorded"] is True
    assert result["prd6_sequence_complete"] is True
    assert result["prd7_handoff_authorised"] is True
