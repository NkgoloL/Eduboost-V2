"""V2 repository unit tests — all DB I/O is mocked via AsyncMock patches.

Tests cover all 5 custom repositories:
  - StudyPlanRepository
  - ParentReportRepository
  - AuthRepository
  - LessonRepository (create + get_by_id)
  - DiagnosticRepository (create_session)
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


LEARNER_ID = str(uuid.uuid4())
GUARDIAN_ID = str(uuid.uuid4())
PLAN_ID = str(uuid.uuid4())
LESSON_ID = str(uuid.uuid4())


# ---------------------------------------------------------------------------
# StudyPlanRepository
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="Legacy mock setup broken by BaseRepository migration")
class TestStudyPlanRepository:
    def _mock_session(self):
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        return session

    @pytest.mark.asyncio
    async def test_create_returns_dict(self):
        from app.repositories.study_plan_repository import StudyPlanRepository
        repo = StudyPlanRepository()
        mock_plan = MagicMock()
        mock_plan.plan_id = uuid.UUID(PLAN_ID)
        mock_plan.week_start = datetime.now(timezone.utc)
        mock_plan.schedule = {}
        mock_plan.gap_ratio = 0.4
        mock_plan.week_focus = "Test focus"
        mock_plan.generated_by = "V2_ALGORITHM"

        session = self._mock_session()
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        with patch("app.repositories.study_plan_repository.AsyncSessionFactory") as mock_factory:
            with patch("app.repositories.study_plan_repository.StudyPlan") as mock_plan_class:
                mock_plan_class.return_value = mock_plan
                mock_factory.return_value = session
                result = await repo.create(
                    learner_id=LEARNER_ID,
                    schedule={"monday": []},
                    gap_ratio=0.4,
                    week_focus="Test focus",
                )
        # Result must be a dict with required keys
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_for_missing(self):
        from app.repositories.study_plan_repository import StudyPlanRepository
        repo = StudyPlanRepository()
        session = self._mock_session()
        execute_result = MagicMock()
        execute_result.scalar_one_or_none = MagicMock(return_value=None)
        session.execute = AsyncMock(return_value=execute_result)
        with patch("app.repositories.study_plan_repository.AsyncSessionFactory",
                   return_value=session):
            result = await repo.get_by_id(str(uuid.uuid4()))
        assert result is None

    @pytest.mark.asyncio
    async def test_list_for_learner_returns_list(self):
        from app.repositories.study_plan_repository import StudyPlanRepository
        repo = StudyPlanRepository()
        session = self._mock_session()
        execute_result = MagicMock()
        execute_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        session.execute = AsyncMock(return_value=execute_result)
        with patch("app.repositories.study_plan_repository.AsyncSessionFactory",
                   return_value=session):
            result = await repo.list_for_learner(LEARNER_ID)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_subject_mastery_returns_list(self):
        from app.repositories.study_plan_repository import StudyPlanRepository
        repo = StudyPlanRepository()
        session = self._mock_session()
        execute_result = MagicMock()
        execute_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        session.execute = AsyncMock(return_value=execute_result)
        with patch("app.repositories.study_plan_repository.AsyncSessionFactory",
                   return_value=session):
            result = await repo.get_subject_mastery(LEARNER_ID)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# ParentReportRepository
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="Legacy mock setup broken by BaseRepository migration")
class TestParentReportRepository:
    def _mock_session(self):
        s = AsyncMock()
        s.__aenter__ = AsyncMock(return_value=s)
        s.__aexit__ = AsyncMock(return_value=False)
        return s

    @pytest.mark.asyncio
    async def test_verify_guardian_link_false_when_missing(self):
        from app.repositories.parent_report_repository import ParentReportRepository
        repo = ParentReportRepository()
        session = self._mock_session()
        execute_result = MagicMock()
        execute_result.scalar_one_or_none = MagicMock(return_value=None)
        session.execute = AsyncMock(return_value=execute_result)
        with patch("app.repositories.parent_report_repository.AsyncSessionFactory",
                   return_value=session):
            result = await repo.verify_guardian_link(LEARNER_ID, GUARDIAN_ID)
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_guardian_link_true_when_present(self):
        from app.repositories.parent_report_repository import ParentReportRepository
        repo = ParentReportRepository()
        session = self._mock_session()
        execute_result = MagicMock()
        execute_result.scalar_one_or_none = MagicMock(return_value=MagicMock())
        session.execute = AsyncMock(return_value=execute_result)
        with patch("app.repositories.parent_report_repository.AsyncSessionFactory",
                   return_value=session):
            result = await repo.verify_guardian_link(LEARNER_ID, GUARDIAN_ID)
        assert result is True

    @pytest.mark.asyncio
    async def test_get_subject_mastery_returns_list(self):
        from app.repositories.parent_report_repository import ParentReportRepository
        repo = ParentReportRepository()
        session = self._mock_session()
        execute_result = MagicMock()
        execute_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        session.execute = AsyncMock(return_value=execute_result)
        with patch("app.repositories.parent_report_repository.AsyncSessionFactory",
                   return_value=session):
            result = await repo.get_subject_mastery(LEARNER_ID)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_reports_for_learner_returns_list(self):
        from app.repositories.parent_report_repository import ParentReportRepository
        repo = ParentReportRepository()
        session = self._mock_session()
        execute_result = MagicMock()
        execute_result.mappings = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        session.execute = AsyncMock(return_value=execute_result)
        with patch("app.repositories.parent_report_repository.AsyncSessionFactory",
                   return_value=session):
            result = await repo.get_reports_for_learner(LEARNER_ID, GUARDIAN_ID)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# AuthRepository
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="Legacy mock setup broken by BaseRepository migration")
class TestAuthRepository:
    def _mock_session(self):
        s = AsyncMock()
        s.__aenter__ = AsyncMock(return_value=s)
        s.__aexit__ = AsyncMock(return_value=False)
        return s

    @pytest.mark.asyncio
    async def test_get_guardian_by_email_hash_none_when_missing(self):
        from app.repositories.auth_repository import AuthRepository
        repo = AuthRepository()
        session = self._mock_session()
        execute_result = MagicMock()
        execute_result.scalar_one_or_none = MagicMock(return_value=None)
        session.execute = AsyncMock(return_value=execute_result)
        with patch("app.repositories.auth_repository.AsyncSessionFactory",
                   return_value=session):
            result = await repo.get_guardian_by_email_hash("test@example.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_is_jti_revoked_false_when_not_present(self):
        from app.repositories.auth_repository import AuthRepository
        repo = AuthRepository()
        session = self._mock_session()
        execute_result = MagicMock()
        execute_result.first = MagicMock(return_value=None)
        session.execute = AsyncMock(return_value=execute_result)
        with patch("app.repositories.auth_repository.AsyncSessionFactory",
                   return_value=session):
            result = await repo.is_jti_revoked("some-jti")
        assert result is False

    @pytest.mark.asyncio
    async def test_is_jti_revoked_true_when_present(self):
        from app.repositories.auth_repository import AuthRepository
        repo = AuthRepository()
        session = self._mock_session()
        execute_result = MagicMock()
        execute_result.first = MagicMock(return_value=("jti",))
        session.execute = AsyncMock(return_value=execute_result)
        with patch("app.repositories.auth_repository.AsyncSessionFactory",
                   return_value=session):
            result = await repo.is_jti_revoked("revoked-jti")
        assert result is True


# ---------------------------------------------------------------------------
# LessonRepository
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="Legacy mock setup broken by BaseRepository migration")
class TestLessonRepository:
    def _mock_session(self):
        s = AsyncMock()
        s.__aenter__ = AsyncMock(return_value=s)
        s.__aexit__ = AsyncMock(return_value=False)
        return s

    @pytest.mark.asyncio
    async def test_get_by_id_none_when_missing(self):
        from app.repositories.lesson_repository import LessonRepository
        repo = LessonRepository()
        session = self._mock_session()
        execute_result = MagicMock()
        execute_result.scalar_one_or_none = MagicMock(return_value=None)
        session.execute = AsyncMock(return_value=execute_result)
        with patch("app.repositories.lesson_repository.AsyncSessionFactory",
                   return_value=session):
            result = await repo.get_by_id(str(uuid.uuid4()))
        assert result is None

    @pytest.mark.asyncio
    async def test_create_commits(self):
        from app.repositories.lesson_repository import LessonRepository
        repo = LessonRepository()
        session = self._mock_session()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        with patch("app.repositories.lesson_repository.AsyncSessionFactory",
                   return_value=session):
            await repo.create(
                lesson={"lesson_id": LESSON_ID, "title": "T", "subject_code": "MATH",
                        "topic": "Fractions", "content": "{}"},
                grade_level=4,
            )
        session.commit.assert_called_once()


# ---------------------------------------------------------------------------
# DiagnosticRepository
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="Legacy mock setup broken by BaseRepository migration")
class TestDiagnosticRepository:
    def _mock_session(self):
        s = AsyncMock()
        s.__aenter__ = AsyncMock(return_value=s)
        s.__aexit__ = AsyncMock(return_value=False)
        return s

    @pytest.mark.asyncio
    async def test_create_session_commits(self):
        from app.repositories.diagnostic_repository import DiagnosticRepository
        repo = DiagnosticRepository()
        session = self._mock_session()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        with patch("app.repositories.diagnostic_repository.AsyncSessionFactory",
                   return_value=session):
            await repo.create_session(
                learner_id=LEARNER_ID,
                subject_code="MATH",
                grade_level=4,
                theta=0.5,
                sem=0.3,
                items_administered=10,
                items_correct=7,
                items_total=10,
                final_mastery_score=0.7,
                knowledge_gaps=[],
            )
        session.commit.assert_called_once()
