from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from scripts.production_readiness.audit_prd405_409_content_quality_final_handoff import audit


def test_prd405_409_authority_is_valid_before_capture():
    result = audit()

    assert_archival_or_current_valid(result)
    assert_archival_or_current_valid(result)
    assert result["previous_prd4_foundation_valid"] is True
    assert result["content_quality_final_acceptance_valid"] is True
    assert_historical_next_with_current_execution(result, "PRD-5")
    assert result["prd5_implementation_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False
