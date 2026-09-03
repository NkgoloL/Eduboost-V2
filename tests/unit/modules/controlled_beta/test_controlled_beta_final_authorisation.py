from app.modules.controlled_beta import (
    build_blocked_controlled_beta_final_authorisation_report,
    build_default_controlled_beta_final_authorisation_report,
)


def test_controlled_beta_final_authorisation_allows_limited_live_traffic_only():
    payload = build_default_controlled_beta_final_authorisation_report().to_payload()

    assert payload["prd_id"] == "PRD-10.5-10.9"
    assert payload["accepted"] is True
    assert payload["controlled_beta_final_evidence_accepted"] is True
    assert payload["controlled_beta_live_traffic_authorised"] is True
    assert payload["live_learner_traffic_authorised"] is True
    assert payload["prd11_handoff_authorised"] is True
    assert payload["public_beta_authorised"] is False
    assert payload["public_beta_live_traffic_authorised"] is False
    assert payload["production_release_authorised"] is False
    assert payload["deployment_authorised"] is False
    assert payload["billing_launch_authorised"] is False
    assert payload["live_payment_processing_authorised"] is False


def test_controlled_beta_final_authorisation_blocked_report_does_not_authorise_live_traffic():
    payload = build_blocked_controlled_beta_final_authorisation_report().to_payload()

    assert payload["accepted"] is False
    assert "controlled_beta_final_authorisation_incomplete" in payload["blockers"]
    assert payload["controlled_beta_live_traffic_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False
    assert payload["prd11_handoff_authorised"] is False


def test_controlled_beta_final_authorisation_custom_parameters():
    from app.modules.controlled_beta.authorisation import ControlledBetaFinalAuthorisationReport

    report = ControlledBetaFinalAuthorisationReport(
        prd_id="PRD-10.5-CUSTOM",
        accepted=True,
        controls=("c1", "c2"),
        blockers=(),
        beta_scope="custom_scope",
        authorisation_decision="custom_decision",
        cohort_gate_state="cohort_state",
        auth_gate_state="auth_state",
        dry_run_gate_state="dry_run_state",
        support_gate_state="support_state",
        live_learner_traffic_authorised=True,
        controlled_beta_live_traffic_authorised=True,
        prd11_handoff_authorised=True,
    )
    p = report.to_payload()
    assert p["prd_id"] == "PRD-10.5-CUSTOM"
    assert p["controls"] == ["c1", "c2"]
    assert p["authorisation_decision"] == "custom_decision"
    assert p["controlled_beta_live_traffic_authorised"] is True
