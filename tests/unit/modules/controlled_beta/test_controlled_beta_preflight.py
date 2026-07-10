from __future__ import annotations

from app.modules.controlled_beta import (
    build_blocked_controlled_beta_preflight_report,
    build_default_controlled_beta_preflight_report,
)


def test_controlled_beta_preflight_default_defines_gates_without_authorising_live_traffic():
    payload = build_default_controlled_beta_preflight_report().to_payload()

    assert payload["prd_id"] == "PRD-10.0-10.4"
    assert payload["accepted"] is True
    assert payload["controlled_beta_preflight_defined"] is True
    assert payload["pyjwt_auth_regression_gate_defined"] is True
    assert payload["cohort_consent_eligibility_gate_defined"] is True
    assert payload["dry_run_kill_switch_rollback_defined"] is True
    assert payload["support_monitoring_incident_go_no_go_defined"] is True
    assert payload["live_learner_traffic_authorised"] is False
    assert payload["public_beta_authorised"] is False
    assert payload["production_release_authorised"] is False
    assert payload["deployment_authorised"] is False
    assert payload["billing_launch_authorised"] is False
    assert payload["live_payment_processing_authorised"] is False


def test_controlled_beta_preflight_blocked_state_exposes_blocker():
    payload = build_blocked_controlled_beta_preflight_report().to_payload()

    assert payload["accepted"] is False
    assert payload["beta_mode"] == "blocked"
    assert "controlled_beta_preflight_incomplete" in payload["blockers"]
