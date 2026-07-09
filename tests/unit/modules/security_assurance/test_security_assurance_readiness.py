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
