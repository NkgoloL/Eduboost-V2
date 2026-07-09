from app.modules.vertical_journey.service import VerticalJourneyInputs, build_vertical_journey_snapshot


def test_vertical_journey_snapshot_tracks_completion_ratio_and_current_step():
    snapshot = build_vertical_journey_snapshot(
        VerticalJourneyInputs(
            learner_id="learner-1",
            guardian_id="guardian-1",
            learner_profile_created=True,
            guardian_consent_active=True,
            learner_onboarding_completed=True,
            diagnostic_completed=True,
            runtime_kg_gap_profile_available=True,
            lesson_generated=False,
        )
    )

    payload = snapshot.to_payload()

    assert payload["prd_id"] == "PRD-3.0-3.4"
    assert payload["completion_ratio"] > 0
    assert payload["current_milestone"] == "lesson_generated"
    assert payload["prd4_implementation_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False


def test_vertical_journey_consent_gap_blocks_downstream_learning_steps():
    snapshot = build_vertical_journey_snapshot(
        VerticalJourneyInputs(
            learner_id="learner-2",
            guardian_id="guardian-1",
            learner_profile_created=True,
            guardian_consent_active=False,
        )
    )

    payload = snapshot.to_payload()

    assert "guardian_consent_inactive" in payload["blocked_reasons"]
    diagnostic = next(item for item in payload["milestones"] if item["key"] == "diagnostic_completed")
    assert diagnostic["complete"] is False
    assert "guardian_consent_inactive" in diagnostic["blocked_by"]


def test_vertical_journey_snapshot_can_represent_complete_controlled_journey():
    snapshot = build_vertical_journey_snapshot(
        VerticalJourneyInputs(
            learner_id="learner-3",
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

    payload = snapshot.to_payload()

    assert payload["complete"] is True
    assert payload["completion_ratio"] == 1.0
    assert payload["current_milestone"] is None
