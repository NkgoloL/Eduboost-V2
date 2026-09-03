from app.modules.performance_scale_cost import (
    PERFORMANCE_COST_EVIDENCE_AREAS,
    build_blocked_performance_scale_cost_final_assurance_report,
    build_default_performance_scale_cost_final_assurance_report,
    default_performance_scale_cost_final_evidence_items,
)


def test_default_performance_final_assurance_is_accepted_and_boundary_safe():
    payload = build_default_performance_scale_cost_final_assurance_report().to_payload()

    assert payload["prd_id"] == "PRD-8.5-8.9"
    assert payload["source_readiness_prd_id"] == "PRD-8.0-8.4"
    assert payload["accepted"] is True
    assert payload["load_test_evidence_accepted"] is True
    assert payload["runtime_kg_query_performance_evidence_accepted"] is True
    assert payload["llm_cost_guardrail_evidence_accepted"] is True
    assert payload["queue_backpressure_capacity_evidence_accepted"] is True
    assert payload["frontend_performance_budget_evidence_accepted"] is True
    assert payload["prd9_handoff_ready"] is True
    assert payload["prd9_implementation_authorised"] is False
    assert payload["billing_launch_authorised"] is False
    assert payload["live_payment_processing_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False


def test_blocked_performance_final_assurance_reports_missing_evidence():
    payload = build_blocked_performance_scale_cost_final_assurance_report().to_payload()

    assert payload["accepted"] is False
    assert "final_performance_scale_cost_evidence_matrix_incomplete" in payload["blockers"]
    assert "scale_cost_reconciliation_not_recorded" in payload["blockers"]
    assert "performance_signoff_not_recorded" in payload["blockers"]


def test_performance_final_evidence_items_cover_all_foundation_areas():
    evidence_items = default_performance_scale_cost_final_evidence_items()

    assert {item.area for item in evidence_items} == set(PERFORMANCE_COST_EVIDENCE_AREAS)
    assert all(item.accepted for item in evidence_items)


def test_performance_final_assurance_granular_blockers_and_actions():
    from app.modules.performance_scale_cost.assurance import (
        PerformanceScaleCostFinalAssuranceInputs,
        PerformanceScaleCostFinalAssuranceReport,
        PerformanceScaleCostFinalEvidenceItem,
    )
    from app.modules.performance_scale_cost.readiness import build_default_performance_scale_cost_readiness_report

    # Test single final evidence item payload and accepted property
    item = PerformanceScaleCostFinalEvidenceItem(area="invalid_area", evidence_recorded=True, threshold_measured=True, owner_confirmed=True, blocker_open=False)
    assert item.accepted is False
    assert item.to_payload()["accepted"] is False

    # Blocked assurance report with empty evidence items
    inputs = PerformanceScaleCostFinalAssuranceInputs(
        readiness_report=build_default_performance_scale_cost_readiness_report(),
        final_evidence_items=(),
        scale_cost_reconciliation_recorded=False,
        performance_signoff_recorded=False,
        prd8_final_reconciliation_recorded=False,
    )
    report = PerformanceScaleCostFinalAssuranceReport(inputs=inputs)
    assert report.accepted is False
    assert report.final_evidence_matrix_accepted is False
    assert report.load_test_evidence_accepted is False
    assert report.runtime_kg_query_performance_evidence_accepted is False
    assert report.database_index_review_evidence_accepted is False
    assert report.llm_cost_guardrail_evidence_accepted is False
    assert report.queue_backpressure_capacity_evidence_accepted is False
    assert report.frontend_performance_budget_evidence_accepted is False

    blockers = report.blockers
    assert "final_performance_scale_cost_evidence_matrix_incomplete" in blockers
    assert "load_test_evidence_incomplete" in blockers
    assert "runtime_kg_query_performance_evidence_incomplete" in blockers
    assert "database_index_review_evidence_incomplete" in blockers
    assert "llm_cost_guardrail_evidence_incomplete" in blockers
    assert "queue_backpressure_capacity_evidence_incomplete" in blockers
    assert "frontend_performance_budget_evidence_incomplete" in blockers
    assert "scale_cost_reconciliation_not_recorded" in blockers
    assert "performance_signoff_not_recorded" in blockers
    assert "prd8_final_reconciliation_not_recorded" in blockers

    actions = report.recommended_next_actions
    assert any(a.startswith("resolve_") for a in actions)

    # Accepted assurance report actions
    accepted_report = build_default_performance_scale_cost_final_assurance_report()
    assert "capture_prd8_final_performance_scale_cost_evidence" in accepted_report.recommended_next_actions
