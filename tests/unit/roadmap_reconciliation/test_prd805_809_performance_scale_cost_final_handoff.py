from scripts.production_readiness.audit_prd805_809_performance_scale_cost_final_handoff import audit


def test_prd805_809_authority_and_evidence_state_are_valid():
    result = audit()

    assert result["authority_valid"] is True
    assert result["previous_prd8_foundation_valid"] is True
    assert result["performance_final_assurance_valid"] is True
    assert result["prd9_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["live_payment_processing_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    if result["valid"]:
        assert result["performance_final_assurance_evidence_recorded"] is True
        assert result["scale_cost_reconciliation_recorded"] is True
        assert result["performance_signoff_recorded"] is True
        assert result["prd8_sequence_complete"] is True
        assert result["prd9_handoff_authorised"] is True
        assert result["next_authorised_item"] == "PRD-9"
    else:
        assert result["performance_final_assurance_evidence_recorded"] is False
        assert result["scale_cost_reconciliation_recorded"] is False
        assert result["performance_signoff_recorded"] is False
        assert result["prd8_sequence_complete"] is False
        assert result["prd9_handoff_authorised"] is False
        assert result["next_authorised_item"] == "PRD-8.5-8.9"
        assert result["register_next_authorised_item"] == "PRD-8.5-8.9"
