from scripts.production_readiness.audit_prd400_404_content_caps_quality_readiness_foundation import audit


def test_prd400_404_authority_is_valid_before_capture():
    result = audit()

    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["content_quality_readiness_helper_valid"] is True
    assert result["content_quality_route_added"] is True
    assert result["next_authorised_item"] == "PRD-4.0-4.4"
    assert result["register_next_authorised_item"] == "PRD-4.0-4.4"
    assert result["prd5_implementation_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False
