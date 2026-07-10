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
