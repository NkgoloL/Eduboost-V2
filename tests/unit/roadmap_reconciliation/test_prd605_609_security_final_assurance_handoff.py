from scripts.production_readiness.audit_prd605_609_security_final_assurance_handoff import audit


def test_prd605_609_authority_and_archival_state_are_valid():
    result = audit()

    assert result["authority_valid"] is True
    assert result["previous_prd6_foundation_valid"] is True
    assert result["security_final_assurance_valid"] is True
    assert result["prd7_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    if result["valid"]:
        assert result["next_authorised_item"] == "PRD-7"
        assert result["register_next_authorised_item"] == "PRD-7"
        assert result["security_final_assurance_evidence_recorded"] is True
        assert result["prd6_sequence_complete"] is True
        assert result["prd7_handoff_authorised"] is True
    else:
        assert result["next_authorised_item"] == "PRD-6.5-6.9"
        assert result["register_next_authorised_item"] == "PRD-6.5-6.9"
        assert result["security_final_assurance_evidence_recorded"] is False
        assert result["prd6_sequence_complete"] is False
        assert result["prd7_handoff_authorised"] is False
