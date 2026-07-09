"""Observability, SRE, and incident readiness helpers for PRD-7.0-7.4.

These helpers expose a deterministic readiness contract for dashboards, alerts,
SLOs, incident runbooks, on-call ownership, backup/restore/rollback proof, and
privacy escalation. They do not connect to a live telemetry backend, modify
infrastructure, enable live learner traffic, or authorise production release.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.modules.observability.production_readiness_contracts import (
    DEFAULT_ALERTS,
    DEFAULT_DASHBOARDS,
    DEFAULT_LOG_EVENTS,
    DEFAULT_METRICS,
    DEFAULT_PROVIDER_DECISION,
    DEFAULT_RETENTION_POLICY,
    DEFAULT_SLOS,
    DEFAULT_TRACE_SPANS,
    default_observability_readiness_report,
)

PRD_ID = "PRD-7.0-7.4"
OBSERVABILITY_SCOPE_ITEMS = (
    "dashboard_readiness",
    "alert_and_slo_readiness",
    "incident_runbook_readiness",
    "on_call_ownership_readiness",
    "backup_restore_rollback_readiness",
    "privacy_escalation_readiness",
)
OBSERVABILITY_EVIDENCE_AREAS = (
    "metrics_dashboard",
    "logs_traces_correlation",
    "slo_burn_alerts",
    "incident_runbooks",
    "on_call_ownership",
    "backup_restore_drill",
    "rollback_drill",
    "privacy_escalation_process",
    "telemetry_pii_redaction",
    "support_status_comms",
)
REQUIRED_RUNBOOKS = (
    "api_error_rate_high",
    "llm_provider_failure_spike",
    "privacy_export_failure",
    "backup_restore_failure",
    "rollback_decision",
)
RECOMMENDED_BACKENDS = (
    "prometheus_or_managed_metrics",
    "structured_json_logs",
    "opentelemetry_collector",
    "sentry_or_managed_error_tracking",
    "alertmanager_or_managed_pager",
)


@dataclass(frozen=True)
class ObservabilityEvidenceControl:
    """One observability/SRE evidence area and its readiness controls."""

    area: str
    owner_assigned: bool = False
    evidence_path_defined: bool = False
    runbook_or_drill_defined: bool = False
    blocks_live_traffic: bool = True

    @property
    def ready(self) -> bool:
        return all([
            self.owner_assigned,
            self.evidence_path_defined,
            self.runbook_or_drill_defined,
        ])

    def to_payload(self) -> dict[str, Any]:
        return {
            "area": self.area,
            "owner_assigned": self.owner_assigned,
            "evidence_path_defined": self.evidence_path_defined,
            "runbook_or_drill_defined": self.runbook_or_drill_defined,
            "blocks_live_traffic": self.blocks_live_traffic,
            "ready": self.ready,
        }


@dataclass(frozen=True)
class ObservabilitySreReadinessInputs:
    """Inputs for the deterministic PRD-7 observability/SRE readiness view."""

    dashboards_defined: bool = False
    alerts_defined: bool = False
    slos_defined: bool = False
    incident_runbooks_defined: bool = False
    on_call_ownership_defined: bool = False
    backup_restore_drill_defined: bool = False
    rollback_drill_defined: bool = False
    privacy_escalation_process_defined: bool = False
    telemetry_pii_redaction_defined: bool = False
    support_status_comms_defined: bool = False
    evidence_controls: tuple[ObservabilityEvidenceControl, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ObservabilitySreReadinessReport:
    """PRD-7.0-7.4 observability/SRE readiness report."""

    inputs: ObservabilitySreReadinessInputs

    @property
    def evidence_matrix_ready(self) -> bool:
        expected = set(OBSERVABILITY_EVIDENCE_AREAS)
        actual = {control.area for control in self.inputs.evidence_controls}
        return expected == actual and all(control.ready for control in self.inputs.evidence_controls)

    @property
    def telemetry_readiness_defined(self) -> bool:
        contract = default_observability_readiness_report()
        return all([
            self.inputs.dashboards_defined,
            self.inputs.alerts_defined,
            self.inputs.slos_defined,
            self.inputs.telemetry_pii_redaction_defined,
            not contract["provider_decision_issues"],
            not contract["metric_issues"],
            not contract["log_event_issues"],
            not contract["trace_span_issues"],
            not contract["slo_issues"],
            not contract["alert_issues"],
            not contract["dashboard_issues"],
            not contract["retention_issues"],
        ])

    @property
    def incident_readiness_defined(self) -> bool:
        return all([
            self.inputs.incident_runbooks_defined,
            self.inputs.on_call_ownership_defined,
            self.inputs.privacy_escalation_process_defined,
            self.inputs.support_status_comms_defined,
        ])

    @property
    def resilience_drills_defined(self) -> bool:
        return all([
            self.inputs.backup_restore_drill_defined,
            self.inputs.rollback_drill_defined,
        ])

    @property
    def ready(self) -> bool:
        return all([
            self.telemetry_readiness_defined,
            self.incident_readiness_defined,
            self.resilience_drills_defined,
            self.evidence_matrix_ready,
        ])

    @property
    def blockers(self) -> list[str]:
        blockers: list[str] = []
        if not self.inputs.dashboards_defined:
            blockers.append("dashboards_missing")
        if not self.inputs.alerts_defined:
            blockers.append("alerts_missing")
        if not self.inputs.slos_defined:
            blockers.append("slos_missing")
        if not self.inputs.incident_runbooks_defined:
            blockers.append("incident_runbooks_missing")
        if not self.inputs.on_call_ownership_defined:
            blockers.append("on_call_ownership_missing")
        if not self.inputs.backup_restore_drill_defined:
            blockers.append("backup_restore_drill_missing")
        if not self.inputs.rollback_drill_defined:
            blockers.append("rollback_drill_missing")
        if not self.inputs.privacy_escalation_process_defined:
            blockers.append("privacy_escalation_process_missing")
        if not self.inputs.telemetry_pii_redaction_defined:
            blockers.append("telemetry_pii_redaction_missing")
        if not self.inputs.support_status_comms_defined:
            blockers.append("support_status_comms_missing")
        if not self.evidence_matrix_ready:
            blockers.append("observability_sre_evidence_matrix_incomplete")
        return blockers

    @property
    def recommended_next_actions(self) -> list[str]:
        if self.ready:
            return [
                "capture_prd7_observability_sre_foundation_evidence",
                "prepare_prd7_final_incident_readiness_handoff",
            ]
        return [f"resolve_{blocker}" for blocker in self.blockers]

    def to_payload(self) -> dict[str, Any]:
        contract = default_observability_readiness_report()
        return {
            "prd_id": PRD_ID,
            "ready": self.ready,
            "blockers": self.blockers,
            "recommended_next_actions": self.recommended_next_actions,
            "scope_items": list(OBSERVABILITY_SCOPE_ITEMS),
            "observability_evidence_areas": list(OBSERVABILITY_EVIDENCE_AREAS),
            "required_runbooks": list(REQUIRED_RUNBOOKS),
            "recommended_backends": list(RECOMMENDED_BACKENDS),
            "dashboards_defined": self.inputs.dashboards_defined,
            "alerts_defined": self.inputs.alerts_defined,
            "slos_defined": self.inputs.slos_defined,
            "incident_runbooks_defined": self.inputs.incident_runbooks_defined,
            "on_call_ownership_defined": self.inputs.on_call_ownership_defined,
            "backup_restore_drill_defined": self.inputs.backup_restore_drill_defined,
            "rollback_drill_defined": self.inputs.rollback_drill_defined,
            "privacy_escalation_process_defined": self.inputs.privacy_escalation_process_defined,
            "telemetry_pii_redaction_defined": self.inputs.telemetry_pii_redaction_defined,
            "support_status_comms_defined": self.inputs.support_status_comms_defined,
            "telemetry_readiness_defined": self.telemetry_readiness_defined,
            "incident_readiness_defined": self.incident_readiness_defined,
            "resilience_drills_defined": self.resilience_drills_defined,
            "evidence_matrix_ready": self.evidence_matrix_ready,
            "evidence_controls": [control.to_payload() for control in self.inputs.evidence_controls],
            "existing_observability_contract": {
                "provider_decision": DEFAULT_PROVIDER_DECISION.__dict__,
                "metric_count": len(DEFAULT_METRICS),
                "log_event_count": len(DEFAULT_LOG_EVENTS),
                "trace_span_count": len(DEFAULT_TRACE_SPANS),
                "slo_count": len(DEFAULT_SLOS),
                "alert_count": len(DEFAULT_ALERTS),
                "dashboard_count": len(DEFAULT_DASHBOARDS),
                "retention_policy": DEFAULT_RETENTION_POLICY.__dict__,
                "contract_issues": {
                    "provider_decision_issues": contract["provider_decision_issues"],
                    "metric_issues": contract["metric_issues"],
                    "log_event_issues": contract["log_event_issues"],
                    "trace_span_issues": contract["trace_span_issues"],
                    "slo_issues": contract["slo_issues"],
                    "alert_issues": contract["alert_issues"],
                    "dashboard_issues": contract["dashboard_issues"],
                    "retention_issues": contract["retention_issues"],
                },
            },
            "prd8_implementation_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "live_learner_traffic_authorised": False,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
        }


def default_observability_evidence_controls(ready: bool = True) -> tuple[ObservabilityEvidenceControl, ...]:
    """Return deterministic PRD-7 observability/SRE evidence controls."""

    return tuple(
        ObservabilityEvidenceControl(
            area=area,
            owner_assigned=ready,
            evidence_path_defined=ready,
            runbook_or_drill_defined=ready,
            blocks_live_traffic=True,
        )
        for area in OBSERVABILITY_EVIDENCE_AREAS
    )


def build_observability_sre_readiness_report(
    inputs: ObservabilitySreReadinessInputs,
) -> ObservabilitySreReadinessReport:
    """Build a PRD-7 observability/SRE readiness report."""

    return ObservabilitySreReadinessReport(inputs=inputs)


def build_default_observability_sre_readiness_report() -> ObservabilitySreReadinessReport:
    """Build the accepted default PRD-7.0-7.4 observability/SRE readiness report."""

    return build_observability_sre_readiness_report(
        ObservabilitySreReadinessInputs(
            dashboards_defined=True,
            alerts_defined=True,
            slos_defined=True,
            incident_runbooks_defined=True,
            on_call_ownership_defined=True,
            backup_restore_drill_defined=True,
            rollback_drill_defined=True,
            privacy_escalation_process_defined=True,
            telemetry_pii_redaction_defined=True,
            support_status_comms_defined=True,
            evidence_controls=default_observability_evidence_controls(ready=True),
        )
    )


def build_blocked_observability_sre_readiness_report() -> ObservabilitySreReadinessReport:
    """Build a blocked PRD-7 readiness report for tests and safety checks."""

    return build_observability_sre_readiness_report(ObservabilitySreReadinessInputs())
