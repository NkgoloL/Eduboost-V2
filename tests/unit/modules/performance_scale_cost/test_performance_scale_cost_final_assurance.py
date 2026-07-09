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
