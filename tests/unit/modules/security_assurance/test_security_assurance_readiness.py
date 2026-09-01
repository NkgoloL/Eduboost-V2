from app.modules.security_assurance import (
    SECURITY_EVIDENCE_AREAS,
    build_blocked_security_assurance_readiness_report,
    build_default_security_assurance_readiness_report,
    default_security_evidence_controls,
)


def test_default_security_assurance_readiness_payload_is_ready_and_guarded():
    payload = build_default_security_assurance_readiness_report().to_payload()

    assert payload["prd_id"] == "PRD-6.0-6.4"
    assert payload["ready"] is True
    assert payload["scanner_readiness_defined"] is True
    assert payload["operational_security_drills_defined"] is True
    assert payload["evidence_matrix_ready"] is True
    assert payload["external_review_path_defined"] is True
    assert payload["prd7_implementation_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False
    assert "capture_prd6_security_assurance_foundation_evidence" in payload["recommended_next_actions"]


def test_blocked_security_assurance_readiness_payload_surfaces_blockers():
    payload = build_blocked_security_assurance_readiness_report().to_payload()

    assert payload["ready"] is False
    assert "dast_api_fuzzing_plan_missing" in payload["blockers"]
    assert "security_evidence_matrix_incomplete" in payload["blockers"]


def test_security_evidence_controls_cover_expected_areas():
    controls = default_security_evidence_controls()

    assert {control.area for control in controls} == set(SECURITY_EVIDENCE_AREAS)
    assert all(control.ready for control in controls)


def test_security_assurance_readiness_granular_blockers_and_actions():
    from app.modules.security_assurance.readiness import (
        SecurityAssuranceReadinessInputs,
        SecurityAssuranceReadinessReport,
        SecurityEvidenceControl,
    )

    # Control ready property when false
    ctrl = SecurityEvidenceControl(area="test", owner_assigned=True, tool_or_method_defined=False)
    assert ctrl.ready is False
    assert ctrl.to_payload()["ready"] is False

    # Blocked readiness report with each missing flag
    inputs = SecurityAssuranceReadinessInputs(
        dast_api_fuzzing_plan_defined=False,
        dependency_scanning_plan_defined=False,
        container_image_scanning_plan_defined=False,
        sbom_generation_plan_defined=False,
        secret_rotation_drill_defined=False,
        rate_limit_abuse_testing_defined=False,
        external_review_path_defined=False,
        critical_endpoint_authz_tests_defined=False,
        evidence_controls=(),
    )
    report = SecurityAssuranceReadinessReport(inputs=inputs)
    assert report.ready is False
    assert report.scanner_readiness_defined is False
    assert report.operational_security_drills_defined is False
    assert report.evidence_matrix_ready is False

    blockers = report.blockers
    assert "dast_api_fuzzing_plan_missing" in blockers
    assert "dependency_scanning_plan_missing" in blockers
    assert "container_image_scanning_plan_missing" in blockers
    assert "sbom_generation_plan_missing" in blockers
    assert "secret_rotation_drill_missing" in blockers
    assert "rate_limit_abuse_testing_plan_missing" in blockers
    assert "critical_endpoint_authz_tests_missing" in blockers
    assert "external_review_path_missing" in blockers
    assert "security_evidence_matrix_incomplete" in blockers

    actions = report.recommended_next_actions
    assert any(a.startswith("resolve_") for a in actions)
