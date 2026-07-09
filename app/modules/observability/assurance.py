"""Final observability/SRE assurance helpers for PRD-7.5-7.9.

This module closes the PRD-7 observability, SRE, and incident-readiness
stream by combining the PRD-7.0-7.4 readiness contract with final evidence,
incident readiness reconciliation, and explicit PRD-8 handoff controls. It does
not authorise PRD-8 implementation, live learner traffic, billing, deployment,
release tags, public beta, or production release.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.modules.observability.readiness import (
    OBSERVABILITY_EVIDENCE_AREAS,
    ObservabilitySreReadinessReport,
    build_default_observability_sre_readiness_report,
)

PRD_ID = "PRD-7.5-7.9"
SOURCE_READINESS_PRD_ID = "PRD-7.0-7.4"
FINAL_ASSURANCE_CRITERIA = (
    "dashboard_alert_slo_evidence_accepted",
    "incident_runbook_on_call_evidence_accepted",
    "backup_restore_rollback_evidence_accepted",
    "privacy_escalation_support_evidence_accepted",
    "telemetry_pii_redaction_evidence_accepted",
    "prd7_final_reconciliation_recorded",
)


@dataclass(frozen=True)
class ObservabilityFinalEvidenceItem:
    """One final PRD-7 observability/SRE evidence item."""

    area: str
    evidence_recorded: bool = False
    drill_or_runbook_exercised: bool = False
    owner_confirmed: bool = False
    blocker_open: bool = True
    blocks_live_traffic: bool = True
    blocks_production_release: bool = True

    @property
    def accepted(self) -> bool:
        return all([
            self.area in OBSERVABILITY_EVIDENCE_AREAS,
            self.evidence_recorded,
            self.drill_or_runbook_exercised,
            self.owner_confirmed,
            not self.blocker_open,
        ])

    def to_payload(self) -> dict[str, Any]:
        return {
            "area": self.area,
            "evidence_recorded": self.evidence_recorded,
            "drill_or_runbook_exercised": self.drill_or_runbook_exercised,
            "owner_confirmed": self.owner_confirmed,
            "blocker_open": self.blocker_open,
            "blocks_live_traffic": self.blocks_live_traffic,
            "blocks_production_release": self.blocks_production_release,
            "accepted": self.accepted,
        }


@dataclass(frozen=True)
class ObservabilityFinalAssuranceInputs:
    """Inputs for the deterministic PRD-7 final assurance view."""

    readiness_report: ObservabilitySreReadinessReport
    final_evidence_items: tuple[ObservabilityFinalEvidenceItem, ...] = field(default_factory=tuple)
    incident_readiness_reconciliation_recorded: bool = False
    sre_signoff_recorded: bool = False
    prd7_final_reconciliation_recorded: bool = False


@dataclass(frozen=True)
class ObservabilityFinalAssuranceReport:
    """Final observability/SRE assurance report for PRD-7.5-7.9."""

    inputs: ObservabilityFinalAssuranceInputs

    @property
    def final_evidence_matrix_accepted(self) -> bool:
        expected = set(OBSERVABILITY_EVIDENCE_AREAS)
        actual = {item.area for item in self.inputs.final_evidence_items}
        return expected == actual and all(item.accepted for item in self.inputs.final_evidence_items)

    @property
    def dashboard_alert_slo_evidence_accepted(self) -> bool:
        areas = {"metrics_dashboard", "logs_traces_correlation", "slo_burn_alerts"}
        actual = {item.area for item in self.inputs.final_evidence_items}
        return areas.issubset(actual) and all(
            item.accepted for item in self.inputs.final_evidence_items if item.area in areas
        )

    @property
    def incident_runbook_on_call_evidence_accepted(self) -> bool:
        areas = {"incident_runbooks", "on_call_ownership"}
        actual = {item.area for item in self.inputs.final_evidence_items}
        return areas.issubset(actual) and all(
            item.accepted for item in self.inputs.final_evidence_items if item.area in areas
        )

    @property
    def backup_restore_rollback_evidence_accepted(self) -> bool:
        areas = {"backup_restore_drill", "rollback_drill"}
        actual = {item.area for item in self.inputs.final_evidence_items}
        return areas.issubset(actual) and all(
            item.accepted for item in self.inputs.final_evidence_items if item.area in areas
        )

    @property
    def privacy_escalation_support_evidence_accepted(self) -> bool:
        areas = {"privacy_escalation_process", "support_status_comms"}
        actual = {item.area for item in self.inputs.final_evidence_items}
        return areas.issubset(actual) and all(
            item.accepted for item in self.inputs.final_evidence_items if item.area in areas
        )

    @property
    def telemetry_pii_redaction_evidence_accepted(self) -> bool:
        return any(
            item.area == "telemetry_pii_redaction" and item.accepted
            for item in self.inputs.final_evidence_items
        )

    @property
    def accepted(self) -> bool:
        return all([
            self.inputs.readiness_report.ready,
            self.final_evidence_matrix_accepted,
            self.inputs.incident_readiness_reconciliation_recorded,
            self.inputs.sre_signoff_recorded,
            self.inputs.prd7_final_reconciliation_recorded,
        ])

    @property
    def blockers(self) -> list[str]:
        blockers: list[str] = []
        if not self.inputs.readiness_report.ready:
            blockers.append("prd7_observability_sre_readiness_incomplete")
            blockers.extend(self.inputs.readiness_report.blockers)
        if not self.final_evidence_matrix_accepted:
            blockers.append("final_observability_sre_evidence_matrix_incomplete")
        if not self.dashboard_alert_slo_evidence_accepted:
            blockers.append("dashboard_alert_slo_evidence_incomplete")
        if not self.incident_runbook_on_call_evidence_accepted:
            blockers.append("incident_runbook_on_call_evidence_incomplete")
        if not self.backup_restore_rollback_evidence_accepted:
            blockers.append("backup_restore_rollback_evidence_incomplete")
        if not self.privacy_escalation_support_evidence_accepted:
            blockers.append("privacy_escalation_support_evidence_incomplete")
        if not self.telemetry_pii_redaction_evidence_accepted:
            blockers.append("telemetry_pii_redaction_evidence_incomplete")
        if not self.inputs.incident_readiness_reconciliation_recorded:
            blockers.append("incident_readiness_reconciliation_not_recorded")
        if not self.inputs.sre_signoff_recorded:
            blockers.append("sre_signoff_not_recorded")
        if not self.inputs.prd7_final_reconciliation_recorded:
            blockers.append("prd7_final_reconciliation_not_recorded")
        return list(dict.fromkeys(blockers))

    @property
    def recommended_next_actions(self) -> list[str]:
        if self.accepted:
            return [
                "capture_prd7_final_observability_sre_evidence",
                "handoff_to_prd8_performance_scale_cost_execution",
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
            "observability_sre_readiness": readiness_payload,
            "dashboard_alert_slo_evidence_accepted": self.dashboard_alert_slo_evidence_accepted,
            "incident_runbook_on_call_evidence_accepted": self.incident_runbook_on_call_evidence_accepted,
            "backup_restore_rollback_evidence_accepted": self.backup_restore_rollback_evidence_accepted,
            "privacy_escalation_support_evidence_accepted": self.privacy_escalation_support_evidence_accepted,
            "telemetry_pii_redaction_evidence_accepted": self.telemetry_pii_redaction_evidence_accepted,
            "final_evidence_matrix_accepted": self.final_evidence_matrix_accepted,
            "incident_readiness_reconciliation_recorded": self.inputs.incident_readiness_reconciliation_recorded,
            "sre_signoff_recorded": self.inputs.sre_signoff_recorded,
            "prd7_final_reconciliation_recorded": self.inputs.prd7_final_reconciliation_recorded,
            "final_evidence_items": [item.to_payload() for item in self.inputs.final_evidence_items],
            "prd7_sequence_complete": self.accepted,
            "prd8_handoff_ready": self.accepted,
            "prd8_implementation_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "live_learner_traffic_authorised": False,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
        }


def default_observability_final_evidence_items(
    accepted: bool = True,
) -> tuple[ObservabilityFinalEvidenceItem, ...]:
    """Return deterministic final observability/SRE evidence items."""

    return tuple(
        ObservabilityFinalEvidenceItem(
            area=area,
            evidence_recorded=accepted,
            drill_or_runbook_exercised=accepted,
            owner_confirmed=accepted,
            blocker_open=not accepted,
            blocks_live_traffic=True,
            blocks_production_release=True,
        )
        for area in OBSERVABILITY_EVIDENCE_AREAS
    )


def build_observability_final_assurance_report(
    inputs: ObservabilityFinalAssuranceInputs,
) -> ObservabilityFinalAssuranceReport:
    """Build a final PRD-7 observability/SRE assurance report."""

    return ObservabilityFinalAssuranceReport(inputs=inputs)


def build_default_observability_final_assurance_report() -> ObservabilityFinalAssuranceReport:
    """Build the accepted default PRD-7.5-7.9 final assurance report."""

    return build_observability_final_assurance_report(
        ObservabilityFinalAssuranceInputs(
            readiness_report=build_default_observability_sre_readiness_report(),
            final_evidence_items=default_observability_final_evidence_items(accepted=True),
            incident_readiness_reconciliation_recorded=True,
            sre_signoff_recorded=True,
            prd7_final_reconciliation_recorded=True,
        )
    )


def build_blocked_observability_final_assurance_report() -> ObservabilityFinalAssuranceReport:
    """Build a blocked PRD-7 final assurance report for tests and safety checks."""

    return build_observability_final_assurance_report(
        ObservabilityFinalAssuranceInputs(
            readiness_report=build_default_observability_sre_readiness_report(),
            final_evidence_items=default_observability_final_evidence_items(accepted=False),
            incident_readiness_reconciliation_recorded=False,
            sre_signoff_recorded=False,
            prd7_final_reconciliation_recorded=False,
        )
    )
