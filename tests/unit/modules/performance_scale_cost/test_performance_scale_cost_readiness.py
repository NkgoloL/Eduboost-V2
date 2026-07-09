from app.modules.performance_scale_cost import (
    PERFORMANCE_COST_EVIDENCE_AREAS,
    build_blocked_performance_scale_cost_readiness_report,
    build_default_performance_scale_cost_readiness_report,
    default_performance_scale_cost_evidence_controls,
)


def test_default_performance_scale_cost_readiness_is_complete_and_boundary_safe():
    payload = build_default_performance_scale_cost_readiness_report().to_payload()

    assert payload["prd_id"] == "PRD-8.0-8.4"
    assert payload["ready"] is True
    assert payload["performance_execution_defined"] is True
    assert payload["scale_execution_defined"] is True
    assert payload["cost_execution_defined"] is True
    assert payload["evidence_matrix_ready"] is True
    assert payload["runtime_kg_query_performance_defined"] is True
    assert payload["llm_cost_simulation_defined"] is True
    assert payload["prd9_implementation_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False


def test_blocked_performance_scale_cost_readiness_reports_missing_controls():
    payload = build_blocked_performance_scale_cost_readiness_report().to_payload()

    assert payload["ready"] is False
    assert "load_tests_missing" in payload["blockers"]
    assert "performance_scale_cost_evidence_matrix_incomplete" in payload["blockers"]


def test_performance_scale_cost_evidence_controls_cover_all_areas():
    controls = default_performance_scale_cost_evidence_controls()

    assert {control.area for control in controls} == set(PERFORMANCE_COST_EVIDENCE_AREAS)
    assert all(control.ready for control in controls)
