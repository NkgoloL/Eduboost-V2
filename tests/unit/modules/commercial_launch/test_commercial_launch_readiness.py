from app.modules.commercial_launch import (
    COMMERCIAL_EVIDENCE_AREAS,
    build_blocked_commercial_launch_readiness_report,
    build_default_commercial_launch_readiness_report,
    default_commercial_launch_evidence_controls,
)


def test_default_commercial_launch_readiness_is_ready_and_boundary_safe():
    payload = build_default_commercial_launch_readiness_report().to_payload()

    assert payload["prd_id"] == "PRD-9.0-9.4"
    assert payload["ready"] is True
    assert payload["billing_contract_readiness_defined"] is True
    assert payload["commercial_policy_readiness_defined"] is True
    assert payload["support_reconciliation_defined"] is True
    assert payload["evidence_matrix_ready"] is True
    assert payload["existing_billing_contracts_valid"] is True
    assert payload["billing_contracts"]["provider_decision_issues"] == []
    assert payload["billing_contracts"]["pricing_policy_issues"] == []
    assert payload["billing_contracts"]["retry_policy_issues"] == []
    assert payload["billing_launch_authorised"] is False
    assert payload["live_payment_processing_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False
    assert payload["prd10_implementation_authorised"] is False
    assert payload["production_release_authorised"] is False


def test_blocked_commercial_launch_readiness_reports_missing_controls():
    payload = build_blocked_commercial_launch_readiness_report().to_payload()

    assert payload["ready"] is False
    assert "billing_provider_test_mode_missing" in payload["blockers"]
    assert "commercial_evidence_matrix_incomplete" in payload["blockers"]
    assert payload["billing_launch_authorised"] is False
    assert payload["live_payment_processing_authorised"] is False


def test_commercial_launch_evidence_controls_cover_all_areas():
    controls = default_commercial_launch_evidence_controls()

    assert {control.area for control in controls} == set(COMMERCIAL_EVIDENCE_AREAS)
    assert all(control.ready for control in controls)
    assert all(control.blocks_billing_launch for control in controls)
    assert all(control.blocks_live_payment_processing for control in controls)
