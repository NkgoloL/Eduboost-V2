"""Vertical learner/parent journey contract for PRD-3.0-3.4.

This module is intentionally dependency-light. It turns the existing product
capabilities — onboarding, consent, diagnostics, runtime KG gap profile,
lessons, assessments, mastery, study plans, gamification, parent reporting,
and POPIA rights controls — into one deterministic journey snapshot.

The service does not authorise public beta or live learner traffic. It only
exposes product-state metadata so routes and tests can prove whether the
learner/parent vertical journey is complete enough to harden in PRD-3.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

PRD3_VERTICAL_JOURNEY_MILESTONES: tuple[str, ...] = (
    "learner_profile_created",
    "guardian_consent_active",
    "learner_onboarding_completed",
    "diagnostic_completed",
    "runtime_kg_gap_profile_available",
    "lesson_generated",
    "lesson_completed",
    "assessment_attempted",
    "mastery_updated",
    "study_plan_generated",
    "gamification_profile_available",
    "parent_progress_report_available",
    "popia_export_path_available",
    "popia_erasure_path_available",
)

_MILESTONE_LABELS: dict[str, str] = {
    "learner_profile_created": "Learner profile created",
    "guardian_consent_active": "Guardian consent active",
    "learner_onboarding_completed": "Learner onboarding completed",
    "diagnostic_completed": "Diagnostic completed",
    "runtime_kg_gap_profile_available": "Runtime KG gap profile available",
    "lesson_generated": "Lesson generated",
    "lesson_completed": "Lesson completed",
    "assessment_attempted": "Assessment attempted",
    "mastery_updated": "Mastery updated",
    "study_plan_generated": "Study plan generated",
    "gamification_profile_available": "Gamification profile available",
    "parent_progress_report_available": "Parent progress/report view available",
    "popia_export_path_available": "POPIA export path available",
    "popia_erasure_path_available": "POPIA erasure path available",
}


@dataclass(frozen=True)
class VerticalJourneyInputs:
    """Raw state used to compute learner/parent journey progress."""

    learner_id: str
    guardian_id: str | None = None
    learner_profile_created: bool = False
    guardian_consent_active: bool = False
    learner_onboarding_completed: bool = False
    diagnostic_completed: bool = False
    runtime_kg_gap_profile_available: bool = False
    lesson_generated: bool = False
    lesson_completed: bool = False
    assessment_attempted: bool = False
    mastery_updated: bool = False
    study_plan_generated: bool = False
    gamification_profile_available: bool = False
    parent_progress_report_available: bool = False
    popia_export_path_available: bool = False
    popia_erasure_path_available: bool = False
    counts: dict[str, int] | None = None


@dataclass(frozen=True)
class VerticalJourneyMilestone:
    """One milestone in the learner/parent journey."""

    key: str
    label: str
    complete: bool
    blocked_by: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["blocked_by"] = list(self.blocked_by)
        return payload


@dataclass(frozen=True)
class VerticalJourneySnapshot:
    """Serializable PRD-3 journey state."""

    learner_id: str
    guardian_id: str | None
    milestones: tuple[VerticalJourneyMilestone, ...]
    completion_ratio: float
    current_milestone: str | None
    blocked_reasons: tuple[str, ...]
    counts: dict[str, int]
    contract_version: str = "prd3.0-3.4/vertical-journey/v1"
    prd_id: str = "PRD-3.0-3.4"
    prd4_implementation_authorised: bool = False
    live_learner_traffic_authorised: bool = False

    @property
    def complete(self) -> bool:
        return all(milestone.complete for milestone in self.milestones)

    def to_payload(self) -> dict[str, Any]:
        return {
            "prd_id": self.prd_id,
            "contract_version": self.contract_version,
            "learner_id": self.learner_id,
            "guardian_id": self.guardian_id,
            "complete": self.complete,
            "completion_ratio": self.completion_ratio,
            "current_milestone": self.current_milestone,
            "blocked_reasons": list(self.blocked_reasons),
            "counts": dict(self.counts),
            "milestones": [milestone.to_payload() for milestone in self.milestones],
            "prd4_implementation_authorised": self.prd4_implementation_authorised,
            "live_learner_traffic_authorised": self.live_learner_traffic_authorised,
        }


def _blocks_for(key: str, inputs: VerticalJourneyInputs) -> tuple[str, ...]:
    blockers: list[str] = []
    if key != "learner_profile_created" and not inputs.learner_profile_created:
        blockers.append("learner_profile_missing")
    consent_gated = {
        "diagnostic_completed",
        "runtime_kg_gap_profile_available",
        "lesson_generated",
        "lesson_completed",
        "assessment_attempted",
        "mastery_updated",
        "study_plan_generated",
        "gamification_profile_available",
        "parent_progress_report_available",
        "popia_export_path_available",
        "popia_erasure_path_available",
    }
    if key in consent_gated and not inputs.guardian_consent_active:
        blockers.append("guardian_consent_inactive")
    if key in {"runtime_kg_gap_profile_available", "lesson_generated", "study_plan_generated"} and not inputs.diagnostic_completed:
        blockers.append("diagnostic_not_completed")
    if key in {"lesson_completed", "assessment_attempted", "mastery_updated"} and not inputs.lesson_generated:
        blockers.append("lesson_not_generated")
    if key == "parent_progress_report_available" and not inputs.guardian_id:
        blockers.append("guardian_context_missing")
    return tuple(blockers)


def build_vertical_journey_snapshot(inputs: VerticalJourneyInputs) -> VerticalJourneySnapshot:
    """Build a deterministic learner/parent vertical journey snapshot."""

    raw = asdict(inputs)
    milestones: list[VerticalJourneyMilestone] = []
    blocked: list[str] = []
    for key in PRD3_VERTICAL_JOURNEY_MILESTONES:
        complete = bool(raw.get(key))
        blockers = () if complete else _blocks_for(key, inputs)
        blocked.extend(blockers)
        milestones.append(
            VerticalJourneyMilestone(
                key=key,
                label=_MILESTONE_LABELS[key],
                complete=complete,
                blocked_by=blockers,
            )
        )
    completed = sum(1 for milestone in milestones if milestone.complete)
    current = next((milestone.key for milestone in milestones if not milestone.complete), None)
    return VerticalJourneySnapshot(
        learner_id=inputs.learner_id,
        guardian_id=inputs.guardian_id,
        milestones=tuple(milestones),
        completion_ratio=round(completed / len(milestones), 3),
        current_milestone=current,
        blocked_reasons=tuple(sorted(set(blocked))),
        counts=dict(inputs.counts or {}),
    )
