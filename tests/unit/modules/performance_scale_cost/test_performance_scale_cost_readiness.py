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


def test_performance_scale_cost_readiness_granular_blockers_and_actions():
    from app.modules.performance_scale_cost.readiness import (
        PerformanceScaleCostEvidenceControl,
        PerformanceScaleCostReadinessInputs,
        PerformanceScaleCostReadinessReport,
    )

    # Test single control payload and ready property
    ctrl = PerformanceScaleCostEvidenceControl(area="test_area", owner_assigned=True, evidence_path_defined=False)
    assert ctrl.ready is False
    assert ctrl.to_payload()["ready"] is False

    # Test individual missing input flags triggering distinct blockers
    inputs = PerformanceScaleCostReadinessInputs(
        load_tests_defined=False,
        runtime_kg_query_performance_defined=False,
        database_index_review_defined=False,
        llm_cost_simulation_defined=False,
        queue_backpressure_tests_defined=False,
        frontend_performance_budget_defined=False,
        capacity_plan_defined=False,
        cost_guardrails_defined=False,
        evidence_controls=(),
    )
    report = PerformanceScaleCostReadinessReport(inputs)
    assert report.ready is False
    assert report.performance_execution_defined is False
    assert report.scale_execution_defined is False
    assert report.cost_execution_defined is False
    assert report.evidence_matrix_ready is False

    blockers = report.blockers
    assert "load_tests_missing" in blockers
    assert "runtime_kg_query_performance_missing" in blockers
    assert "database_index_review_missing" in blockers
    assert "llm_cost_simulation_missing" in blockers
    assert "queue_backpressure_tests_missing" in blockers
    assert "frontend_performance_budget_missing" in blockers
    assert "capacity_plan_missing" in blockers
    assert "cost_guardrails_missing" in blockers
    assert "performance_scale_cost_evidence_matrix_incomplete" in blockers

    actions = report.recommended_next_actions
    assert any(a.startswith("resolve_") for a in actions)

    # Ready report recommended actions
    ready_report = build_default_performance_scale_cost_readiness_report()
    assert "capture_prd8_performance_scale_cost_foundation_evidence" in ready_report.recommended_next_actions
