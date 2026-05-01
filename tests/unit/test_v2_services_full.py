"""Full V2 service unit-test suite.

Covers: LessonServiceV2, StudyPlanServiceV2, ParentReportServiceV2,
        AssessmentServiceV2, GamificationServiceV2, AuthService, AuditService.

All external I/O (DB, Redis, LLM) is mocked — no live infrastructure required.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.entities import LearnerProfile, AuditLog
from app.domain.schemas import AuditLogEntry

LEARNER_ID = str(uuid.uuid4())
GUARDIAN_ID = str(uuid.uuid4())
PLAN_ID = str(uuid.uuid4())
LESSON_ID = str(uuid.uuid4())
ASSESSMENT_ID = str(uuid.uuid4())


def _learner(grade: int = 4, mastery: float = 0.6) -> LearnerProfile:
    return LearnerProfile(learner_id=LEARNER_ID, grade=grade, home_language="en", overall_mastery=mastery)


def _audit_log(event_type: str = "TEST") -> AuditLog:
    return AuditLog(event_id=str(uuid.uuid4()), learner_id=LEARNER_ID, event_type=event_type,
                    occurred_at=datetime.now(timezone.utc), payload={})


# ---------------------------------------------------------------------------
# LessonServiceV2
# ---------------------------------------------------------------------------

class TestLessonServiceV2:
    def _svc(self, cached=None, db_row=None):
        from app.services.lesson_service_v2 import LessonServiceV2
        repo = AsyncMock()
        repo.create = AsyncMock()
        repo.get_by_id = AsyncMock(return_value=db_row)
        svc = LessonServiceV2(lesson_repository=repo)
        svc.redis = AsyncMock()
        svc.redis.get = AsyncMock(return_value=None)
        svc.redis.set = AsyncMock()
        svc.quota_service = AsyncMock()
        svc.quota_service.assert_within_quota = AsyncMock(return_value=1)
        svc.quota_service.get_cached = AsyncMock(return_value=cached)
        svc.quota_service.set_cached = AsyncMock()
        return svc, repo

    @pytest.mark.asyncio
    async def test_generate_returns_cached(self):
        cached = {"lesson_id": LESSON_ID, "source": "cache"}
        svc, _ = self._svc(cached=cached)
        with patch("app.services.lesson_service_v2.AuditService"):
            result = await svc.generate_lesson(LEARNER_ID, "MATH", "Fractions")
        assert result["lesson_id"] == LESSON_ID

    @pytest.mark.asyncio
    async def test_generate_calls_llm_on_cache_miss(self):
        svc, repo = self._svc()
        fake = {"story_hook": "test", "learning_objectives": [], "key_concepts": [],
                "worked_example": "", "practice_questions": [], "reflection": ""}
        with patch("app.services.lesson_service_v2._call_llm", new=AsyncMock(return_value=fake)):
            with patch("app.services.lesson_service_v2.AuditService") as a:
                a.return_value.log_event = AsyncMock()
                result = await svc.generate_lesson(LEARNER_ID, "MATH", "Fractions", grade_level=4)
        assert result["generated_by"] == "V2_LLM"
        repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_enforces_quota(self):
        from app.services.quota_service import QuotaExceededError
        svc, _ = self._svc()
        svc.quota_service.assert_within_quota = AsyncMock(side_effect=QuotaExceededError("over"))
        with pytest.raises(QuotaExceededError):
            await svc.generate_lesson(LEARNER_ID, "MATH", "Fractions")

    @pytest.mark.asyncio
    async def test_get_lesson_from_redis(self):
        import json
        svc, _ = self._svc()
        svc.redis.get = AsyncMock(return_value=json.dumps({"lesson_id": LESSON_ID}))
        result = await svc.get_lesson(LESSON_ID)
        assert result["lesson_id"] == LESSON_ID

    @pytest.mark.asyncio
    async def test_get_lesson_falls_back_to_db(self):
        row = MagicMock()
        row.lesson_id = LESSON_ID
        row.title = "DB Lesson"
        row.subject_code = "MATH"
        row.grade_level = 4
        row.topic = "Fractions"
        row.content = {}
        row.generated_by = "V2_LLM"
        svc, _ = self._svc(db_row=row)
        result = await svc.get_lesson(LESSON_ID)
        assert result["source"] == "database"

    @pytest.mark.asyncio
    async def test_get_lesson_none_when_missing(self):
        svc, _ = self._svc(db_row=None)
        assert await svc.get_lesson(str(uuid.uuid4())) is None

    @pytest.mark.asyncio
    async def test_submit_feedback(self):
        svc, _ = self._svc()
        with patch("app.services.lesson_service_v2.AuditService") as a:
            a.return_value.log_event = AsyncMock()
            r = await svc.submit_feedback(LESSON_ID, LEARNER_ID, rating=5, comment="Great")
        assert r["recorded"] is True


# ---------------------------------------------------------------------------
# StudyPlanServiceV2
# ---------------------------------------------------------------------------

class TestStudyPlanServiceV2:
    def _svc(self, learner=None, mastery=None, plan=None):
        from app.services.study_plan_service_v2 import StudyPlanServiceV2
        lr = AsyncMock(); lr.get_by_id = AsyncMock(return_value=learner)
        pr = AsyncMock()
        pr.get_subject_mastery = AsyncMock(return_value=mastery or [])
        pr.create = AsyncMock(return_value=plan or {"plan_id": PLAN_ID, "learner_id": LEARNER_ID,
                                                     "schedule": {}, "gap_ratio": 0.4, "week_focus": "ok"})
        pr.get_by_id = AsyncMock(return_value=plan)
        pr.list_for_learner = AsyncMock(return_value=[])
        return StudyPlanServiceV2(learner_repository=lr, study_plan_repository=pr), lr, pr

    @pytest.mark.asyncio
    async def test_generate_raises_learner_not_found(self):
        svc, _, _ = self._svc(learner=None)
        with pytest.raises(ValueError, match="Learner not found"):
            await svc.generate_plan(LEARNER_ID)

    @pytest.mark.asyncio
    async def test_generate_creates_plan(self):
        mastery = [{"subject_code": "MATH", "grade_level": 3, "mastery_score": 0.3, "knowledge_gaps": []}]
        svc, _, pr = self._svc(learner=_learner(), mastery=mastery)
        with patch("app.services.study_plan_service_v2.AuditService") as a:
            a.return_value.log_event = AsyncMock()
            r = await svc.generate_plan(LEARNER_ID)
        assert r["plan_id"] == PLAN_ID
        pr.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_balanced_focus_when_no_mastery(self):
        svc, _, pr = self._svc(learner=_learner(), mastery=[])
        with patch("app.services.study_plan_service_v2.AuditService") as a:
            a.return_value.log_event = AsyncMock()
            await svc.generate_plan(LEARNER_ID)
        assert "Balanced" in pr.create.call_args.kwargs["week_focus"]

    @pytest.mark.asyncio
    async def test_list_raises_learner_not_found(self):
        svc, _, _ = self._svc(learner=None)
        with pytest.raises(ValueError):
            await svc.list_plans(LEARNER_ID)


# ---------------------------------------------------------------------------
# ParentReportServiceV2
# ---------------------------------------------------------------------------

class TestParentReportServiceV2:
    def _svc(self, learner=None, linked=True, subjects=None):
        from app.services.parent_report_service_v2 import ParentReportServiceV2
        lr = AsyncMock(); lr.get_by_id = AsyncMock(return_value=learner)
        rr = AsyncMock()
        rr.verify_guardian_link = AsyncMock(return_value=linked)
        rr.get_subject_mastery = AsyncMock(return_value=subjects or [])
        rr.persist_report = AsyncMock(return_value=str(uuid.uuid4()))
        rr.get_reports_for_learner = AsyncMock(return_value=[])
        return ParentReportServiceV2(learner_repository=lr, parent_report_repository=rr), rr

    @pytest.mark.asyncio
    async def test_raises_learner_not_found(self):
        svc, _ = self._svc(learner=None)
        with pytest.raises(ValueError, match="Learner not found"):
            await svc.build_report(LEARNER_ID, GUARDIAN_ID)

    @pytest.mark.asyncio
    async def test_raises_guardian_not_linked(self):
        svc, _ = self._svc(learner=_learner(), linked=False)
        with pytest.raises(PermissionError, match="Guardian is not linked"):
            await svc.build_report(LEARNER_ID, GUARDIAN_ID)

    @pytest.mark.asyncio
    async def test_report_mentions_weak_subject(self):
        subjects = [{"subject_code": "MATH", "grade_level": 3, "mastery_score": 0.2, "knowledge_gaps": []}]
        svc, rr = self._svc(learner=_learner(), subjects=subjects)
        with patch("app.services.parent_report_service_v2.AuditService") as a:
            a.return_value.log_event = AsyncMock()
            r = await svc.build_report(LEARNER_ID, GUARDIAN_ID)
        assert "MATH" in r["summary"]
        rr.persist_report.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_reports(self):
        svc, rr = self._svc(learner=_learner())
        rr.get_reports_for_learner = AsyncMock(return_value=[{"report_id": "r1"}])
        result = await svc.list_reports(LEARNER_ID, GUARDIAN_ID)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# AssessmentServiceV2
# ---------------------------------------------------------------------------

class TestAssessmentServiceV2:
    @pytest.mark.asyncio
    async def test_list_assessments(self):
        from app.services.assessment_service_v2 import AssessmentServiceV2
        repo = AsyncMock()
        repo.list_assessments = AsyncMock(return_value=[{"assessment_id": "a1"}])
        svc = AssessmentServiceV2(repository=repo)
        with patch("app.services.assessment_service_v2.AuditService") as a:
            a.return_value.log_event = AsyncMock()
            r = await svc.list_assessments()
        assert r["assessments"][0]["assessment_id"] == "a1"

    @pytest.mark.asyncio
    async def test_submit_raises_not_found(self):
        from app.services.assessment_service_v2 import AssessmentServiceV2
        repo = AsyncMock(); repo.get_assessment = AsyncMock(return_value=None)
        svc = AssessmentServiceV2(repository=repo)
        with pytest.raises(ValueError, match="Assessment not found"):
            await svc.submit_attempt(ASSESSMENT_ID, LEARNER_ID, responses=[])

    @pytest.mark.asyncio
    async def test_submit_scores_correctly(self):
        from app.services.assessment_service_v2 import AssessmentServiceV2
        qs = [{"question_id": "q1", "correct_answer": "4", "marks": 2},
              {"question_id": "q2", "correct_answer": "paris", "marks": 1}]
        repo = AsyncMock()
        repo.get_assessment = AsyncMock(return_value={"questions": qs, "total_marks": 3})
        repo.create_attempt = AsyncMock(return_value=str(uuid.uuid4()))
        svc = AssessmentServiceV2(repository=repo)
        with patch("app.services.assessment_service_v2.AuditService") as a:
            a.return_value.log_event = AsyncMock()
            r = await svc.submit_attempt(ASSESSMENT_ID, LEARNER_ID,
                responses=[{"question_id": "q1", "learner_answer": "4"},
                            {"question_id": "q2", "learner_answer": "london"}])
        assert r["correct_count"] == 1
        assert r["marks_obtained"] == 2


# ---------------------------------------------------------------------------
# GamificationServiceV2
# ---------------------------------------------------------------------------

class TestGamificationServiceV2:
    @pytest.mark.asyncio
    async def test_get_profile_raises_not_found(self):
        from app.services.gamification_service_v2 import GamificationServiceV2
        repo = AsyncMock(); repo.get_profile_rows = AsyncMock(return_value=(None, []))
        svc = GamificationServiceV2(repository=repo)
        with pytest.raises(ValueError, match="Learner not found"):
            await svc.get_profile(LEARNER_ID)

    @pytest.mark.asyncio
    async def test_get_profile_calculates_level(self):
        from app.services.gamification_service_v2 import GamificationServiceV2
        ml = MagicMock(); ml.learner_id = uuid.UUID(LEARNER_ID); ml.total_xp = 350; ml.streak_days = 7
        repo = AsyncMock(); repo.get_profile_rows = AsyncMock(return_value=(ml, []))
        svc = GamificationServiceV2(repository=repo)
        with patch("app.services.gamification_service_v2.AuditService") as a:
            a.return_value.log_event = AsyncMock()
            r = await svc.get_profile(LEARNER_ID)
        assert r["level"] == 4

    @pytest.mark.asyncio
    async def test_leaderboard(self):
        from app.services.gamification_service_v2 import GamificationServiceV2
        learners = []
        for xp in [500, 300]:
            m = MagicMock(); m.learner_id = uuid.uuid4(); m.total_xp = xp; m.streak_days = 1
            learners.append(m)
        repo = AsyncMock(); repo.get_leaderboard_rows = AsyncMock(return_value=learners)
        svc = GamificationServiceV2(repository=repo)
        r = await svc.leaderboard()
        assert r[0]["total_xp"] == 500


# ---------------------------------------------------------------------------
# AuthService
# ---------------------------------------------------------------------------

class TestAuthService:
    def _svc(self):
        from app.services.auth_service import AuthService
        with patch("app.services.auth_service.get_v2_settings") as m:
            m.return_value.jwt_secret = "test-secret-32-chars-long-enough!!"
            m.return_value.jwt_algorithm = "HS256"
            return AuthService()

    def test_create_and_decode_session(self):
        svc = self._svc()
        s = svc.create_session("u1", "Parent")
        p = svc.decode_token(s.access_token)
        assert p["sub"] == "u1"

    def test_rotate_refresh_token(self):
        svc = self._svc()
        s = svc.create_session("u2", "Student")
        n = svc.rotate_refresh_token(s.refresh_token)
        assert svc.decode_token(n.access_token)["sub"] == "u2"

    def test_rotate_rejects_access_token(self):
        svc = self._svc()
        s = svc.create_session("u3", "Parent")
        with pytest.raises(ValueError):
            svc.rotate_refresh_token(s.access_token)

    def test_password_hash_verify(self):
        svc = self._svc()
        h = svc.hash_password("pass123")
        assert svc.verify_password("pass123", h)
        assert not svc.verify_password("wrong", h)


# ---------------------------------------------------------------------------
# AuditService
# ---------------------------------------------------------------------------

class TestAuditService:
    @pytest.mark.asyncio
    async def test_log_event(self):
        from app.services.audit_service import AuditService
        repo = AsyncMock(); repo.append = AsyncMock(return_value=_audit_log("EV"))
        svc = AuditService(repository=repo)
        e = await svc.log_event("EV", payload={}, learner_id=LEARNER_ID)
        assert isinstance(e, AuditLogEntry)
        assert e.event_type == "EV"

    @pytest.mark.asyncio
    async def test_get_recent_events(self):
        from app.services.audit_service import AuditService
        repo = AsyncMock(); repo.latest = AsyncMock(return_value=[_audit_log(f"E{i}") for i in range(3)])
        svc = AuditService(repository=repo)
        result = await svc.get_recent_events(limit=3)
        assert len(result) == 3
