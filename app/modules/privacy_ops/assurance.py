"""Final POPIA privacy assurance helpers for PRD-5.5-5.9.

The helpers here close the PRD-5 privacy assurance stream by combining the
PRD-5.0-5.4 live-data readiness contract with a traceable audit-crosswalk.
They do not authorise PRD-6 implementation, live learner traffic, billing,
deployment, release tags, public beta, or production release.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.modules.privacy_ops.readiness import (
    PrivacyLiveDataReadinessInputs,
    PrivacyLiveDataReadinessReport,
    build_default_privacy_live_data_readiness_report,
    build_privacy_live_data_readiness_report,
)

PRD_ID = "PRD-5.5-5.9"
SOURCE_READINESS_PRD_ID = "PRD-5.0-5.4"
AUDIT_REPORT_ID = "EduBoost Codebase Audit 2026-07-09"
FINAL_ASSURANCE_CRITERIA = (
    "live_data_processing_impact_assessment_accepted",
    "consent_withdrawal_export_deletion_retention_drills_accepted",
    "ai_prompt_and_telemetry_pii_redaction_accepted",
    "subprocessor_data_flow_and_privacy_signoff_accepted",
    "audit_2026_07_09_crosswalk_reconciled",
)


@dataclass(frozen=True)
class AuditCrosswalkItem:
    """One audit concern mapped into the existing PRD ladder."""

    concern: str
    disposition: str
    owning_prd: str
    blocks_live_traffic: bool = False
    blocks_production_release: bool = False

    @property
    def reconciled(self) -> bool:
        return bool(self.concern and self.disposition and self.owning_prd)

    def to_payload(self) -> dict[str, Any]:
        return {
            "concern": self.concern,
            "disposition": self.disposition,
            "owning_prd": self.owning_prd,
            "blocks_live_traffic": self.blocks_live_traffic,
            "blocks_production_release": self.blocks_production_release,
            "reconciled": self.reconciled,
        }


@dataclass(frozen=True)
class PrivacyFinalAssuranceInputs:
    """Inputs for the deterministic PRD-5 final assurance view."""

    readiness_report: PrivacyLiveDataReadinessReport
    audit_crosswalk: tuple[AuditCrosswalkItem, ...] = field(default_factory=tuple)
    privacy_signoff_recorded: bool = False
    prd5_final_reconciliation_recorded: bool = False


@dataclass(frozen=True)
class PrivacyFinalAssuranceReport:
    """Final POPIA live-data privacy assurance report for PRD-5.5-5.9."""

    inputs: PrivacyFinalAssuranceInputs

    @property
    def audit_crosswalk_reconciled(self) -> bool:
        expected = {
            "runtime_kg_persistence_temporal_evidence",
            "popia_data_subject_rights",
            "content_caps_quality",
            "ci_dependency_hygiene",
            "security_external_review",
            "observability_incident_privacy_escalation",
            "performance_scale_cost",
        }
        actual = {item.concern for item in self.inputs.audit_crosswalk}
        return expected.issubset(actual) and all(item.reconciled for item in self.inputs.audit_crosswalk)

    @property
    def data_subject_rights_ready(self) -> bool:
        payload = self.inputs.readiness_report.to_payload()
        return all([
            payload.get("consent_withdrawal_drill_proven") is True,
            payload.get("export_drill_proven") is True,
            payload.get("deletion_drill_proven") is True,
            payload.get("retention_drill_proven") is True,
        ])

    @property
    def redaction_ready(self) -> bool:
        payload = self.inputs.readiness_report.to_payload()
        return all([
            payload.get("ai_prompt_pii_redaction_proven") is True,
            payload.get("telemetry_pii_redaction_proven") is True,
        ])

    @property
    def accepted(self) -> bool:
        return all([
            self.inputs.readiness_report.ready,
            self.data_subject_rights_ready,
            self.redaction_ready,
            self.inputs.privacy_signoff_recorded,
            self.inputs.prd5_final_reconciliation_recorded,
            self.audit_crosswalk_reconciled,
        ])

    @property
    def blockers(self) -> list[str]:
        blockers: list[str] = []
        if not self.inputs.readiness_report.ready:
            blockers.append("prd5_live_data_readiness_incomplete")
            blockers.extend(self.inputs.readiness_report.blockers)
        if not self.data_subject_rights_ready:
            blockers.append("data_subject_rights_drills_incomplete")
        if not self.redaction_ready:
            blockers.append("ai_prompt_telemetry_redaction_incomplete")
        if not self.inputs.privacy_signoff_recorded:
            blockers.append("privacy_signoff_not_recorded")
        if not self.inputs.prd5_final_reconciliation_recorded:
            blockers.append("prd5_final_reconciliation_not_recorded")
        if not self.audit_crosswalk_reconciled:
            blockers.append("audit_2026_07_09_crosswalk_not_reconciled")
        return list(dict.fromkeys(blockers))

    @property
    def recommended_next_actions(self) -> list[str]:
        if self.accepted:
            return [
                "capture_prd5_final_privacy_assurance_evidence",
                "handoff_to_prd6_security_assurance_external_review",
            ]
        return [f"resolve_{blocker}" for blocker in self.blockers]

    def to_payload(self) -> dict[str, Any]:
        readiness_payload = self.inputs.readiness_report.to_payload()
        return {
            "prd_id": PRD_ID,
            "source_readiness_prd_id": SOURCE_READINESS_PRD_ID,
            "audit_report_id": AUDIT_REPORT_ID,
            "accepted": self.accepted,
            "blockers": self.blockers,
            "recommended_next_actions": self.recommended_next_actions,
            "acceptance_criteria": list(FINAL_ASSURANCE_CRITERIA),
            "privacy_live_data_readiness": readiness_payload,
            "live_data_processing_impact_assessment_accepted": readiness_payload.get("live_data_processing_impact_assessment_complete") is True,
            "data_subject_rights_drills_accepted": self.data_subject_rights_ready,
            "ai_prompt_telemetry_pii_redaction_accepted": self.redaction_ready,
            "subprocessor_data_flow_confirmed": readiness_payload.get("subprocessor_data_flow_confirmed") is True,
            "privacy_signoff_recorded": self.inputs.privacy_signoff_recorded,
            "prd5_final_reconciliation_recorded": self.inputs.prd5_final_reconciliation_recorded,
            "audit_2026_07_09_crosswalk_reconciled": self.audit_crosswalk_reconciled,
            "audit_crosswalk": [item.to_payload() for item in self.inputs.audit_crosswalk],
            "prd5_sequence_complete": self.accepted,
            "prd6_handoff_ready": self.accepted,
            "prd6_implementation_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "live_learner_traffic_authorised": False,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
        }


def default_audit_crosswalk_items() -> tuple[AuditCrosswalkItem, ...]:
    """Return the audit crosswalk mapped into the existing PRD ladder."""

    return (
        AuditCrosswalkItem(
            concern="runtime_kg_persistence_temporal_evidence",
            disposition="closed_by_prd2_with_follow_up_evidence_visible_to_later_assurance",
            owning_prd="PRD-2",
            blocks_live_traffic=True,
            blocks_production_release=True,
        ),
        AuditCrosswalkItem(
            concern="popia_data_subject_rights",
            disposition="closed_by_prd5_live_data_privacy_assurance",
            owning_prd="PRD-5",
            blocks_live_traffic=True,
            blocks_production_release=True,
        ),
        AuditCrosswalkItem(
            concern="content_caps_quality",
            disposition="closed_by_prd4_content_quality_readiness",
            owning_prd="PRD-4",
            blocks_live_traffic=True,
            blocks_production_release=True,
        ),
        AuditCrosswalkItem(
            concern="ci_dependency_hygiene",
            disposition="prd1_closed_with_remaining_security_dependency_scans_deferred_to_prd6",
            owning_prd="PRD-1/PRD-6",
            blocks_live_traffic=True,
            blocks_production_release=True,
        ),
        AuditCrosswalkItem(
            concern="security_external_review",
            disposition="scheduled_for_prd6_security_assurance_external_review",
            owning_prd="PRD-6",
            blocks_live_traffic=True,
            blocks_production_release=True,
        ),
        AuditCrosswalkItem(
            concern="observability_incident_privacy_escalation",
            disposition="scheduled_for_prd7_observability_sre_incident_readiness",
            owning_prd="PRD-7",
            blocks_live_traffic=True,
            blocks_production_release=True,
        ),
        AuditCrosswalkItem(
            concern="performance_scale_cost",
            disposition="scheduled_for_prd8_performance_scale_cost_execution",
            owning_prd="PRD-8",
            blocks_live_traffic=False,
            blocks_production_release=True,
        ),
    )


def build_privacy_final_assurance_report(
    inputs: PrivacyFinalAssuranceInputs,
) -> PrivacyFinalAssuranceReport:
    """Build a final POPIA privacy assurance report."""

    return PrivacyFinalAssuranceReport(inputs=inputs)


def build_default_privacy_final_assurance_report() -> PrivacyFinalAssuranceReport:
    """Build the accepted default PRD-5.5-5.9 privacy assurance report."""

    return build_privacy_final_assurance_report(
        PrivacyFinalAssuranceInputs(
            readiness_report=build_default_privacy_live_data_readiness_report(),
            audit_crosswalk=default_audit_crosswalk_items(),
            privacy_signoff_recorded=True,
            prd5_final_reconciliation_recorded=True,
        )
    )


def build_blocked_privacy_final_assurance_report() -> PrivacyFinalAssuranceReport:
    """Build a blocked PRD-5 final assurance report for tests and safety checks."""

    return build_privacy_final_assurance_report(
        PrivacyFinalAssuranceInputs(
            readiness_report=build_privacy_live_data_readiness_report(PrivacyLiveDataReadinessInputs()),
            audit_crosswalk=(),
            privacy_signoff_recorded=False,
            prd5_final_reconciliation_recorded=False,
        )
    )
