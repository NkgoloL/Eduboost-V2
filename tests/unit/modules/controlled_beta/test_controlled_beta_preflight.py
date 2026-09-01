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


def test_controlled_beta_preflight_custom_parameters():
    from app.modules.controlled_beta.preflight import ControlledBetaPreflightReport

    report = ControlledBetaPreflightReport(
        prd_id="PRD-10-TEST",
        accepted=True,
        controls=("ctrl1", "ctrl2"),
        blockers=("test_blocker",),
        beta_mode="custom_mode",
        live_traffic_gate_state="active",
        auth_token_regression_gate="gate_active",
        cohort_gate="cohort_active",
        kill_switch_state="ready",
        support_go_no_go_state="ready",
        prd10_final_handoff_authorised=True,
    )
    p = report.to_payload()
    assert p["prd_id"] == "PRD-10-TEST"
    assert p["controls"] == ["ctrl1", "ctrl2"]
    assert p["blockers"] == ["test_blocker"]
    assert p["prd10_final_handoff_authorised"] is True
