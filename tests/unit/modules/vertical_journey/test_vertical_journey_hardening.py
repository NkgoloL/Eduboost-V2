from app.modules.vertical_journey.hardening import build_vertical_journey_hardening_report
from app.modules.vertical_journey.service import VerticalJourneyInputs, build_vertical_journey_snapshot


def _complete_snapshot():
    return build_vertical_journey_snapshot(
        VerticalJourneyInputs(
            learner_id="learner-complete",
            guardian_id="guardian-1",
            learner_profile_created=True,
            guardian_consent_active=True,
            learner_onboarding_completed=True,
            diagnostic_completed=True,
            runtime_kg_gap_profile_available=True,
            lesson_generated=True,
            lesson_completed=True,
            assessment_attempted=True,
            mastery_updated=True,
            study_plan_generated=True,
            gamification_profile_available=True,
            parent_progress_report_available=True,
            popia_export_path_available=True,
            popia_erasure_path_available=True,
        )
    )


def test_final_hardening_accepts_complete_vertical_journey_without_live_traffic():
    report = build_vertical_journey_hardening_report(_complete_snapshot()).to_payload()

    assert report["prd_id"] == "PRD-3.5-3.9"
    assert report["accepted"] is True
    assert report["incomplete_milestones"] == []
    assert report["consent_gate_clear"] is True
    assert report["runtime_kg_gap_profile_visible"] is True
    assert report["parent_report_visible"] is True
    assert report["popia_export_visible"] is True
    assert report["popia_erasure_visible"] is True
    assert report["prd4_handoff_authorised"] is False
    assert report["prd4_implementation_authorised"] is False
    assert report["live_learner_traffic_authorised"] is False
    assert report["production_release_authorised"] is False


def test_final_hardening_preserves_consent_blocker_and_next_actions():
    snapshot = build_vertical_journey_snapshot(
        VerticalJourneyInputs(
            learner_id="learner-blocked",
            guardian_id="guardian-1",
            learner_profile_created=True,
            guardian_consent_active=False,
        )
    )
    report = build_vertical_journey_hardening_report(snapshot).to_payload()

    assert report["accepted"] is False
    assert "guardian_consent_inactive" in report["blockers"]
    assert "diagnostic_completed" in report["incomplete_milestones"]
    assert report["recommended_next_actions"]
    assert report["consent_gate_clear"] is False


def test_final_hardening_partial_visibility_flags():
    # Snapshot missing POPIA export and erasure
    snapshot = build_vertical_journey_snapshot(
        VerticalJourneyInputs(
            learner_id="learner-partial",
            guardian_id="guardian-1",
            learner_profile_created=True,
            guardian_consent_active=True,
            learner_onboarding_completed=True,
            diagnostic_completed=True,
            runtime_kg_gap_profile_available=True,
            lesson_generated=True,
            lesson_completed=True,
            assessment_attempted=True,
            mastery_updated=True,
            study_plan_generated=True,
            gamification_profile_available=True,
            parent_progress_report_available=True,
            popia_export_path_available=False,
            popia_erasure_path_available=False,
        )
    )
    report = build_vertical_journey_hardening_report(snapshot).to_payload()
    assert report["accepted"] is False
    assert report["popia_export_visible"] is False
    assert report["popia_erasure_visible"] is False
    assert "popia_export_path_available" in report["incomplete_milestones"]
    assert "popia_erasure_path_available" in report["incomplete_milestones"]
