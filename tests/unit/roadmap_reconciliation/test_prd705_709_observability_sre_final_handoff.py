from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from scripts.production_readiness.audit_prd705_709_observability_sre_final_handoff import audit


def test_prd705_709_authority_and_archival_state_are_valid():
    result = audit()

    assert_archival_or_current_valid(result)
    assert result["previous_prd7_foundation_valid"] is True
    assert result["observability_final_assurance_valid"] is True
    assert result["prd8_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    assert_historical_next_with_current_execution(result, "PRD-8")
    assert result["observability_final_assurance_evidence_recorded"] is True
    assert result["prd7_sequence_complete"] is True
    assert result["prd8_handoff_authorised"] is True
