from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from scripts.production_readiness.audit_prd600_604_security_assurance_foundation import audit


def test_prd600_604_authority_and_archival_state_are_valid():
    result = audit()

    assert_archival_or_current_valid(result)
    assert result["previous_prd5_handoff_valid"] is True
    assert result["security_readiness_valid"] is True
    assert result["prd7_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    assert_historical_next_with_current_execution(result, "PRD-6.5-6.9")
    assert result["security_assurance_foundation_recorded"] is True
    assert result["security_assurance_evidence_recorded"] is True
