from app.modules.production_release import (
    build_blocked_production_release_preflight_report,
    build_default_production_release_preflight_report,
)


def test_production_release_preflight_defines_release_gates_without_authorisation():
    payload = build_default_production_release_preflight_report().to_payload()

    assert payload["prd_id"] == "PRD-11.0-11.4"
    assert payload["accepted"] is True
    assert payload["production_release_preflight_defined"] is True
    assert payload["release_candidate_artifact_gate_defined"] is True
    assert payload["deployment_environment_preflight_defined"] is True
    assert payload["database_migration_rollback_gate_defined"] is True
    assert payload["controlled_beta_to_production_go_no_go_defined"] is True
    assert payload["support_monitoring_incident_release_comms_defined"] is True
    assert payload["production_release_dry_run_gate_defined"] is True
    assert payload["controlled_beta_live_traffic_authorised"] is True
    assert payload["live_learner_traffic_authorised"] is True
    assert payload["production_release_authorised"] is False
    assert payload["deployment_authorised"] is False
    assert payload["release_tag_authorised"] is False
    assert payload["public_beta_authorised"] is False
    assert payload["billing_launch_authorised"] is False
    assert payload["live_payment_processing_authorised"] is False


def test_blocked_production_release_preflight_does_not_preserve_live_traffic():
    payload = build_blocked_production_release_preflight_report().to_payload()

    assert payload["accepted"] is False
    assert "production_release_preflight_incomplete" in payload["blockers"]
    assert payload["controlled_beta_live_traffic_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False
    assert payload["production_release_authorised"] is False


def test_production_release_preflight_custom_parameters():
    from app.modules.production_release.readiness import ProductionReleasePreflightReport

    report = ProductionReleasePreflightReport(
        accepted=True,
        prd_id="PRD-11-TEST",
        controls=("ctrl1",),
        blockers=("blocker1",),
        release_scope="custom_scope",
        controlled_beta_state="custom_beta",
        release_candidate_gate_state="rc_state",
        deployment_gate_state="deploy_state",
        migration_rollback_gate_state="mig_state",
        go_no_go_gate_state="gng_state",
        production_release_final_handoff_authorised=True,
    )
    p = report.to_payload()
    assert p["prd_id"] == "PRD-11-TEST"
    assert p["controls"] == ["ctrl1"]
    assert p["blockers"] == ["blocker1"]
    assert p["production_release_final_handoff_authorised"] is True
