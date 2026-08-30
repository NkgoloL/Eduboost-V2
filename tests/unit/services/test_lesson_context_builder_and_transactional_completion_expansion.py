"""Batch 206: Unit tests for lesson_context_builder and lesson_transactional_completion services."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from app.services.lesson_context_builder import (
    GRADE_LEVEL_THRESHOLD,
    LessonContext,
    LessonContextBuilder,
)
from app.services.lesson_transactional_completion import (
    LessonCompletionInput,
    LessonCompletionNotFoundError,
    LessonCompletionResult,
    LessonCompletionTransactionError,
    TransactionalLessonCompletionService,
)


# ─────────────────────────────────────────────
# LessonContext
# ─────────────────────────────────────────────


class TestLessonContext:
    def test_to_prompt_dict_basic(self):
        ctx = LessonContext(
            learner_id="learner-1",
            caps_ref="4.M.1.1",
            grade=4,
            subject="Mathematics",
            term=1,
            topic="Whole Numbers",
            subtopic="Counting",
            language="en",
            theta=0.5,
            below_grade_level=False,
            severity="mild",
            misconception_tags=["place_value"],
            gap_topics=["4.M.1.1"],
            remediation_focus="Focus on numbers",
            suggested_examples=["Example 1"],
            prior_correct_count=8,
            prior_attempted=10,
        )
        prompt_dict = ctx.to_prompt_dict()
        assert prompt_dict["learner_id"] == "learner-1"
        assert prompt_dict["caps_ref"] == "4.M.1.1"
        assert prompt_dict["accuracy_pct"] == 80.0
        assert prompt_dict["theta"] == 0.5

    def test_to_prompt_dict_zero_attempts_accuracy(self):
        ctx = LessonContext(
            learner_id="l-2",
            caps_ref="4.M.1.1",
            grade=4,
            subject="Mathematics",
            term=1,
            topic="Math",
            subtopic="Sub",
            prior_correct_count=0,
            prior_attempted=0,
        )
        prompt_dict = ctx.to_prompt_dict()
        assert prompt_dict["accuracy_pct"] == 0.0


# ─────────────────────────────────────────────
# LessonContextBuilder
# ─────────────────────────────────────────────


class TestLessonContextBuilder:
    @pytest.fixture
    def topic_map(self):
        return {
            "4.M.1.1": {
                "grade": 4,
                "subject": "Mathematics",
                "term": 1,
                "topic": "Whole Numbers",
                "subtopic": "Count and Order",
                "suggested_examples": ["Order 12, 15, 9."],
            }
        }

    def test_build_with_known_caps_ref(self, topic_map):
        builder = LessonContextBuilder(topic_map)
        session_result = {
            "learner_id": "L1",
            "caps_ref": "4.M.1.1",
            "theta": 0.5,
            "below_grade_level": False,
            "misconception_tags": ["tag_a"],
            "gap_topics": [],
            "items_correct": 4,
            "items_attempted": 5,
        }
        ctx = builder.build(session_result, learner_language="zu")
        assert ctx.learner_id == "L1"
        assert ctx.grade == 4
        assert ctx.subject == "Mathematics"
        assert ctx.topic == "Whole Numbers"
        assert ctx.language == "zu"
        assert ctx.severity == "mild"
        assert "Whole Numbers" in ctx.remediation_focus

    def test_build_with_unknown_caps_ref_fallback(self, topic_map):
        builder = LessonContextBuilder(topic_map)
        session_result = {
            "learner_id": "L2",
            "caps_ref": "UNKNOWN.CAPS.REF",
            "theta": -1.5,
            "below_grade_level": True,
            "misconception_tags": ["deep_misconception"],
            "items_correct": 1,
            "items_attempted": 5,
        }
        ctx = builder.build(session_result, learner_language="en")
        assert ctx.caps_ref == "UNKNOWN.CAPS.REF"
        assert ctx.severity == "severe"
        assert ctx.grade == 4  # default fallback
        assert "foundational re-teaching" in ctx.remediation_focus

    def test_classify_severity_thresholds(self):
        assert LessonContextBuilder._classify_severity(0.5) == "mild"
        assert LessonContextBuilder._classify_severity(0.0) == "mild"
        assert LessonContextBuilder._classify_severity(-0.5) == "moderate"
        assert LessonContextBuilder._classify_severity(-1.0) == "moderate"
        assert LessonContextBuilder._classify_severity(-1.5) == "severe"


# ─────────────────────────────────────────────
# Lesson Completion Services & Transactional Flow
# ─────────────────────────────────────────────


class TestLessonCompletionDataclasses:
    def test_input_fields_and_defaults(self):
        inp = LessonCompletionInput(
            lesson_id="les-1",
            learner_id="learn-1",
            xp_award=50,
            audit_actor_id="actor-1",
        )
        assert inp.lesson_id == "les-1"
        assert inp.xp_award == 50
        assert inp.fail_after_lesson is False
        assert inp.fail_after_xp is False
        assert inp.fail_after_audit is False

    def test_result_fields(self):
        res = LessonCompletionResult(
            lesson_id="les-1",
            learner_id="learn-1",
            xp_award=50,
            audit_event_id="audit-123",
        )
        assert res.audit_event_id == "audit-123"

    def test_errors_subclass_runtime_error(self):
        assert issubclass(LessonCompletionTransactionError, RuntimeError)
        assert issubclass(LessonCompletionNotFoundError, RuntimeError)


def _make_mock_session_for_completion(lesson_rowcount=1, profile_rowcount=1):
    mock_session = MagicMock()
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=None)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)
    mock_session.begin = MagicMock(return_value=mock_ctx)

    lesson_exec_result = MagicMock(rowcount=lesson_rowcount)
    profile_exec_result = MagicMock(rowcount=profile_rowcount)
    audit_exec_result = MagicMock(rowcount=1)

    mock_session.execute = AsyncMock(
        side_effect=[lesson_exec_result, profile_exec_result, audit_exec_result]
    )
    return mock_session


def _make_completion_service(session):
    mock_lessons = MagicMock()
    mock_lessons.update.return_value.where.return_value.where.return_value.values.return_value = MagicMock()
    mock_lessons.c.id = "id"
    mock_lessons.c.learner_id = "learner_id"

    mock_profiles = MagicMock()
    mock_profiles.update.return_value.where.return_value.values.return_value = MagicMock()
    mock_profiles.c.learner_id = "learner_id"
    mock_profiles.c.xp = 100

    mock_audit = MagicMock()
    mock_audit.insert.return_value.values.return_value = MagicMock()

    fixed_time = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)

    return TransactionalLessonCompletionService(
        session=session,
        lessons_table=mock_lessons,
        profiles_table=mock_profiles,
        audit_events_table=mock_audit,
        clock=lambda: fixed_time,
    )


class TestTransactionalLessonCompletionService:
    @pytest.mark.asyncio
    async def test_successful_lesson_completion(self):
        session = _make_mock_session_for_completion(lesson_rowcount=1, profile_rowcount=1)
        service = _make_completion_service(session)
        data = LessonCompletionInput(
            lesson_id="les-001",
            learner_id="learn-001",
            xp_award=25,
            audit_actor_id="actor-1",
        )
        result = await service.complete_lesson(data)
        assert isinstance(result, LessonCompletionResult)
        assert result.lesson_id == "les-001"
        assert result.learner_id == "learn-001"
        assert result.xp_award == 25
        assert result.audit_event_id is not None
        assert session.execute.call_count == 3

    @pytest.mark.asyncio
    async def test_lesson_not_found_raises(self):
        session = _make_mock_session_for_completion(lesson_rowcount=0, profile_rowcount=1)
        service = _make_completion_service(session)
        data = LessonCompletionInput(
            lesson_id="missing-les",
            learner_id="learn-001",
            xp_award=25,
            audit_actor_id="actor-1",
        )
        with pytest.raises(LessonCompletionNotFoundError, match="lesson not found"):
            await service.complete_lesson(data)

    @pytest.mark.asyncio
    async def test_profile_not_found_raises(self):
        session = _make_mock_session_for_completion(lesson_rowcount=1, profile_rowcount=0)
        service = _make_completion_service(session)
        data = LessonCompletionInput(
            lesson_id="les-001",
            learner_id="missing-profile",
            xp_award=25,
            audit_actor_id="actor-1",
        )
        with pytest.raises(LessonCompletionNotFoundError, match="gamification profile not found"):
            await service.complete_lesson(data)

    @pytest.mark.asyncio
    async def test_fail_after_lesson_simulated_error(self):
        session = _make_mock_session_for_completion()
        service = _make_completion_service(session)
        data = LessonCompletionInput(
            lesson_id="les-001",
            learner_id="learn-001",
            xp_award=25,
            audit_actor_id="actor-1",
            fail_after_lesson=True,
        )
        with pytest.raises(LessonCompletionTransactionError, match="after lesson completion"):
            await service.complete_lesson(data)

    @pytest.mark.asyncio
    async def test_fail_after_xp_simulated_error(self):
        session = _make_mock_session_for_completion()
        service = _make_completion_service(session)
        data = LessonCompletionInput(
            lesson_id="les-001",
            learner_id="learn-001",
            xp_award=25,
            audit_actor_id="actor-1",
            fail_after_xp=True,
        )
        with pytest.raises(LessonCompletionTransactionError, match="after XP update"):
            await service.complete_lesson(data)

    @pytest.mark.asyncio
    async def test_fail_after_audit_simulated_error(self):
        session = _make_mock_session_for_completion()
        service = _make_completion_service(session)
        data = LessonCompletionInput(
            lesson_id="les-001",
            learner_id="learn-001",
            xp_award=25,
            audit_actor_id="actor-1",
            fail_after_audit=True,
        )
        with pytest.raises(LessonCompletionTransactionError, match="after audit write"):
            await service.complete_lesson(data)
