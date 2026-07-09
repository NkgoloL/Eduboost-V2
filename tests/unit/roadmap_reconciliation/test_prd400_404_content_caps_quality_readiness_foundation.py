from scripts.production_readiness.audit_prd400_404_content_caps_quality_readiness_foundation import audit


def test_prd400_404_archival_authority_remains_valid_after_prd4_progression():
    result = audit()

    assert result["authority_valid"] is True
    assert result["valid"] is True
    assert result["content_quality_readiness_helper_valid"] is True
    assert result["content_quality_route_added"] is True
    assert result["next_authorised_item"] == "PRD-4.5-4.9"
    assert result["register_next_authorised_item"] in {"PRD-4.5-4.9", "PRD-5"}
    assert result["prd5_implementation_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False
