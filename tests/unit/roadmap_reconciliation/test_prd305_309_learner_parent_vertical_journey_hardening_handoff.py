from pathlib import Path

from scripts.production_readiness.audit_prd305_309_learner_parent_vertical_journey_hardening_handoff import ROOT, audit


def test_prd305_309_authority_and_recorded_states_are_valid_when_expected():
    result = audit(Path(ROOT))

    assert result["authority_valid"] is True
    assert result["previous_prd3_foundation_valid"] is True
    assert result["vertical_journey_hardening_helper_valid"] is True
    assert result["live_learner_traffic_authorised"] is False
    assert result["prd4_implementation_authorised"] is False

    if result["valid"] is True:
        assert result["vertical_journey_final_hardening_recorded"] is True
        assert result["vertical_journey_final_evidence_recorded"] is True
        assert result["prd3_sequence_complete"] is True
        assert result["register_next_authorised_item"] == "PRD-4"
    else:
        assert result["vertical_journey_final_hardening_recorded"] is False
        assert result["register_next_authorised_item"] == "PRD-3.5-3.9"
