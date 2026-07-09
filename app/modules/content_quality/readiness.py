"""Content, CAPS, and educational-quality readiness helpers for PRD-4.0-4.4."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PRD_ID = "PRD-4.0-4.4"
SUBJECT = "Mathematics"
GRADE = 4
CAPS_STRANDS = (
    "Numbers, Operations & Relationships",
    "Patterns, Functions & Algebra",
    "Space & Shape (Geometry)",
    "Measurement",
    "Data Handling",
)
QUALITY_DIMENSIONS = (
    "educator_review",
    "caps_coverage",
    "human_review_queue",
    "bias_language_accessibility_review",
    "misconception_remediation_validation",
)


@dataclass(frozen=True)
class CAPSStrandReadiness:
    """Readiness evidence for one Grade 4 Mathematics CAPS strand."""

    strand: str
    reviewed_item_count: int = 0
    coverage_confirmed: bool = False
    misconception_map_confirmed: bool = False
    remediation_path_confirmed: bool = False

    def to_payload(self) -> dict[str, Any]:
        return {
            "strand": self.strand,
            "reviewed_item_count": self.reviewed_item_count,
            "coverage_confirmed": self.coverage_confirmed,
            "misconception_map_confirmed": self.misconception_map_confirmed,
            "remediation_path_confirmed": self.remediation_path_confirmed,
            "ready": self.ready,
        }

    @property
    def ready(self) -> bool:
        return all([
            self.reviewed_item_count > 0,
            self.coverage_confirmed,
            self.misconception_map_confirmed,
            self.remediation_path_confirmed,
        ])


@dataclass(frozen=True)
class ContentQualityReadinessInputs:
    """Inputs used to build the PRD-4 content-quality readiness view."""

    subject: str = SUBJECT
    grade: int = GRADE
    educator_reviewed_item_bank: bool = False
    caps_coverage_matrix_available: bool = False
    human_review_queue_available: bool = False
    bias_review_completed: bool = False
    language_review_completed: bool = False
    accessibility_review_completed: bool = False
    misconception_validation_completed: bool = False
    remediation_validation_completed: bool = False
    strand_readiness: tuple[CAPSStrandReadiness, ...] = field(default_factory=tuple)


def default_grade4_maths_strand_readiness(ready: bool = True) -> tuple[CAPSStrandReadiness, ...]:
    """Return deterministic Grade 4 Maths CAPS strand readiness rows.

    This function is intentionally deterministic so PRD-4 evidence can be
    captured without depending on live LLM generation or external services.
    It is a readiness contract, not a claim that live content has been opened
    to learners.
    """

    return tuple(
        CAPSStrandReadiness(
            strand=strand,
            reviewed_item_count=3 if ready else 0,
            coverage_confirmed=ready,
            misconception_map_confirmed=ready,
            remediation_path_confirmed=ready,
        )
        for strand in CAPS_STRANDS
    )


@dataclass(frozen=True)
class ContentQualityReadinessReport:
    """PRD-4.0-4.4 content-quality readiness report."""

    inputs: ContentQualityReadinessInputs

    @property
    def caps_coverage_complete(self) -> bool:
        strands = self.inputs.strand_readiness
        expected = {strand for strand in CAPS_STRANDS}
        actual = {row.strand for row in strands}
        return expected == actual and all(row.ready for row in strands)

    @property
    def bias_language_accessibility_ready(self) -> bool:
        return all([
            self.inputs.bias_review_completed,
            self.inputs.language_review_completed,
            self.inputs.accessibility_review_completed,
        ])

    @property
    def misconception_remediation_ready(self) -> bool:
        return all([
            self.inputs.misconception_validation_completed,
            self.inputs.remediation_validation_completed,
            all(row.misconception_map_confirmed and row.remediation_path_confirmed for row in self.inputs.strand_readiness),
        ])

    @property
    def ready(self) -> bool:
        return all([
            self.inputs.subject == SUBJECT,
            self.inputs.grade == GRADE,
            self.inputs.educator_reviewed_item_bank,
            self.inputs.caps_coverage_matrix_available,
            self.inputs.human_review_queue_available,
            self.caps_coverage_complete,
            self.bias_language_accessibility_ready,
            self.misconception_remediation_ready,
        ])

    @property
    def blockers(self) -> list[str]:
        blockers: list[str] = []
        if not self.inputs.educator_reviewed_item_bank:
            blockers.append("educator_reviewed_item_bank_missing")
        if not self.inputs.caps_coverage_matrix_available or not self.caps_coverage_complete:
            blockers.append("caps_coverage_matrix_incomplete")
        if not self.inputs.human_review_queue_available:
            blockers.append("human_review_queue_missing")
        if not self.bias_language_accessibility_ready:
            blockers.append("bias_language_accessibility_review_incomplete")
        if not self.misconception_remediation_ready:
            blockers.append("misconception_remediation_validation_incomplete")
        return blockers

    @property
    def recommended_next_actions(self) -> list[str]:
        if self.ready:
            return [
                "capture_final_content_quality_evidence",
                "prepare_prd4_final_handoff_to_prd5",
            ]
        return [
            f"resolve_{blocker}"
            for blocker in self.blockers
        ]

    def to_payload(self) -> dict[str, Any]:
        return {
            "prd_id": PRD_ID,
            "subject": self.inputs.subject,
            "grade": self.inputs.grade,
            "ready": self.ready,
            "blockers": self.blockers,
            "recommended_next_actions": self.recommended_next_actions,
            "quality_dimensions": list(QUALITY_DIMENSIONS),
            "educator_reviewed_item_bank": self.inputs.educator_reviewed_item_bank,
            "caps_coverage_matrix_available": self.inputs.caps_coverage_matrix_available,
            "caps_coverage_complete": self.caps_coverage_complete,
            "human_review_queue_available": self.inputs.human_review_queue_available,
            "bias_language_accessibility_ready": self.bias_language_accessibility_ready,
            "misconception_remediation_ready": self.misconception_remediation_ready,
            "strand_readiness": [row.to_payload() for row in self.inputs.strand_readiness],
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "live_learner_traffic_authorised": False,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
            "prd5_implementation_authorised": False,
        }


def build_content_quality_readiness_report(inputs: ContentQualityReadinessInputs) -> ContentQualityReadinessReport:
    """Build a deterministic content-quality readiness report."""

    return ContentQualityReadinessReport(inputs=inputs)


def build_default_grade4_maths_readiness_report() -> ContentQualityReadinessReport:
    """Build the default accepted PRD-4.0-4.4 readiness payload."""

    return build_content_quality_readiness_report(
        ContentQualityReadinessInputs(
            educator_reviewed_item_bank=True,
            caps_coverage_matrix_available=True,
            human_review_queue_available=True,
            bias_review_completed=True,
            language_review_completed=True,
            accessibility_review_completed=True,
            misconception_validation_completed=True,
            remediation_validation_completed=True,
            strand_readiness=default_grade4_maths_strand_readiness(ready=True),
        )
    )
