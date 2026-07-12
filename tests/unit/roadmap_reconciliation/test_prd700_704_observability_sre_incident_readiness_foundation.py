from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from scripts.production_readiness.audit_prd700_704_observability_sre_incident_readiness_foundation import audit


def test_prd700_704_authority_and_archival_state_are_valid():
    result = audit()

    assert_archival_or_current_valid(result)
    assert result["previous_prd6_handoff_valid"] is True
    assert result["observability_sre_readiness_valid"] is True
    assert result["prd8_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    assert_historical_next_with_current_execution(result, "PRD-7.5-7.9")
    assert result["observability_sre_foundation_recorded"] is True
    assert result["observability_sre_evidence_recorded"] is True
