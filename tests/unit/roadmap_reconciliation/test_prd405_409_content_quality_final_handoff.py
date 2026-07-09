from scripts.production_readiness.audit_prd405_409_content_quality_final_handoff import audit


def test_prd405_409_authority_is_valid_before_capture():
    result = audit()

    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["previous_prd4_foundation_valid"] is True
    assert result["content_quality_final_acceptance_valid"] is True
    assert result["next_authorised_item"] == "PRD-4.5-4.9"
    assert result["register_next_authorised_item"] == "PRD-4.5-4.9"
    assert result["prd5_implementation_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False
