from scripts.production_readiness.audit_prd600_604_security_assurance_foundation import audit


def test_prd600_604_authority_and_archival_state_are_valid():
    result = audit()

    assert result["authority_valid"] is True
    assert result["previous_prd5_handoff_valid"] is True
    assert result["security_readiness_valid"] is True
    assert result["prd7_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    if result["valid"]:
        assert result["next_authorised_item"] == "PRD-6.5-6.9"
        assert result["register_next_authorised_item"] == "PRD-6.5-6.9"
        assert result["security_assurance_foundation_recorded"] is True
        assert result["security_assurance_evidence_recorded"] is True
    else:
        assert result["next_authorised_item"] == "PRD-6.0-6.4"
        assert result["register_next_authorised_item"] == "PRD-6.0-6.4"
        assert result["security_assurance_foundation_recorded"] is False
        assert result["security_assurance_evidence_recorded"] is False
