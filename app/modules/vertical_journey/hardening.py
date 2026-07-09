"""Final PRD-3 learner/parent vertical journey hardening helpers.

The helper turns the PRD-3.0-3.4 journey snapshot into a compact acceptance
payload that routes and evidence capture can use to prove the vertical learner
and parent journey is hardened without authorising live learner traffic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.modules.vertical_journey.service import PRD3_VERTICAL_JOURNEY_MILESTONES, VerticalJourneySnapshot

PRD3_FINAL_HARDENING_ID = "PRD-3.5-3.9"
PRD3_FINAL_REQUIRED_MILESTONES: tuple[str, ...] = PRD3_VERTICAL_JOURNEY_MILESTONES

_ACTION_LABELS: dict[str, str] = {
    "learner_profile_created": "Create learner profile",
    "guardian_consent_active": "Capture active guardian consent",
    "learner_onboarding_completed": "Complete learner onboarding",
    "diagnostic_completed": "Complete diagnostic assessment",
    "runtime_kg_gap_profile_available": "Build learner KG gap profile",
    "lesson_generated": "Generate a personalised lesson",
    "lesson_completed": "Complete a lesson",
    "assessment_attempted": "Attempt an assessment",
    "mastery_updated": "Persist mastery update",
    "study_plan_generated": "Generate a study plan",
    "gamification_profile_available": "Expose gamification profile",
    "parent_progress_report_available": "Expose parent progress/report view",
    "popia_export_path_available": "Expose POPIA export path",
    "popia_erasure_path_available": "Expose POPIA erasure path",
}


@dataclass(frozen=True)
class VerticalJourneyHardeningReport:
    """Final PRD-3 acceptance state for one learner/guardian journey."""

    learner_id: str
    guardian_id: str | None
    accepted: bool
    completion_ratio: float
    incomplete_milestones: tuple[str, ...]
    blockers: tuple[str, ...]
    recommended_next_actions: tuple[str, ...]
    consent_gate_clear: bool
    runtime_kg_gap_profile_visible: bool
    parent_report_visible: bool
    popia_export_visible: bool
    popia_erasure_visible: bool
    prd_id: str = PRD3_FINAL_HARDENING_ID
    contract_version: str = "prd3.5-3.9/vertical-journey-hardening/v1"
    prd4_handoff_authorised: bool = False
    prd4_implementation_authorised: bool = False
    live_learner_traffic_authorised: bool = False
    production_release_authorised: bool = False

    def to_payload(self) -> dict[str, Any]:
        return {
            "prd_id": self.prd_id,
            "contract_version": self.contract_version,
            "learner_id": self.learner_id,
            "guardian_id": self.guardian_id,
            "accepted": self.accepted,
            "completion_ratio": self.completion_ratio,
            "incomplete_milestones": list(self.incomplete_milestones),
            "blockers": list(self.blockers),
            "recommended_next_actions": list(self.recommended_next_actions),
            "consent_gate_clear": self.consent_gate_clear,
            "runtime_kg_gap_profile_visible": self.runtime_kg_gap_profile_visible,
            "parent_report_visible": self.parent_report_visible,
            "popia_export_visible": self.popia_export_visible,
            "popia_erasure_visible": self.popia_erasure_visible,
            "prd4_handoff_authorised": self.prd4_handoff_authorised,
            "prd4_implementation_authorised": self.prd4_implementation_authorised,
            "live_learner_traffic_authorised": self.live_learner_traffic_authorised,
            "production_release_authorised": self.production_release_authorised,
        }


def build_vertical_journey_hardening_report(
    snapshot: VerticalJourneySnapshot,
) -> VerticalJourneyHardeningReport:
    """Build a deterministic final-hardening report from a journey snapshot."""

    milestone_payloads = {milestone.key: milestone for milestone in snapshot.milestones}
    incomplete = tuple(
        key for key in PRD3_FINAL_REQUIRED_MILESTONES if key in milestone_payloads and not milestone_payloads[key].complete
    )
    blockers = tuple(sorted(set(snapshot.blocked_reasons)))
    next_actions = tuple(_ACTION_LABELS.get(key, key) for key in incomplete[:5])
    consent_gate_clear = bool(milestone_payloads.get("guardian_consent_active") and milestone_payloads["guardian_consent_active"].complete)
    runtime_kg_visible = bool(
        milestone_payloads.get("runtime_kg_gap_profile_available")
        and milestone_payloads["runtime_kg_gap_profile_available"].complete
    )
    parent_report_visible = bool(
        milestone_payloads.get("parent_progress_report_available")
        and milestone_payloads["parent_progress_report_available"].complete
    )
    popia_export_visible = bool(
        milestone_payloads.get("popia_export_path_available")
        and milestone_payloads["popia_export_path_available"].complete
    )
    popia_erasure_visible = bool(
        milestone_payloads.get("popia_erasure_path_available")
        and milestone_payloads["popia_erasure_path_available"].complete
    )
    accepted = all(
        [
            snapshot.complete,
            consent_gate_clear,
            runtime_kg_visible,
            parent_report_visible,
            popia_export_visible,
            popia_erasure_visible,
            not blockers,
        ]
    )
    return VerticalJourneyHardeningReport(
        learner_id=snapshot.learner_id,
        guardian_id=snapshot.guardian_id,
        accepted=accepted,
        completion_ratio=snapshot.completion_ratio,
        incomplete_milestones=incomplete,
        blockers=blockers,
        recommended_next_actions=next_actions,
        consent_gate_clear=consent_gate_clear,
        runtime_kg_gap_profile_visible=runtime_kg_visible,
        parent_report_visible=parent_report_visible,
        popia_export_visible=popia_export_visible,
        popia_erasure_visible=popia_erasure_visible,
    )
