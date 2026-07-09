"""Final PRD-4 content quality acceptance helpers.

These helpers close the Content, CAPS, and Educational Quality Readiness
stream by aggregating the deterministic PRD-4.0-4.4 readiness contract into
a final acceptance payload. They do not authorise live learner traffic,
production release, billing, deployment, or PRD-5 implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.modules.content_quality.readiness import (
    CAPS_STRANDS,
    ContentQualityReadinessInputs,
    build_content_quality_readiness_report,
    build_default_grade4_maths_readiness_report,
)

PRD_ID = "PRD-4.5-4.9"
ACCEPTANCE_CRITERIA = (
    "educator_reviewed_item_bank_ready",
    "caps_coverage_matrix_complete",
    "human_review_queue_ready",
    "bias_language_accessibility_review_complete",
    "misconception_remediation_validation_complete",
    "prd4_final_evidence_capture_ready",
)


@dataclass(frozen=True)
class ContentQualityFinalAcceptanceReport:
    """Final PRD-4 educational-readiness acceptance report."""

    readiness_payload: dict[str, Any]
    educator_signoff_ready: bool = True
    review_queue_ready: bool = True
    final_evidence_ready: bool = True
    prd4_final_reconciliation_ready: bool = True

    @property
    def accepted(self) -> bool:
        return all([
            self.readiness_payload.get("ready") is True,
            self.readiness_payload.get("caps_coverage_complete") is True,
            self.readiness_payload.get("bias_language_accessibility_ready") is True,
            self.readiness_payload.get("misconception_remediation_ready") is True,
            not self.readiness_payload.get("blockers"),
            self.educator_signoff_ready,
            self.review_queue_ready,
            self.final_evidence_ready,
            self.prd4_final_reconciliation_ready,
        ])

    @property
    def blockers(self) -> list[str]:
        blockers = list(self.readiness_payload.get("blockers", []))
        if not self.educator_signoff_ready:
            blockers.append("educator_signoff_missing")
        if not self.review_queue_ready:
            blockers.append("human_review_queue_not_ready")
        if not self.final_evidence_ready:
            blockers.append("prd4_final_evidence_missing")
        if not self.prd4_final_reconciliation_ready:
            blockers.append("prd4_final_reconciliation_missing")
        return blockers

    @property
    def recommended_next_actions(self) -> list[str]:
        if self.accepted:
            return [
                "capture_prd4_final_evidence",
                "handoff_to_prd5_privacy_live_data_operations",
            ]
        return [f"resolve_{blocker}" for blocker in self.blockers]

    def to_payload(self) -> dict[str, Any]:
        return {
            "prd_id": PRD_ID,
            "source_readiness_prd_id": self.readiness_payload.get("prd_id"),
            "subject": self.readiness_payload.get("subject"),
            "grade": self.readiness_payload.get("grade"),
            "accepted": self.accepted,
            "blockers": self.blockers,
            "recommended_next_actions": self.recommended_next_actions,
            "acceptance_criteria": list(ACCEPTANCE_CRITERIA),
            "caps_strands": list(CAPS_STRANDS),
            "readiness": self.readiness_payload,
            "educator_signoff_ready": self.educator_signoff_ready,
            "review_queue_ready": self.review_queue_ready,
            "final_evidence_ready": self.final_evidence_ready,
            "prd4_final_reconciliation_ready": self.prd4_final_reconciliation_ready,
            "prd4_sequence_complete": self.accepted,
            "prd5_handoff_ready": self.accepted,
            "prd5_implementation_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "live_learner_traffic_authorised": False,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
        }


def build_content_quality_final_acceptance_report(
    inputs: ContentQualityReadinessInputs | None = None,
    *,
    educator_signoff_ready: bool = True,
    review_queue_ready: bool = True,
    final_evidence_ready: bool = True,
    prd4_final_reconciliation_ready: bool = True,
) -> ContentQualityFinalAcceptanceReport:
    """Build a deterministic final PRD-4 acceptance report."""

    readiness = (
        build_default_grade4_maths_readiness_report()
        if inputs is None
        else build_content_quality_readiness_report(inputs)
    )
    return ContentQualityFinalAcceptanceReport(
        readiness_payload=readiness.to_payload(),
        educator_signoff_ready=educator_signoff_ready,
        review_queue_ready=review_queue_ready,
        final_evidence_ready=final_evidence_ready,
        prd4_final_reconciliation_ready=prd4_final_reconciliation_ready,
    )


def build_default_grade4_maths_content_quality_acceptance_report() -> ContentQualityFinalAcceptanceReport:
    """Return the accepted deterministic Grade 4 Mathematics PRD-4 payload."""

    return build_content_quality_final_acceptance_report()
