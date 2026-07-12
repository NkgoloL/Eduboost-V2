from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from scripts.production_readiness.audit_prd1100_1104_production_release_deployment_preflight_foundation import audit


def test_prd1100_1104_authority_state_is_valid_before_or_after_capture():
    result = audit()

    assert_archival_or_current_valid(result)
    assert result["production_release_preflight_valid"] is True
    assert result["prd11_production_release_preflight_foundation_recorded"] is True
    assert result["release_gate_definition_recorded"] is True
    assert result["release_candidate_artifact_gate_recorded"] is True
    assert result["deployment_environment_preflight_recorded"] is True
    assert result["database_migration_rollback_gate_recorded"] is True
    assert result["controlled_beta_to_production_go_no_go_gate_recorded"] is True
    assert result["support_monitoring_incident_release_comms_gate_recorded"] is True
    assert result["production_release_dry_run_gate_recorded"] is True
    assert result["controlled_beta_live_traffic_authorised"] is True
    assert result["live_learner_traffic_authorised"] is True
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["release_tag_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["live_payment_processing_authorised"] is False

    assert result["production_release_preflight_evidence_recorded"] is False
    assert_historical_next_with_current_execution(result, "PRD-11.0-11.4")
