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


def test_commercial_launch_readiness_granular_blockers_and_actions():
    from app.modules.commercial_launch.readiness import (
        CommercialLaunchEvidenceControl,
        CommercialLaunchReadinessInputs,
        CommercialLaunchReadinessReport,
    )

    # Control ready property when false
    ctrl = CommercialLaunchEvidenceControl(area="test", owner_assigned=True, evidence_path_defined=False)
    assert ctrl.ready is False
    assert ctrl.to_payload()["ready"] is False

    # Blocked readiness report with each missing flag
    inputs = CommercialLaunchReadinessInputs(
        billing_provider_test_mode_defined=False,
        pricing_packaging_defined=False,
        checkout_webhook_contract_defined=False,
        subscription_entitlement_matrix_defined=False,
        invoice_tax_refund_support_defined=False,
        sponsorship_school_procurement_defined=False,
        commercial_support_reconciliation_defined=False,
        terms_privacy_launch_comms_defined=False,
        existing_billing_contracts_valid=False,
        evidence_controls=(),
    )
    report = CommercialLaunchReadinessReport(inputs=inputs)
    assert report.ready is False
    assert report.billing_contract_readiness_defined is False
    assert report.commercial_policy_readiness_defined is False
    assert report.support_reconciliation_defined is False
    assert report.evidence_matrix_ready is False

    blockers = report.blockers
    assert "billing_provider_test_mode_missing" in blockers
    assert "pricing_packaging_missing" in blockers
    assert "checkout_webhook_contract_missing" in blockers
    assert "subscription_entitlement_matrix_missing" in blockers
    assert "invoice_tax_refund_support_missing" in blockers
    assert "sponsorship_school_procurement_missing" in blockers
    assert "commercial_support_reconciliation_missing" in blockers
    assert "terms_privacy_launch_comms_missing" in blockers
    assert "existing_billing_contracts_not_valid" in blockers
    assert "commercial_evidence_matrix_incomplete" in blockers

    actions = report.recommended_next_actions
    assert any(a.startswith("resolve_") for a in actions)

    # Ready report actions
    ready_report = build_default_commercial_launch_readiness_report()
    assert "capture_prd9_commercial_launch_readiness_foundation_evidence" in ready_report.recommended_next_actions
