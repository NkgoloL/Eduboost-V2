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


def test_vertical_journey_all_dependency_blockers():
    # 1. learner_profile_created = False blocks everything else
    snap_no_profile = build_vertical_journey_snapshot(
        VerticalJourneyInputs(
            learner_id="l-no-prof",
            guardian_id=None,
            learner_profile_created=False,
            guardian_consent_active=True,
        )
    )
    p1 = snap_no_profile.to_payload()
    assert "learner_profile_missing" in p1["blocked_reasons"]
    assert "guardian_context_missing" in p1["blocked_reasons"]

    # 2. diagnostic_not_completed blocks kg_gap, lesson_generated, study_plan
    snap_no_diag = build_vertical_journey_snapshot(
        VerticalJourneyInputs(
            learner_id="l-no-diag",
            guardian_id="g-1",
            learner_profile_created=True,
            guardian_consent_active=True,
            diagnostic_completed=False,
            lesson_generated=False,
        )
    )
    p2 = snap_no_diag.to_payload()
    assert "diagnostic_not_completed" in p2["blocked_reasons"]

    # 3. lesson_not_generated blocks lesson_completed, assessment_attempted, mastery_updated
    snap_no_lesson = build_vertical_journey_snapshot(
        VerticalJourneyInputs(
            learner_id="l-no-lesson",
            guardian_id="g-1",
            learner_profile_created=True,
            guardian_consent_active=True,
            diagnostic_completed=True,
            lesson_generated=False,
        )
    )
    p3 = snap_no_lesson.to_payload()
    assert "lesson_not_generated" in p3["blocked_reasons"]

    # 4. Milestone to_payload
    m = snap_no_lesson.milestones[0]
    mp = m.to_payload()
    assert mp["key"] == "learner_profile_created"
    assert mp["complete"] is True
