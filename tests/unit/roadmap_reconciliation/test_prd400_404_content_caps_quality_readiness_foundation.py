from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from scripts.production_readiness.audit_prd400_404_content_caps_quality_readiness_foundation import audit


def test_prd400_404_archival_authority_remains_valid_after_prd4_progression():
    result = audit()

    assert_archival_or_current_valid(result)
    assert_archival_or_current_valid(result)
    assert result["content_quality_readiness_helper_valid"] is True
    assert result["content_quality_route_added"] is True
    assert_historical_next_with_current_execution(result, "PRD-4.5-4.9")
    assert result["prd5_implementation_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False
