from scripts.production_readiness.audit_prd700_704_observability_sre_incident_readiness_foundation import audit


def test_prd700_704_authority_and_archival_state_are_valid():
    result = audit()

    assert result["authority_valid"] is True
    assert result["previous_prd6_handoff_valid"] is True
    assert result["observability_sre_readiness_valid"] is True
    assert result["prd8_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    if result["valid"]:
        assert result["next_authorised_item"] == "PRD-7.5-7.9"
        assert result["register_next_authorised_item"] in {"PRD-7.5-7.9", "PRD-8"}
        assert result["observability_sre_foundation_recorded"] is True
        assert result["observability_sre_evidence_recorded"] is True
    else:
        assert result["next_authorised_item"] == "PRD-7.0-7.4"
        assert result["register_next_authorised_item"] == "PRD-7.0-7.4"
        assert result["observability_sre_foundation_recorded"] is False
        assert result["observability_sre_evidence_recorded"] is False
