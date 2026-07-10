"""PRD-11.0R true-state runtime baseline restoration contracts.

This module intentionally does not authorise release.  It records an operational
hold until runtime evidence proves that the live/disposable stack, schema,
product gates, security gates, and generated contracts are green.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PRD_ID = "PRD-11.0R"

TRUE_STATE_CONCERN_CATEGORIES = (
    "operational_hold",
    "runtime_readiness_probe",
    "database_lineage_and_schema",
    "disposable_stack_restore",
    "popia_runtime_wiring",
    "product_test_gates",
    "frontend_quality_gates",
    "openapi_route_inventory_drift",
    "dependency_security_audits",
    "secret_baseline_triage",
    "coverage_baseline",
    "billing_runtime_contracts",
    "backup_restore_rollback_incident_drills",
    "external_security_privacy_content_operations_gates",
)

FALSE_RELEASE_BOUNDARIES = {
    "production_release_authorised": False,
    "deployment_authorised": False,
    "release_tag_authorised": False,
    "public_beta_authorised": False,
    "public_beta_live_traffic_authorised": False,
    "billing_launch_authorised": False,
    "live_payment_processing_authorised": False,
    "prd12_implementation_authorised": False,
}

DEFAULT_BLOCKERS = (
    "runtime_baseline_not_yet_green",
    "ready_probe_not_proven_200",
    "database_lineage_not_proven_at_repository_head",
    "schema_drift_not_proven_clean",
    "backend_product_gates_not_proven_green",
    "frontend_quality_gates_not_proven_green",
    "dependency_security_audits_not_proven_clean_or_accepted",
    "external_approvals_not_recorded",
)


@dataclass(frozen=True)
class TrueStateRuntimeBaselineReport:
    """PRD-11.0R runtime-baseline evidence-hardening payload.

    ``accepted`` means the operational hold and evidence-hardening gate are
    installed.  It does not mean release readiness.  Release readiness is
    represented by ``runtime_baseline_green`` and remains false until actual
    runtime evidence proves every hard gate.
    """

    accepted: bool = True
    prd_id: str = PRD_ID
    report_scope: str = "true_state_runtime_baseline_restoration_and_evidence_hardening"
    concern_categories: tuple[str, ...] = TRUE_STATE_CONCERN_CATEGORIES
    blockers: tuple[str, ...] = DEFAULT_BLOCKERS
    runtime_baseline_green: bool = False
    runtime_baseline_status: str = "red_no_go_operational_hold_active"
    controlled_beta_live_traffic_authorised: bool = True
    live_learner_traffic_authorised: bool = True
    controlled_beta_activation_operational_hold: bool = True
    live_learner_traffic_operationally_safe: bool = False
    production_release_evidence_blocked_until_runtime_baseline_green: bool = True
    true_state_report_reconciled: bool = True
    runtime_evidence_mode: str = "actual_probe_evidence_required_not_constant_status"
    baseline_green_required_before_prd1100_evidence_capture: bool = True
    next_action: str = "restore_disposable_stack_and_collect_green_runtime_baseline"
    boundaries: dict[str, bool] = field(default_factory=lambda: dict(FALSE_RELEASE_BOUNDARIES))

    def to_payload(self) -> dict[str, Any]:
        return {
            "prd_id": self.prd_id,
            "accepted": self.accepted,
            "report_scope": self.report_scope,
            "concern_categories": list(self.concern_categories),
            "blockers": list(self.blockers),
            "runtime_baseline_green": self.runtime_baseline_green,
            "runtime_baseline_status": self.runtime_baseline_status,
            "controlled_beta_live_traffic_authorised": self.controlled_beta_live_traffic_authorised,
            "live_learner_traffic_authorised": self.live_learner_traffic_authorised,
            "controlled_beta_activation_operational_hold": self.controlled_beta_activation_operational_hold,
            "live_learner_traffic_operationally_safe": self.live_learner_traffic_operationally_safe,
            "production_release_evidence_blocked_until_runtime_baseline_green": (
                self.production_release_evidence_blocked_until_runtime_baseline_green
            ),
            "true_state_report_reconciled": self.true_state_report_reconciled,
            "runtime_evidence_mode": self.runtime_evidence_mode,
            "baseline_green_required_before_prd1100_evidence_capture": (
                self.baseline_green_required_before_prd1100_evidence_capture
            ),
            "next_action": self.next_action,
            **self.boundaries,
        }


def build_default_true_state_runtime_baseline_report() -> TrueStateRuntimeBaselineReport:
    return TrueStateRuntimeBaselineReport()


def build_green_true_state_runtime_baseline_report() -> TrueStateRuntimeBaselineReport:
    return TrueStateRuntimeBaselineReport(
        blockers=(),
        runtime_baseline_green=True,
        runtime_baseline_status="green_runtime_baseline_restored",
        controlled_beta_activation_operational_hold=False,
        live_learner_traffic_operationally_safe=True,
        production_release_evidence_blocked_until_runtime_baseline_green=False,
        next_action="prd1100_1104_preflight_evidence_capture_may_proceed",
    )
