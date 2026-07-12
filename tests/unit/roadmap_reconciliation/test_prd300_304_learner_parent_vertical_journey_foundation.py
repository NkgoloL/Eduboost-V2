from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from pathlib import Path

from scripts.production_readiness.audit_prd300_304_learner_parent_vertical_journey_foundation import ROOT, audit


def test_prd300_304_authority_and_recorded_states_are_valid_when_expected():
    result = audit(Path(ROOT))

    assert_archival_or_current_valid(result)
    assert result["vertical_journey_service_added"] is True
    assert result["vertical_journey_route_registered"] is True
    assert result["live_learner_traffic_authorised"] is False
    assert result["prd4_implementation_authorised"] is False

    assert result["learner_parent_vertical_journey_foundation_recorded"] is True
    assert_historical_next_with_current_execution(result, "PRD-3.5-3.9")
