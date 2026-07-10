from scripts.production_readiness.audit_prd1005_1009_controlled_beta_final_live_traffic_handoff import audit


def test_prd1005_1009_authority_state_is_valid_before_or_after_capture():
    result = audit()

    assert result["authority_valid"] is True
    assert result["previous_prd10_preflight_valid"] is True
    assert result["controlled_beta_final_authorisation_valid"] is True
    assert result["controlled_beta_final_authority_recorded"] is True
    assert result["cohort_guardian_consent_learner_eligibility_evidence_accepted"] is True
    assert result["auth_token_regression_evidence_accepted"] is True
    assert result["dry_run_kill_switch_rollback_evidence_accepted"] is True
    assert result["support_monitoring_incident_go_no_go_evidence_accepted"] is True
    assert result["public_beta_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["live_payment_processing_authorised"] is False
    assert result["prd11_implementation_authorised"] is False

    if result["valid"]:
        assert result["controlled_beta_final_evidence_recorded"] is True
        assert result["controlled_beta_live_traffic_authorised"] is True
        assert result["live_learner_traffic_authorised"] is True
        assert result["prd10_sequence_complete"] is True
        assert result["prd11_handoff_authorised"] is True
        assert result["next_authorised_item"] == "PRD-11"
    else:
        assert result["controlled_beta_final_evidence_recorded"] is False
        assert result["controlled_beta_live_traffic_authorised"] is False
        assert result["live_learner_traffic_authorised"] is False
        assert result["next_authorised_item"] == "PRD-10.5-10.9"
