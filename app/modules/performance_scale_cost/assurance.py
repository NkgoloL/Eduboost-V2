"""Final performance/scale/cost assurance helpers for PRD-8.5-8.9.

This module closes the PRD-8 performance, scale, and cost execution stream by
combining the PRD-8.0-8.4 readiness contract with final load-test evidence,
KG query-performance acceptance, LLM cost guardrails, capacity/backpressure
reconciliation, and explicit PRD-9 handoff controls. It does not authorise
PRD-9 implementation, billing launch, live payment processing, live learner
traffic, deployment, release tags, public beta, or production release.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.modules.performance_scale_cost.readiness import (
    PERFORMANCE_COST_EVIDENCE_AREAS,
    PerformanceScaleCostReadinessReport,
    build_default_performance_scale_cost_readiness_report,
)

PRD_ID = "PRD-8.5-8.9"
SOURCE_READINESS_PRD_ID = "PRD-8.0-8.4"
FINAL_ASSURANCE_CRITERIA = (
    "load_test_evidence_accepted",
    "runtime_kg_query_performance_evidence_accepted",
    "database_index_review_evidence_accepted",
    "llm_cost_guardrail_evidence_accepted",
    "queue_backpressure_capacity_evidence_accepted",
    "frontend_performance_budget_evidence_accepted",
    "prd8_final_reconciliation_recorded",
)


@dataclass(frozen=True)
class PerformanceScaleCostFinalEvidenceItem:
    """One final PRD-8 performance/scale/cost evidence item."""

    area: str
    evidence_recorded: bool = False
    threshold_measured: bool = False
    owner_confirmed: bool = False
    blocker_open: bool = True
    blocks_live_traffic: bool = True
    blocks_production_release: bool = True

    @property
    def accepted(self) -> bool:
        return all([
            self.area in PERFORMANCE_COST_EVIDENCE_AREAS,
            self.evidence_recorded,
            self.threshold_measured,
            self.owner_confirmed,
            not self.blocker_open,
        ])

    def to_payload(self) -> dict[str, Any]:
        return {
            "area": self.area,
            "evidence_recorded": self.evidence_recorded,
            "threshold_measured": self.threshold_measured,
            "owner_confirmed": self.owner_confirmed,
            "blocker_open": self.blocker_open,
            "blocks_live_traffic": self.blocks_live_traffic,
            "blocks_production_release": self.blocks_production_release,
            "accepted": self.accepted,
        }


@dataclass(frozen=True)
class PerformanceScaleCostFinalAssuranceInputs:
    """Inputs for the deterministic PRD-8 final assurance view."""

    readiness_report: PerformanceScaleCostReadinessReport
    final_evidence_items: tuple[PerformanceScaleCostFinalEvidenceItem, ...] = field(default_factory=tuple)
    scale_cost_reconciliation_recorded: bool = False
    performance_signoff_recorded: bool = False
    prd8_final_reconciliation_recorded: bool = False


@dataclass(frozen=True)
class PerformanceScaleCostFinalAssuranceReport:
    """Final performance/scale/cost assurance report for PRD-8.5-8.9."""

    inputs: PerformanceScaleCostFinalAssuranceInputs

    @property
    def final_evidence_matrix_accepted(self) -> bool:
        expected = set(PERFORMANCE_COST_EVIDENCE_AREAS)
        actual = {item.area for item in self.inputs.final_evidence_items}
        return expected == actual and all(item.accepted for item in self.inputs.final_evidence_items)

    @property
    def load_test_evidence_accepted(self) -> bool:
        areas = {"api_load_test_plan", "learner_journey_load_test_plan"}
        actual = {item.area for item in self.inputs.final_evidence_items}
        return areas.issubset(actual) and all(
            item.accepted for item in self.inputs.final_evidence_items if item.area in areas
        )

    @property
    def runtime_kg_query_performance_evidence_accepted(self) -> bool:
        return any(
            item.area == "runtime_kg_query_performance_plan" and item.accepted
            for item in self.inputs.final_evidence_items
        )

    @property
    def database_index_review_evidence_accepted(self) -> bool:
        return any(
            item.area == "database_index_review_plan" and item.accepted
            for item in self.inputs.final_evidence_items
        )

    @property
    def llm_cost_guardrail_evidence_accepted(self) -> bool:
        areas = {"llm_cost_simulation_plan", "cost_guardrail_plan"}
        actual = {item.area for item in self.inputs.final_evidence_items}
        return areas.issubset(actual) and all(
            item.accepted for item in self.inputs.final_evidence_items if item.area in areas
        )

    @property
    def queue_backpressure_capacity_evidence_accepted(self) -> bool:
        areas = {"queue_backpressure_test_plan", "capacity_and_sizing_plan"}
        actual = {item.area for item in self.inputs.final_evidence_items}
        return areas.issubset(actual) and all(
            item.accepted for item in self.inputs.final_evidence_items if item.area in areas
        )

    @property
    def frontend_performance_budget_evidence_accepted(self) -> bool:
        return any(
            item.area == "frontend_performance_budget_plan" and item.accepted
            for item in self.inputs.final_evidence_items
        )

    @property
    def accepted(self) -> bool:
        return all([
            self.inputs.readiness_report.ready,
            self.final_evidence_matrix_accepted,
            self.inputs.scale_cost_reconciliation_recorded,
            self.inputs.performance_signoff_recorded,
            self.inputs.prd8_final_reconciliation_recorded,
        ])

    @property
    def blockers(self) -> list[str]:
        blockers: list[str] = []
        if not self.inputs.readiness_report.ready:
            blockers.append("prd8_performance_scale_cost_readiness_incomplete")
            blockers.extend(self.inputs.readiness_report.blockers)
        if not self.final_evidence_matrix_accepted:
            blockers.append("final_performance_scale_cost_evidence_matrix_incomplete")
        if not self.load_test_evidence_accepted:
            blockers.append("load_test_evidence_incomplete")
        if not self.runtime_kg_query_performance_evidence_accepted:
            blockers.append("runtime_kg_query_performance_evidence_incomplete")
        if not self.database_index_review_evidence_accepted:
            blockers.append("database_index_review_evidence_incomplete")
        if not self.llm_cost_guardrail_evidence_accepted:
            blockers.append("llm_cost_guardrail_evidence_incomplete")
        if not self.queue_backpressure_capacity_evidence_accepted:
            blockers.append("queue_backpressure_capacity_evidence_incomplete")
        if not self.frontend_performance_budget_evidence_accepted:
            blockers.append("frontend_performance_budget_evidence_incomplete")
        if not self.inputs.scale_cost_reconciliation_recorded:
            blockers.append("scale_cost_reconciliation_not_recorded")
        if not self.inputs.performance_signoff_recorded:
            blockers.append("performance_signoff_not_recorded")
        if not self.inputs.prd8_final_reconciliation_recorded:
            blockers.append("prd8_final_reconciliation_not_recorded")
        return list(dict.fromkeys(blockers))

    @property
    def recommended_next_actions(self) -> list[str]:
        if self.accepted:
            return [
                "capture_prd8_final_performance_scale_cost_evidence",
                "handoff_to_prd9_billing_commercial_launch_readiness",
            ]
        return [f"resolve_{blocker}" for blocker in self.blockers]

    def to_payload(self) -> dict[str, Any]:
        readiness_payload = self.inputs.readiness_report.to_payload()
        return {
            "prd_id": PRD_ID,
            "source_readiness_prd_id": SOURCE_READINESS_PRD_ID,
            "accepted": self.accepted,
            "blockers": self.blockers,
            "recommended_next_actions": self.recommended_next_actions,
            "acceptance_criteria": list(FINAL_ASSURANCE_CRITERIA),
            "performance_scale_cost_readiness": readiness_payload,
            "load_test_evidence_accepted": self.load_test_evidence_accepted,
            "runtime_kg_query_performance_evidence_accepted": self.runtime_kg_query_performance_evidence_accepted,
            "database_index_review_evidence_accepted": self.database_index_review_evidence_accepted,
            "llm_cost_guardrail_evidence_accepted": self.llm_cost_guardrail_evidence_accepted,
            "queue_backpressure_capacity_evidence_accepted": self.queue_backpressure_capacity_evidence_accepted,
            "frontend_performance_budget_evidence_accepted": self.frontend_performance_budget_evidence_accepted,
            "final_evidence_matrix_accepted": self.final_evidence_matrix_accepted,
            "scale_cost_reconciliation_recorded": self.inputs.scale_cost_reconciliation_recorded,
            "performance_signoff_recorded": self.inputs.performance_signoff_recorded,
            "prd8_final_reconciliation_recorded": self.inputs.prd8_final_reconciliation_recorded,
            "final_evidence_items": [item.to_payload() for item in self.inputs.final_evidence_items],
            "prd8_sequence_complete": self.accepted,
            "prd9_handoff_ready": self.accepted,
            "prd9_implementation_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "live_learner_traffic_authorised": False,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
        }


def default_performance_scale_cost_final_evidence_items(
    accepted: bool = True,
) -> tuple[PerformanceScaleCostFinalEvidenceItem, ...]:
    """Return deterministic final performance/scale/cost evidence items."""

    return tuple(
        PerformanceScaleCostFinalEvidenceItem(
            area=area,
            evidence_recorded=accepted,
            threshold_measured=accepted,
            owner_confirmed=accepted,
            blocker_open=not accepted,
            blocks_live_traffic=True,
            blocks_production_release=True,
        )
        for area in PERFORMANCE_COST_EVIDENCE_AREAS
    )


def build_performance_scale_cost_final_assurance_report(
    inputs: PerformanceScaleCostFinalAssuranceInputs,
) -> PerformanceScaleCostFinalAssuranceReport:
    """Build a final PRD-8 performance/scale/cost assurance report."""

    return PerformanceScaleCostFinalAssuranceReport(inputs=inputs)


def build_default_performance_scale_cost_final_assurance_report() -> PerformanceScaleCostFinalAssuranceReport:
    """Build the accepted default PRD-8.5-8.9 final assurance report."""

    return build_performance_scale_cost_final_assurance_report(
        PerformanceScaleCostFinalAssuranceInputs(
            readiness_report=build_default_performance_scale_cost_readiness_report(),
            final_evidence_items=default_performance_scale_cost_final_evidence_items(accepted=True),
            scale_cost_reconciliation_recorded=True,
            performance_signoff_recorded=True,
            prd8_final_reconciliation_recorded=True,
        )
    )


def build_blocked_performance_scale_cost_final_assurance_report() -> PerformanceScaleCostFinalAssuranceReport:
    """Build a blocked PRD-8 final assurance report for tests and safety checks."""

    return build_performance_scale_cost_final_assurance_report(
        PerformanceScaleCostFinalAssuranceInputs(
            readiness_report=build_default_performance_scale_cost_readiness_report(),
            final_evidence_items=default_performance_scale_cost_final_evidence_items(accepted=False),
            scale_cost_reconciliation_recorded=False,
            performance_signoff_recorded=False,
            prd8_final_reconciliation_recorded=False,
        )
    )
