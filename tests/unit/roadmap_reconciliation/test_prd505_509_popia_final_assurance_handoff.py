from scripts.production_readiness.audit_prd505_509_popia_final_assurance_handoff import audit


def test_prd505_509_authority_and_archival_state_are_valid():
    result = audit()

    assert result["authority_valid"] is True
    assert result["previous_prd5_foundation_valid"] is True
    assert result["privacy_final_assurance_valid"] is True
    assert result["prd6_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    if result["valid"]:
        assert result["next_authorised_item"] == "PRD-6"
        assert result["register_next_authorised_item"] in {"PRD-6", "PRD-6.5-6.9", "PRD-7"}
        assert result["privacy_final_assurance_evidence_recorded"] is True
        assert result["audit_2026_07_09_crosswalk_reconciled"] is True
        assert result["prd5_sequence_complete"] is True
        assert result["prd6_handoff_authorised"] is True
    else:
        assert result["next_authorised_item"] == "PRD-5.5-5.9"
        assert result["register_next_authorised_item"] == "PRD-5.5-5.9"
        assert result["privacy_final_assurance_evidence_recorded"] is False
        assert result["audit_2026_07_09_crosswalk_reconciled"] is False
        assert result["prd5_sequence_complete"] is False
        assert result["prd6_handoff_authorised"] is False
