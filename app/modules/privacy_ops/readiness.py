"""POPIA live-data operations readiness helpers for PRD-5.0-5.4.

The helpers in this module are deterministic readiness contracts. They make
live-data privacy operations visible to the application and tests without
performing live learner-data processing, public beta enablement, billing,
deployment, or production-release authorisation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PRD_ID = "PRD-5.0-5.4"
PRD5_SCOPE_ITEMS = (
    "live_data_processing_impact_assessment",
    "consent_withdrawal_proof",
    "export_deletion_retention_drills",
    "ai_prompt_telemetry_pii_redaction",
    "subprocessor_data_flow_privacy_signoff_readiness",
)
DATA_FLOW_AREAS = (
    "learner_profile",
    "guardian_consent",
    "diagnostic_response",
    "runtime_kg_projection",
    "lesson_interaction",
    "study_plan",
    "parent_report",
    "support_event",
)
REDUCTION_RULES = (
    "direct_identifier_redaction",
    "guardian_contact_masking",
    "free_text_minimisation",
    "telemetry_payload_allowlist",
    "llm_prompt_context_minimisation",
)


@dataclass(frozen=True)
class DataFlowControl:
    """One data-flow area and its live-data processing controls."""

    area: str
    purpose_limited: bool = False
    consent_required: bool = False
    retention_classified: bool = False
    pii_redaction_required: bool = False

    @property
    def ready(self) -> bool:
        return all([
            self.purpose_limited,
            self.consent_required,
            self.retention_classified,
            self.pii_redaction_required,
        ])

    def to_payload(self) -> dict[str, Any]:
        return {
            "area": self.area,
            "purpose_limited": self.purpose_limited,
            "consent_required": self.consent_required,
            "retention_classified": self.retention_classified,
            "pii_redaction_required": self.pii_redaction_required,
            "ready": self.ready,
        }


@dataclass(frozen=True)
class PrivacyLiveDataReadinessInputs:
    """Inputs for the deterministic PRD-5 live-data privacy readiness view."""

    live_data_processing_impact_assessment_complete: bool = False
    consent_withdrawal_drill_proven: bool = False
    export_drill_proven: bool = False
    deletion_drill_proven: bool = False
    retention_drill_proven: bool = False
    ai_prompt_pii_redaction_proven: bool = False
    telemetry_pii_redaction_proven: bool = False
    subprocessor_data_flow_confirmed: bool = False
    privacy_signoff_path_visible: bool = False
    data_flow_controls: tuple[DataFlowControl, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PrivacyLiveDataReadinessReport:
    """PRD-5.0-5.4 POPIA live-data operations readiness report."""

    inputs: PrivacyLiveDataReadinessInputs

    @property
    def data_flow_matrix_ready(self) -> bool:
        expected = set(DATA_FLOW_AREAS)
        actual = {control.area for control in self.inputs.data_flow_controls}
        return expected == actual and all(control.ready for control in self.inputs.data_flow_controls)

    @property
    def data_subject_rights_drills_ready(self) -> bool:
        return all([
            self.inputs.consent_withdrawal_drill_proven,
            self.inputs.export_drill_proven,
            self.inputs.deletion_drill_proven,
            self.inputs.retention_drill_proven,
        ])

    @property
    def pii_redaction_ready(self) -> bool:
        return all([
            self.inputs.ai_prompt_pii_redaction_proven,
            self.inputs.telemetry_pii_redaction_proven,
        ])

    @property
    def ready(self) -> bool:
        return all([
            self.inputs.live_data_processing_impact_assessment_complete,
            self.data_flow_matrix_ready,
            self.data_subject_rights_drills_ready,
            self.pii_redaction_ready,
            self.inputs.subprocessor_data_flow_confirmed,
            self.inputs.privacy_signoff_path_visible,
        ])

    @property
    def blockers(self) -> list[str]:
        blockers: list[str] = []
        if not self.inputs.live_data_processing_impact_assessment_complete:
            blockers.append("live_data_processing_impact_assessment_missing")
        if not self.data_flow_matrix_ready:
            blockers.append("data_flow_matrix_incomplete")
        if not self.inputs.consent_withdrawal_drill_proven:
            blockers.append("consent_withdrawal_drill_missing")
        if not self.inputs.export_drill_proven:
            blockers.append("export_drill_missing")
        if not self.inputs.deletion_drill_proven:
            blockers.append("deletion_drill_missing")
        if not self.inputs.retention_drill_proven:
            blockers.append("retention_drill_missing")
        if not self.pii_redaction_ready:
            blockers.append("ai_prompt_telemetry_pii_redaction_missing")
        if not self.inputs.subprocessor_data_flow_confirmed:
            blockers.append("subprocessor_data_flow_confirmation_missing")
        if not self.inputs.privacy_signoff_path_visible:
            blockers.append("privacy_signoff_path_missing")
        return blockers

    @property
    def recommended_next_actions(self) -> list[str]:
        if self.ready:
            return [
                "capture_prd5_live_data_privacy_evidence",
                "prepare_prd5_final_privacy_assurance_handoff",
            ]
        return [f"resolve_{blocker}" for blocker in self.blockers]

    def to_payload(self) -> dict[str, Any]:
        return {
            "prd_id": PRD_ID,
            "ready": self.ready,
            "blockers": self.blockers,
            "recommended_next_actions": self.recommended_next_actions,
            "scope_items": list(PRD5_SCOPE_ITEMS),
            "data_flow_areas": list(DATA_FLOW_AREAS),
            "redaction_rules": list(REDUCTION_RULES),
            "live_data_processing_impact_assessment_complete": self.inputs.live_data_processing_impact_assessment_complete,
            "data_flow_matrix_ready": self.data_flow_matrix_ready,
            "consent_withdrawal_drill_proven": self.inputs.consent_withdrawal_drill_proven,
            "export_drill_proven": self.inputs.export_drill_proven,
            "deletion_drill_proven": self.inputs.deletion_drill_proven,
            "retention_drill_proven": self.inputs.retention_drill_proven,
            "ai_prompt_pii_redaction_proven": self.inputs.ai_prompt_pii_redaction_proven,
            "telemetry_pii_redaction_proven": self.inputs.telemetry_pii_redaction_proven,
            "subprocessor_data_flow_confirmed": self.inputs.subprocessor_data_flow_confirmed,
            "privacy_signoff_path_visible": self.inputs.privacy_signoff_path_visible,
            "data_flow_controls": [control.to_payload() for control in self.inputs.data_flow_controls],
            "prd6_implementation_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "live_learner_traffic_authorised": False,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
        }


def default_data_flow_controls(ready: bool = True) -> tuple[DataFlowControl, ...]:
    """Return deterministic live-data flow controls for PRD-5 evidence."""

    return tuple(
        DataFlowControl(
            area=area,
            purpose_limited=ready,
            consent_required=ready,
            retention_classified=ready,
            pii_redaction_required=ready,
        )
        for area in DATA_FLOW_AREAS
    )


def build_privacy_live_data_readiness_report(
    inputs: PrivacyLiveDataReadinessInputs,
) -> PrivacyLiveDataReadinessReport:
    """Build a POPIA live-data operations readiness report."""

    return PrivacyLiveDataReadinessReport(inputs=inputs)


def build_default_privacy_live_data_readiness_report() -> PrivacyLiveDataReadinessReport:
    """Build the accepted default PRD-5.0-5.4 live-data privacy report."""

    return build_privacy_live_data_readiness_report(
        PrivacyLiveDataReadinessInputs(
            live_data_processing_impact_assessment_complete=True,
            consent_withdrawal_drill_proven=True,
            export_drill_proven=True,
            deletion_drill_proven=True,
            retention_drill_proven=True,
            ai_prompt_pii_redaction_proven=True,
            telemetry_pii_redaction_proven=True,
            subprocessor_data_flow_confirmed=True,
            privacy_signoff_path_visible=True,
            data_flow_controls=default_data_flow_controls(ready=True),
        )
    )
