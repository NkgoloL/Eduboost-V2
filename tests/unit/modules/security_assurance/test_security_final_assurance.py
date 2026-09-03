from app.modules.security_assurance.assurance import (
    build_blocked_security_final_assurance_report,
    build_default_security_final_assurance_report,
    default_security_final_evidence_items,
)


def test_default_security_final_assurance_is_accepted_and_guarded():
    payload = build_default_security_final_assurance_report().to_payload()

    assert payload["prd_id"] == "PRD-6.5-6.9"
    assert payload["accepted"] is True
    assert payload["dast_api_fuzzing_evidence_accepted"] is True
    assert payload["dependency_container_sbom_evidence_accepted"] is True
    assert payload["secret_rotation_rate_limit_abuse_evidence_accepted"] is True
    assert payload["critical_endpoint_authz_negative_tests_accepted"] is True
    assert payload["external_or_independent_review_recorded"] is True
    assert payload["security_signoff_recorded"] is True
    assert payload["prd6_final_reconciliation_recorded"] is True
    assert payload["prd7_implementation_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False
    assert payload["production_release_authorised"] is False


def test_blocked_security_final_assurance_reports_blockers():
    payload = build_blocked_security_final_assurance_report().to_payload()

    assert payload["accepted"] is False
    assert "final_security_evidence_matrix_incomplete" in payload["blockers"]
    assert "external_or_independent_review_not_recorded" in payload["blockers"]
    assert "security_signoff_not_recorded" in payload["blockers"]


def test_final_evidence_items_are_complete_when_accepted():
    items = default_security_final_evidence_items(accepted=True)

    assert len(items) >= 10
    assert all(item.accepted for item in items)


def test_security_final_assurance_granular_blockers_and_actions():
    from app.modules.security_assurance.assurance import (
        SecurityFinalAssuranceInputs,
        SecurityFinalAssuranceReport,
        SecurityFinalEvidenceItem,
    )
    from app.modules.security_assurance.readiness import build_default_security_assurance_readiness_report

    # Single item accepted property
    item = SecurityFinalEvidenceItem(area="invalid", evidence_recorded=True, findings_triaged=True, high_severity_blockers_open=False)
    assert item.accepted is False
    assert item.to_payload()["accepted"] is False

    # Blocked assurance report with empty evidence items
    inputs = SecurityFinalAssuranceInputs(
        readiness_report=build_default_security_assurance_readiness_report(),
        final_evidence_items=(),
        external_or_independent_review_recorded=False,
        security_signoff_recorded=False,
        prd6_final_reconciliation_recorded=False,
    )
    report = SecurityFinalAssuranceReport(inputs=inputs)
    assert report.accepted is False
    assert report.final_evidence_matrix_accepted is False
    assert report.dast_api_fuzzing_evidence_accepted is False
    assert report.dependency_container_sbom_evidence_accepted is False
    assert report.operational_security_evidence_accepted is False
    assert report.external_review_evidence_accepted is False

    blockers = report.blockers
    assert "final_security_evidence_matrix_incomplete" in blockers
    assert "dast_api_fuzzing_evidence_incomplete" in blockers
    assert "dependency_container_sbom_evidence_incomplete" in blockers
    assert "operational_security_evidence_incomplete" in blockers
    assert "external_review_evidence_incomplete" in blockers
    assert "external_or_independent_review_not_recorded" in blockers
    assert "security_signoff_not_recorded" in blockers
    assert "prd6_final_reconciliation_not_recorded" in blockers

    actions = report.recommended_next_actions
    assert any(a.startswith("resolve_") for a in actions)

    # Accepted actions
    accepted_report = build_default_security_final_assurance_report()
    assert "capture_prd6_final_security_assurance_evidence" in accepted_report.recommended_next_actions
