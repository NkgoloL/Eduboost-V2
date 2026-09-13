from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.assessment_service_v2 import AssessmentServiceV2
from app.services.gamification_service_v2 import GamificationServiceV2, _EmptyGamificationRepository


@pytest.mark.asyncio
async def test_assessment_service_v2_complete():
    mock_repo = AsyncMock()
    mock_db = AsyncMock()

    # 1. Initialization and with_db (lines 11-23)
    svc = AssessmentServiceV2(repository=mock_repo, db=mock_db)
    assert svc.db is mock_db
    mock_repo.db = None
    svc.with_db(mock_db)
    assert mock_repo.db is mock_db

    # with_db when repository does not have 'db' attribute (line 21->23 False branch)
    class SimpleRepo:
        pass
    svc_no_db_attr = AssessmentServiceV2(repository=SimpleRepo())
    svc_no_db_attr.with_db(mock_db)

    # Lazy repo initialization branch (lines 13-15)
    with patch("app.repositories.assessment_repository.AssessmentRepository") as mock_repo_cls:
        svc_lazy = AssessmentServiceV2(db=mock_db)
        mock_repo_cls.assert_called_once_with(mock_db)


    # 2. list_assessments (lines 25-28)
    mock_repo.list_assessments.return_value = [{"id": "a1", "title": "Maths Quiz"}]
    res_list = await svc.list_assessments(limit=10, offset=0)
    assert res_list == {"assessments": [{"id": "a1", "title": "Maths Quiz"}]}

    # 3. submit_attempt assessment not found (lines 37-39)
    mock_repo.get_assessment.return_value = None
    with pytest.raises(ValueError, match="Assessment not found"):
        await svc.submit_attempt("missing-id", "learner-1", [])

    # 4. submit_attempt successful calculation (lines 40-74)
    mock_assessment = {
        "id": "a1",
        "total_marks": 5,
        "questions": [
            {"question_id": "q1", "correct_answer": "A", "marks": 2},
            {"item_id": "q2", "correct_answer": "B", "marks": 3},
            {"item_id": "q3", "correct_answer": "C", "marks": 1},
        ],
    }
    mock_repo.get_assessment.return_value = mock_assessment
    mock_repo.create_attempt.return_value = "attempt-123"

    responses = [
        {"question_id": "q1", "selected_option": "A"},  # correct (+2)
        {"item_id": "q2", "learner_answer": "b"},       # correct (+3)
        {"item_id": "q3", "answer": "Wrong"},           # incorrect
        {"no_id": "skip"},
    ]

    res_attempt = await svc.submit_attempt("a1", "learner-1", responses, time_taken_seconds=120)
    assert res_attempt["attempt_id"] == "attempt-123"
    assert res_attempt["correct_count"] == 2
    assert res_attempt["marks_obtained"] == 5
    assert res_attempt["score"] == 1.0
    assert res_attempt["total_marks"] == 5

    # 5. submit_attempt with zero total_marks fallback (line 56)
    mock_assessment_zero = {"id": "a2", "total_marks": 0, "questions": []}
    mock_repo.get_assessment.return_value = mock_assessment_zero
    res_zero = await svc.submit_attempt("a2", "learner-1", [])
    assert res_zero["score"] == 0.0


@pytest.mark.asyncio
async def test_gamification_service_v2_complete():
    mock_session = AsyncMock()

    # 1. from_session and session-based repo initialization (lines 16-17, 21-23)
    with patch("app.services.gamification_service_v2.GamificationRepository") as mock_gam_repo_cls:
        svc_session = GamificationServiceV2.from_session(mock_session)
        mock_gam_repo_cls.assert_called_once_with(mock_session)


    # 2. _EmptyGamificationRepository defaults (lines 74-80)
    empty_repo = _EmptyGamificationRepository()
    learner, badges = await empty_repo.get_profile_rows("l1")
    assert learner is None
    assert badges == []
    assert await empty_repo.get_leaderboard_rows() == []

    # 3. award_xp with session None (lines 49-50)
    svc_no_session = GamificationServiceV2()
    await svc_no_session.award_xp("learner-1", 50)

    # 4. award_xp with session and lesson_id (lines 51-54)
    with patch("app.services.gamification_service_v2.LearnerRepository") as mock_learner_repo_cls, \
         patch("app.services.gamification_service_v2.LessonRepository") as mock_lesson_repo_cls:
        mock_l_repo = AsyncMock()
        mock_les_repo = AsyncMock()
        mock_learner_repo_cls.return_value = mock_l_repo
        mock_lesson_repo_cls.return_value = mock_les_repo

        svc_with_session = GamificationServiceV2(session=mock_session)
        await svc_with_session.award_xp("learner-1", 100, lesson_id="les-456")
        await svc_with_session.award_xp("learner-1", 100, lesson_id=None)

        assert mock_l_repo.add_xp.await_count == 2
        mock_les_repo.mark_completed.assert_awaited_once_with("les-456")

    # 5. repository parameter passed directly (lines 14-15)
    custom_repo = AsyncMock()
    svc_custom = GamificationServiceV2(repository=custom_repo)
    assert svc_custom.repository is custom_repo

    # 6. get_profile learner not found (lines 26-28)
    custom_repo.get_profile_rows.return_value = (None, [])
    with pytest.raises(ValueError, match="Learner not found"):
        await svc_custom.get_profile("missing-learner")

    # 7. get_profile success with badges and audit log (lines 29-46, 68-71)
    learner_obj = {
        "learner_id": "l-100",
        "total_xp": 250,
        "streak_days": 4,
    }
    badge_rows = [
        ({"earned_at": "2026-09-01"}, {"badge_key": "first_lesson", "name": "First Lesson"}),
        (type("BadgeRef", (), {"earned_at": "2026-09-02"})(), type("BadgeInfo", (), {"badge_key": "streak_3", "name": "3 Day Streak"})()),
    ]
    custom_repo.get_profile_rows.return_value = (learner_obj, badge_rows)
    with patch("app.services.gamification_service_v2.AuditService") as mock_audit_cls:
        mock_audit = AsyncMock()
        mock_audit_cls.return_value = mock_audit
        profile = await svc_custom.get_profile("l-100")
        assert profile["learner_id"] == "l-100"
        assert profile["total_xp"] == 250
        assert profile["level"] == 3  # 250 // 100 + 1
        assert len(profile["badges"]) == 2
        assert profile["badges"][0]["badge_key"] == "first_lesson"
        assert profile["badges"][1]["badge_key"] == "streak_3"
        mock_audit.log_event.assert_awaited_once_with("GAMIFICATION_PROFILE_READ", {}, "l-100")

    # 8. leaderboard (lines 56-65)
    custom_repo.get_leaderboard_rows.return_value = [
        {"learner_id": "l-1", "total_xp": 500, "streak_days": 10},
        type("LeaderRow", (), {"id": "l-2", "xp": 300, "streak_days": 5})(),
    ]
    lb = await svc_custom.leaderboard(limit=5)
    assert len(lb) == 2
    assert lb[0]["learner_id"] == "l-1"
    assert lb[0]["total_xp"] == 500
    assert lb[1]["learner_id"] == "l-2"
    assert lb[1]["total_xp"] == 300

