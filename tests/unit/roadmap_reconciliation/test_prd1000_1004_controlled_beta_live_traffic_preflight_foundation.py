from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from scripts.production_readiness.audit_prd1000_1004_controlled_beta_live_traffic_preflight_foundation import audit


def test_prd1000_1004_authority_state_is_valid_and_live_traffic_locked():
    result = audit()

    assert_archival_or_current_valid(result)
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

    assert result["controlled_beta_preflight_evidence_recorded"] is True
    assert_historical_next_with_current_execution(result, "PRD-10.0-10.4")
