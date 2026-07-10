from scripts.production_readiness.audit_prd1000_1004_controlled_beta_live_traffic_preflight_foundation import audit


def test_prd1000_1004_authority_state_is_valid_and_live_traffic_locked():
    result = audit()

    assert result["authority_valid"] is True
    assert result["previous_prd9_handoff_valid"] is True
    assert result["pyjwt_migration_valid"] is True
    assert result["controlled_beta_preflight_valid"] is True
    assert result["controlled_beta_preflight_foundation_recorded"] is True
    assert result["auth_token_regression_gate_recorded"] is True
    assert result["cohort_consent_eligibility_gate_recorded"] is True
    assert result["dry_run_kill_switch_rollback_gate_recorded"] is True
    assert result["support_monitoring_incident_go_no_go_gate_recorded"] is True
    assert result["live_learner_traffic_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["live_payment_processing_authorised"] is False

    if result["valid"]:
        assert result["controlled_beta_preflight_evidence_recorded"] is True
        assert result["next_authorised_item"] == "PRD-10.5-10.9"
    else:
        assert result["controlled_beta_preflight_evidence_recorded"] is False
        assert result["next_authorised_item"] == "PRD-10.0-10.4"
        assert result["register_next_authorised_item"] == "PRD-10.0-10.4"
