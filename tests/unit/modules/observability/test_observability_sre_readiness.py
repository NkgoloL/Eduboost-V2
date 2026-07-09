from app.modules.observability import (
    OBSERVABILITY_EVIDENCE_AREAS,
    build_blocked_observability_sre_readiness_report,
    build_default_observability_sre_readiness_report,
    default_observability_evidence_controls,
)


def test_default_observability_sre_readiness_payload_is_ready_and_guarded():
    payload = build_default_observability_sre_readiness_report().to_payload()

    assert payload["prd_id"] == "PRD-7.0-7.4"
    assert payload["ready"] is True
    assert payload["telemetry_readiness_defined"] is True
    assert payload["incident_readiness_defined"] is True
    assert payload["resilience_drills_defined"] is True
    assert payload["evidence_matrix_ready"] is True
    assert payload["prd8_implementation_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False
    assert "capture_prd7_observability_sre_foundation_evidence" in payload["recommended_next_actions"]


def test_blocked_observability_sre_readiness_payload_surfaces_blockers():
    payload = build_blocked_observability_sre_readiness_report().to_payload()

    assert payload["ready"] is False
    assert "dashboards_missing" in payload["blockers"]
    assert "observability_sre_evidence_matrix_incomplete" in payload["blockers"]


def test_observability_evidence_controls_cover_expected_areas():
    controls = default_observability_evidence_controls()

    assert {control.area for control in controls} == set(OBSERVABILITY_EVIDENCE_AREAS)
    assert all(control.ready for control in controls)
