from scripts.production_readiness.audit_prd1100r_true_state_runtime_baseline_restoration import audit


def test_prd1100r_authority_state_is_valid_before_or_after_capture():
    result = audit()

    assert result["authority_valid"] is True
    assert result["previous_prd10_handoff_valid"] is True
    assert result["runtime_baseline_helper_valid"] is True
    assert result["true_state_runtime_baseline_restoration_authority_recorded"] is True
    assert result["true_state_report_reconciled"] is True
    assert result["concern_coverage_valid"] is True
    assert result["operational_hold_recorded"] is True
    assert result["controlled_beta_activation_operational_hold"] is True
    assert result["controlled_beta_live_traffic_authorised"] is True
    assert result["live_learner_traffic_authorised"] is True
    assert result["live_learner_traffic_operationally_safe"] is False
    assert result["production_release_evidence_blocked_until_runtime_baseline_green"] is True
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["billing_launch_authorised"] is False

    if result["valid"]:
        assert result["true_state_runtime_baseline_evidence_recorded"] is True
        assert result["next_authorised_item"] == "PRD-11.0R.RUNTIME-RESTORE"
    else:
        assert result["true_state_runtime_baseline_evidence_recorded"] is True
        assert result["next_authorised_item"] == "PRD-11.0R"
