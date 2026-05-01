import pytest
from unittest.mock import AsyncMock

from app.services.assessment_service_v2 import AssessmentServiceV2
from app.services.diagnostic_service_v2 import DiagnosticServiceV2
from app.services.gamification_service_v2 import GamificationServiceV2
from app.services.lesson_service_v2 import LessonServiceV2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assessment_service_uses_repository():
    repo = AsyncMock()
    repo.list_assessments.return_value = [{"assessment_id": "1"}]
    service = AssessmentServiceV2(repository=repo)

    result = await service.list_assessments(limit=10, offset=0)

    assert result["assessments"] == [{"assessment_id": "1"}]
    repo.list_assessments.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_gamification_service_uses_repository():
    learner = type("Learner", (), {"learner_id": "learner-1", "total_xp": 120, "streak_days": 4})
    badge = type("Badge", (), {"badge_key": "starter", "name": "Starter"})
    learner_badge = type("LearnerBadge", (), {"earned_at": None})
    repo = AsyncMock()
    repo.get_profile_rows.return_value = (learner, [(learner_badge, badge)])
    service = GamificationServiceV2(repository=repo)

    result = await service.get_profile("learner-1")

    assert result["learner_id"] == "learner-1"
    assert result["badges"][0]["badge_key"] == "starter"
    repo.get_profile_rows.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_diagnostic_service_uses_repository():
    learner = type("LearnerProfile", (), {"grade": 4, "overall_mastery": 0.8})
    learner_repo = AsyncMock()
    learner_repo.get_by_id.return_value = learner
    quota = AsyncMock()
    quota.get_cached.return_value = {"cached": True}
    diag_repo = AsyncMock()

    service = DiagnosticServiceV2(
        learner_repository=learner_repo,
        quota_service=quota,
        diagnostic_repository=diag_repo,
    )

    result = await service.run_diagnostic("learner-1", "MATH")

    assert result == {"cached": True}
    learner_repo.get_by_id.assert_awaited_once()
    quota.get_cached.assert_awaited_once()
    diag_repo.create_session.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_lesson_service_accepts_repository_injection():
    repo = AsyncMock()
    quota = AsyncMock()
    quota.get_cached.return_value = {"lesson_id": "cached-1"}
    service = LessonServiceV2(lesson_repository=repo)
    service.quota_service = quota

    result = await service.generate_lesson("learner-1", "MATH", "Fractions")

    assert result["lesson_id"] == "cached-1"
    repo.create.assert_not_called()
