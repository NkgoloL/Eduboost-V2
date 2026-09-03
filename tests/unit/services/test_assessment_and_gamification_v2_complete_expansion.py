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

