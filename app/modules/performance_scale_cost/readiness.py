"""Performance, scale, and cost execution readiness helpers for PRD-8.0-8.4.

The helper exposes a deterministic readiness contract for load testing, KG
query performance, database/index review, LLM cost simulation, queue/backpressure
controls, and frontend performance budgets. It does not run load tests, modify
infrastructure, enable live learner traffic, authorise billing, or authorise
production release.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PRD_ID = "PRD-8.0-8.4"
PERFORMANCE_SCOPE_ITEMS = (
    "load_test_readiness",
    "runtime_kg_query_performance_readiness",
    "database_index_review_readiness",
    "llm_cost_simulation_readiness",
    "queue_backpressure_readiness",
    "frontend_performance_budget_readiness",
    "capacity_plan_readiness",
)
PERFORMANCE_COST_EVIDENCE_AREAS = (
    "api_load_test_plan",
    "learner_journey_load_test_plan",
    "runtime_kg_query_performance_plan",
    "database_index_review_plan",
    "llm_cost_simulation_plan",
    "queue_backpressure_test_plan",
    "frontend_performance_budget_plan",
    "capacity_and_sizing_plan",
    "cost_guardrail_plan",
)
RECOMMENDED_PERFORMANCE_THRESHOLDS = {
    "api_p95_ms": 750,
    "critical_route_p95_ms": 1200,
    "runtime_kg_query_p95_ms": 250,
    "frontend_lcp_ms": 2500,
    "frontend_cls_max": 0.1,
    "llm_cost_per_active_learner_monthly_cap_usd": 2.50,
}
FALSE_RELEASE_BOUNDARIES = {
    "prd9_implementation_authorised": False,
    "production_release_authorised": False,
    "deployment_authorised": False,
    "release_tag_authorised": False,
    "public_beta_authorised": False,
    "live_learner_traffic_authorised": False,
    "billing_launch_authorised": False,
    "live_payment_processing_authorised": False,
}


@dataclass(frozen=True)
class PerformanceScaleCostEvidenceControl:
    """One PRD-8 evidence area and its readiness controls."""

    area: str
    owner_assigned: bool = False
    evidence_path_defined: bool = False
    threshold_defined: bool = False
    drill_or_test_defined: bool = False
    blocks_live_traffic: bool = True

    @property
    def ready(self) -> bool:
        return all([
            self.owner_assigned,
            self.evidence_path_defined,
            self.threshold_defined,
            self.drill_or_test_defined,
        ])

    def to_payload(self) -> dict[str, Any]:
        return {
            "area": self.area,
            "owner_assigned": self.owner_assigned,
            "evidence_path_defined": self.evidence_path_defined,
            "threshold_defined": self.threshold_defined,
            "drill_or_test_defined": self.drill_or_test_defined,
            "blocks_live_traffic": self.blocks_live_traffic,
            "ready": self.ready,
        }


@dataclass(frozen=True)
class PerformanceScaleCostReadinessInputs:
    """Inputs for the deterministic PRD-8 readiness view."""

    load_tests_defined: bool = False
    runtime_kg_query_performance_defined: bool = False
    database_index_review_defined: bool = False
    llm_cost_simulation_defined: bool = False
    queue_backpressure_tests_defined: bool = False
    frontend_performance_budget_defined: bool = False
    capacity_plan_defined: bool = False
    cost_guardrails_defined: bool = False
    evidence_controls: tuple[PerformanceScaleCostEvidenceControl, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PerformanceScaleCostReadinessReport:
    """PRD-8.0-8.4 performance, scale, and cost readiness report."""

    inputs: PerformanceScaleCostReadinessInputs

    @property
    def evidence_matrix_ready(self) -> bool:
        expected = set(PERFORMANCE_COST_EVIDENCE_AREAS)
        actual = {control.area for control in self.inputs.evidence_controls}
        return expected == actual and all(control.ready for control in self.inputs.evidence_controls)

    @property
    def performance_execution_defined(self) -> bool:
        return all([
            self.inputs.load_tests_defined,
            self.inputs.runtime_kg_query_performance_defined,
            self.inputs.database_index_review_defined,
            self.inputs.frontend_performance_budget_defined,
        ])

    @property
    def scale_execution_defined(self) -> bool:
        return all([
            self.inputs.queue_backpressure_tests_defined,
            self.inputs.capacity_plan_defined,
        ])

    @property
    def cost_execution_defined(self) -> bool:
        return all([
            self.inputs.llm_cost_simulation_defined,
            self.inputs.cost_guardrails_defined,
        ])

    @property
    def ready(self) -> bool:
        return all([
            self.performance_execution_defined,
            self.scale_execution_defined,
            self.cost_execution_defined,
            self.evidence_matrix_ready,
        ])

    @property
    def blockers(self) -> list[str]:
        blockers: list[str] = []
        if not self.inputs.load_tests_defined:
            blockers.append("load_tests_missing")
        if not self.inputs.runtime_kg_query_performance_defined:
            blockers.append("runtime_kg_query_performance_missing")
        if not self.inputs.database_index_review_defined:
            blockers.append("database_index_review_missing")
        if not self.inputs.llm_cost_simulation_defined:
            blockers.append("llm_cost_simulation_missing")
        if not self.inputs.queue_backpressure_tests_defined:
            blockers.append("queue_backpressure_tests_missing")
        if not self.inputs.frontend_performance_budget_defined:
            blockers.append("frontend_performance_budget_missing")
        if not self.inputs.capacity_plan_defined:
            blockers.append("capacity_plan_missing")
        if not self.inputs.cost_guardrails_defined:
            blockers.append("cost_guardrails_missing")
        if not self.evidence_matrix_ready:
            blockers.append("performance_scale_cost_evidence_matrix_incomplete")
        return blockers

    @property
    def recommended_next_actions(self) -> list[str]:
        if self.ready:
            return [
                "capture_prd8_performance_scale_cost_foundation_evidence",
                "prepare_prd8_final_performance_scale_cost_handoff",
            ]
        return [f"resolve_{blocker}" for blocker in self.blockers]

    def to_payload(self) -> dict[str, Any]:
        return {
            "prd_id": PRD_ID,
            "ready": self.ready,
            "blockers": self.blockers,
            "recommended_next_actions": self.recommended_next_actions,
            "scope_items": list(PERFORMANCE_SCOPE_ITEMS),
            "evidence_areas": list(PERFORMANCE_COST_EVIDENCE_AREAS),
            "recommended_thresholds": RECOMMENDED_PERFORMANCE_THRESHOLDS,
            "load_tests_defined": self.inputs.load_tests_defined,
            "runtime_kg_query_performance_defined": self.inputs.runtime_kg_query_performance_defined,
            "database_index_review_defined": self.inputs.database_index_review_defined,
            "llm_cost_simulation_defined": self.inputs.llm_cost_simulation_defined,
            "queue_backpressure_tests_defined": self.inputs.queue_backpressure_tests_defined,
            "frontend_performance_budget_defined": self.inputs.frontend_performance_budget_defined,
            "capacity_plan_defined": self.inputs.capacity_plan_defined,
            "cost_guardrails_defined": self.inputs.cost_guardrails_defined,
            "performance_execution_defined": self.performance_execution_defined,
            "scale_execution_defined": self.scale_execution_defined,
            "cost_execution_defined": self.cost_execution_defined,
            "evidence_matrix_ready": self.evidence_matrix_ready,
            "evidence_controls": [control.to_payload() for control in self.inputs.evidence_controls],
            **FALSE_RELEASE_BOUNDARIES,
        }


def default_performance_scale_cost_evidence_controls() -> tuple[PerformanceScaleCostEvidenceControl, ...]:
    """Return the deterministic PRD-8.0-8.4 evidence-control matrix."""

    return tuple(
        PerformanceScaleCostEvidenceControl(
            area=area,
            owner_assigned=True,
            evidence_path_defined=True,
            threshold_defined=True,
            drill_or_test_defined=True,
        )
        for area in PERFORMANCE_COST_EVIDENCE_AREAS
    )


def build_default_performance_scale_cost_readiness_report() -> PerformanceScaleCostReadinessReport:
    """Build the accepted PRD-8.0-8.4 readiness report."""

    return PerformanceScaleCostReadinessReport(
        PerformanceScaleCostReadinessInputs(
            load_tests_defined=True,
            runtime_kg_query_performance_defined=True,
            database_index_review_defined=True,
            llm_cost_simulation_defined=True,
            queue_backpressure_tests_defined=True,
            frontend_performance_budget_defined=True,
            capacity_plan_defined=True,
            cost_guardrails_defined=True,
            evidence_controls=default_performance_scale_cost_evidence_controls(),
        )
    )


def build_blocked_performance_scale_cost_readiness_report() -> PerformanceScaleCostReadinessReport:
    """Build a blocked report used by tests to prove failure semantics."""

    return PerformanceScaleCostReadinessReport(PerformanceScaleCostReadinessInputs())
