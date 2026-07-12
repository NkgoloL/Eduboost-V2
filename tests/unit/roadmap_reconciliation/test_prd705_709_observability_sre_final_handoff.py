from scripts.production_readiness.audit_prd705_709_observability_sre_final_handoff import audit


def test_prd705_709_authority_and_archival_state_are_valid():
    result = audit()

    assert result["authority_valid"] is True
    assert result["previous_prd7_foundation_valid"] is True
    assert result["observability_final_assurance_valid"] is True
    assert result["prd8_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    if result["valid"]:
        assert result["next_authorised_item"] == "PRD-8"
        assert result["register_next_authorised_item"] == "PRD-8"
        assert result["observability_final_assurance_evidence_recorded"] is True
        assert result["prd7_sequence_complete"] is True
        assert result["prd8_handoff_authorised"] is True
    else:
        assert result["next_authorised_item"] == "PRD-7.5-7.9"
        assert result["register_next_authorised_item"] == "PRD-7.5-7.9"
        assert result["observability_final_assurance_evidence_recorded"] is True
        assert result["prd7_sequence_complete"] is True
        assert result["prd8_handoff_authorised"] is False
