from pathlib import Path

from scripts.production_readiness.audit_prd300_304_learner_parent_vertical_journey_foundation import ROOT, audit


def test_prd300_304_authority_and_recorded_states_are_valid_when_expected():
    result = audit(Path(ROOT))

    assert result["authority_valid"] is True
    assert result["vertical_journey_service_added"] is True
    assert result["vertical_journey_route_registered"] is True
    assert result["live_learner_traffic_authorised"] is False
    assert result["prd4_implementation_authorised"] is False

    if result["valid"] is True:
        assert result["learner_parent_vertical_journey_foundation_recorded"] is True
        assert result["register_next_authorised_item"] == "PRD-3.5-3.9"
    else:
        assert result["learner_parent_vertical_journey_foundation_recorded"] is True
        assert result["register_next_authorised_item"] in {"PRD-3", "PRD-3.0-3.4"}
