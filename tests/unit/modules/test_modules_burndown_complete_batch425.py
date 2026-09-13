"""Unit tests for Batch 425:
- app/modules/lessons/service.py
- app/modules/lessons/llm_gateway.py
- app/modules/lessons/lesson_coverage_router.py
- app/modules/lessons/lesson_review_router.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

# ---------------------------------------------------------------------------
# Target 1: app/modules/lessons/service.py
# ---------------------------------------------------------------------------
from app.domain.schemas import LessonRequest, LessonResponse
from app.models import Lesson
from app.modules.lessons.service import LessonService
from app.services.lesson_generator import QuotaExceededError


class TestLessonService:
    @pytest.mark.asyncio
    async def test_init(self):
        mock_db = AsyncMock()
        svc = LessonService(mock_db)
        assert svc.db is mock_db
        assert svc._executive is not None
        assert svc._lesson_repo is not None
        assert svc._learner_repo is not None
        assert svc._guardian_repo is not None
        assert svc._consent_service is not None
        assert svc._audit_service is not None

    @pytest.mark.asyncio
    async def test_generate_lesson_for_learner_not_found(self):
        mock_db = AsyncMock()
        svc = LessonService(mock_db)
        svc._consent_service = AsyncMock()
        svc._learner_repo = AsyncMock()
        svc._learner_repo.get_by_id.return_value = None

        req = LessonRequest(
            learner_id=str(uuid4()),
            subject="Mathematics",
            topic="Addition",
            language="en",
        )
        with pytest.raises(HTTPException) as exc_info:
            await svc.generate_lesson_for_learner(req, current_user_id=uuid4())
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Learner not found"

    @pytest.mark.asyncio
    async def test_generate_lesson_for_learner_quota_exceeded(self):
        mock_db = AsyncMock()
        svc = LessonService(mock_db)
        svc._consent_service = AsyncMock()
        svc._learner_repo = AsyncMock()
        mock_learner = MagicMock(
            pseudonym_id="pseudo-1",
            grade=4,
            archetype="visual",
            guardian_id=uuid4(),
        )
        svc._learner_repo.get_by_id.return_value = mock_learner
        svc._guardian_repo = AsyncMock()
        svc._guardian_repo.get_by_id.return_value = MagicMock(subscription_tier="free")
        svc._executive = AsyncMock()
        svc._executive.generate_lesson.side_effect = QuotaExceededError("Quota reached")

        req = LessonRequest(
            learner_id=str(uuid4()),
            subject="Mathematics",
            topic="Addition",
            language="en",
        )
        with patch("app.modules.lessons.service.build_lesson_context_with_runtime_kg", new_callable=AsyncMock) as mock_ctx:
            mock_ctx.return_value = {}
            with pytest.raises(HTTPException) as exc_info:
                await svc.generate_lesson_for_learner(req, current_user_id=uuid4())
            assert exc_info.value.status_code == 429
            assert "Daily AI quota exceeded" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_generate_lesson_for_learner_success_fresh(self):
        mock_db = AsyncMock()
        svc = LessonService(mock_db)
        svc._consent_service = AsyncMock()
        svc._learner_repo = AsyncMock()
        guardian_id = uuid4()
        learner_id = uuid4()
        mock_learner = MagicMock(
            pseudonym_id="pseudo-1",
            grade=4,
            archetype="visual",
            guardian_id=guardian_id,
        )
        svc._learner_repo.get_by_id.return_value = mock_learner
        svc._guardian_repo = AsyncMock()
        svc._guardian_repo.get_by_id.return_value = None  # test fallback tier="free"

        payload = SimpleNamespace(
            title="Addition Basics",
            introduction="Intro to addition",
            main_content="Step 1: add units.",
            worked_example="1 + 2 = 3",
            practice_question="What is 2 + 2?",
            answer="4",
            cultural_hook="Sharing mangos",
            caps_reference="4.M.1.1",
            alignment_confidence=0.95,
            quality_score=0.9,
            trust_label=SimpleNamespace(model_dump=lambda: {"label": "trusted"}),
        )
        svc._executive = AsyncMock()
        svc._executive.generate_lesson.return_value = (payload, False)

        lesson_id = uuid4()
        created_lesson = MagicMock(spec=Lesson)
        created_lesson.id = str(lesson_id)
        created_lesson.learner_id = str(learner_id)
        created_lesson.grade = 4
        created_lesson.subject = "Mathematics"
        created_lesson.topic = "Addition"
        created_lesson.language = "en"
        created_lesson.archetype = "visual"
        created_lesson.content = "rendered"
        created_lesson.caps_reference = "4.M.1.1"
        created_lesson.alignment_confidence = 0.95
        created_lesson.quality_score = 0.9
        created_lesson.trust_label = {"label": "trusted"}
        created_lesson.llm_provider = "groq"
        created_lesson.served_from_cache = False
        created_lesson.completed_at = None
        created_lesson.learner_feedback_score = None
        created_lesson.created_at = datetime.now(timezone.utc)
        created_lesson.title = "Addition Basics"

        svc._lesson_repo = AsyncMock()
        svc._lesson_repo.create.return_value = created_lesson
        svc._audit_service = AsyncMock()

        req = LessonRequest(
            learner_id=str(learner_id),
            subject="Mathematics",
            topic="Addition",
            language="en",
        )

        with patch("app.modules.lessons.service.build_lesson_context_with_runtime_kg", new_callable=AsyncMock) as mock_ctx:
            mock_ctx.return_value = {"knowledge_gaps": []}
            with patch("app.modules.lessons.service.active_provider_label", return_value="groq"):
                resp, from_cache, provider = await svc.generate_lesson_for_learner(req, current_user_id=uuid4())
                assert from_cache is False
                assert provider == "groq"
                assert resp.caps_aligned is True
                assert resp.cache_hit is False
                mock_db.commit.assert_called_once()
                svc._audit_service.lesson_generated.assert_called_once_with(
                    "pseudo-1", "Mathematics", "Addition", "groq"
                )

    @pytest.mark.asyncio
    async def test_generate_lesson_for_learner_success_from_cache(self):
        mock_db = AsyncMock()
        svc = LessonService(mock_db)
        svc._consent_service = AsyncMock()
        svc._learner_repo = AsyncMock()
        guardian_id = uuid4()
        learner_id = uuid4()
        mock_learner = MagicMock(
            pseudonym_id="pseudo-1",
            grade=4,
            archetype="visual",
            guardian_id=guardian_id,
        )
        svc._learner_repo.get_by_id.return_value = mock_learner
        svc._guardian_repo = AsyncMock()
        svc._guardian_repo.get_by_id.return_value = MagicMock(subscription_tier="premium")

        payload = SimpleNamespace(
            title="Cached Addition",
            introduction="Intro",
            main_content="Content",
            worked_example="Ex",
            practice_question="Q",
            answer="A",
            cultural_hook="Hook",
            trust_label=None,
        )
        svc._executive = AsyncMock()
        svc._executive.generate_lesson.return_value = (payload, True)

        lesson_id = uuid4()
        created_lesson = MagicMock(spec=Lesson)
        created_lesson.id = str(lesson_id)
        created_lesson.learner_id = str(learner_id)
        created_lesson.grade = 4
        created_lesson.subject = "Mathematics"
        created_lesson.topic = "Addition"
        created_lesson.language = "en"
        created_lesson.archetype = "visual"
        created_lesson.content = "rendered"
        created_lesson.caps_reference = None
        created_lesson.alignment_confidence = 0.0
        created_lesson.quality_score = 0.0
        created_lesson.trust_label = {}
        created_lesson.llm_provider = "cache"
        created_lesson.served_from_cache = True
        created_lesson.completed_at = None
        created_lesson.learner_feedback_score = None
        created_lesson.created_at = datetime.now(timezone.utc)
        created_lesson.title = "Cached Addition"

        svc._lesson_repo = AsyncMock()
        svc._lesson_repo.create.return_value = created_lesson
        svc._audit_service = AsyncMock()

        req = LessonRequest(
            learner_id=str(learner_id),
            subject="Mathematics",
            topic="Addition",
            language="en",
        )

        with patch("app.modules.lessons.service.build_lesson_context_with_runtime_kg", new_callable=AsyncMock):
            resp, from_cache, provider = await svc.generate_lesson_for_learner(req, current_user_id=uuid4())
            assert from_cache is True
            assert provider == "cache"
            assert resp.cache_hit is True

    @pytest.mark.asyncio
    async def test_complete_lesson(self):
        mock_db = AsyncMock()
        svc = LessonService(mock_db)
        svc._lesson_repo = AsyncMock()
        await svc.complete_lesson("lesson-1")
        svc._lesson_repo.mark_completed.assert_called_once_with("lesson-1")
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_feedback(self):
        mock_db = AsyncMock()
        svc = LessonService(mock_db)
        svc._lesson_repo = AsyncMock()
        await svc.record_feedback("lesson-1", 5)
        svc._lesson_repo.record_feedback.assert_called_once_with("lesson-1", 5)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_lesson_by_id(self):
        mock_db = AsyncMock()
        mock_exec_res = MagicMock()
        mock_exec_res.scalar_one_or_none.return_value = "lesson-mock"
        mock_db.execute.return_value = mock_exec_res

        svc = LessonService(mock_db)
        res = await svc.get_lesson_by_id("l-123")
        assert res == "lesson-mock"

    @pytest.mark.asyncio
    async def test_build_learner_context(self):
        mock_db = AsyncMock()
        mock_exec_res = MagicMock()
        mock_exec_res.all.return_value = [("Fractions", 3), ("Geometry", 2)]
        mock_db.execute.return_value = mock_exec_res

        svc = LessonService(mock_db)
        svc._lesson_repo = AsyncMock()
        svc._lesson_repo.get_recent.return_value = [
            SimpleNamespace(subject="Mathematics", topic="Numbers", completed_at=datetime.now(timezone.utc)),
            SimpleNamespace(subject="Mathematics", topic="Algebra", completed_at=None),
        ]

        ctx = await svc._build_learner_context("learner-1", "Mathematics")
        assert len(ctx["knowledge_gaps"]) == 2
        assert ctx["knowledge_gaps"][0]["topic"] == "Fractions"
        assert len(ctx["recent_lessons"]) == 2
        assert ctx["recent_lessons"][0]["completed"] is True
        assert ctx["recent_lessons"][1]["completed"] is False

    def test_render_lesson_content(self):
        svc = LessonService(AsyncMock())
        payload = SimpleNamespace(
            title="Title",
            introduction="Intro",
            main_content="Main",
            worked_example="Ex",
            practice_question="Q",
            answer="A",
            cultural_hook="Hook",
        )
        content = svc._render_lesson_content(payload)
        assert "# Title" in content
        assert "## Worked Example\nEx" in content
        assert "## Practice\nQ\n\n**Answer:** A" in content
        assert "---\n*Hook*" in content


# ---------------------------------------------------------------------------
# Target 2: app/modules/lessons/llm_gateway.py
# ---------------------------------------------------------------------------
from app.core.exceptions import LLMError
from app.modules.lessons.llm_gateway import LLMGateway, LLMResponse


class TestLLMGateway:
    @pytest.mark.asyncio
    async def test_generate_success(self):
        gateway = LLMGateway()
        mock_comp = MagicMock(
            content='{"lesson": "content"}',
            provider="groq",
            model="llama-3.3-70b",
            prompt_tokens=100,
            completion_tokens=200,
        )
        with patch("app.modules.lessons.llm_gateway.JsonCompletionGateway") as mock_cls:
            mock_instance = AsyncMock()
            mock_instance.complete.return_value = mock_comp
            mock_cls.return_value = mock_instance

            resp = await gateway.generate(prompt="Explain division", system="Custom tutor")
            assert isinstance(resp, LLMResponse)
            assert resp.content == '{"lesson": "content"}'
            assert resp.provider == "groq"
            assert resp.prompt_tokens == 100
            assert resp.completion_tokens == 200

    @pytest.mark.asyncio
    async def test_generate_failure(self):
        gateway = LLMGateway()
        with patch("app.modules.lessons.llm_gateway.JsonCompletionGateway") as mock_cls:
            mock_instance = AsyncMock()
            mock_instance.complete.side_effect = RuntimeError("All providers unavailable")
            mock_cls.return_value = mock_instance

            with pytest.raises(LLMError, match="Lesson generation is temporarily unavailable"):
                await gateway.generate(prompt="Explain division")

    @pytest.mark.asyncio
    async def test_call_groq_missing_key(self):
        gateway = LLMGateway()
        with patch("app.modules.lessons.llm_gateway.get_settings") as mock_settings:
            mock_settings.return_value = SimpleNamespace(GROQ_API_KEY=None)
            with pytest.raises(LLMError, match="Groq API key not configured"):
                await gateway._call_groq("prompt", system="", max_tokens=100)

    @pytest.mark.asyncio
    async def test_call_groq_success(self):
        gateway = LLMGateway()
        with patch("app.modules.lessons.llm_gateway.get_settings") as mock_settings:
            mock_settings.return_value = SimpleNamespace(
                GROQ_API_KEY="gsk_test123",
                GROQ_MODEL="llama3-70b-8192",
                LLM_TIMEOUT_SECONDS=30,
            )
            mock_groq_client = MagicMock()
            mock_comp = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Groq generated lesson"))],
                usage=MagicMock(prompt_tokens=50, completion_tokens=80),
            )
            mock_groq_client.chat.completions.create = AsyncMock(return_value=mock_comp)

            with patch("groq.AsyncGroq", return_value=mock_groq_client):
                resp = await gateway._call_groq("prompt", system="You are tutor", max_tokens=100)
                assert resp.content == "Groq generated lesson"
                assert resp.provider == "groq"
                assert resp.prompt_tokens == 50
                assert resp.completion_tokens == 80

    @pytest.mark.asyncio
    async def test_call_anthropic_missing_key(self):
        gateway = LLMGateway()
        with patch("app.modules.lessons.llm_gateway.get_settings") as mock_settings:
            mock_settings.return_value = SimpleNamespace(ANTHROPIC_API_KEY=None)
            with pytest.raises(LLMError, match="Anthropic API key not configured"):
                await gateway._call_anthropic("prompt", system="", max_tokens=100)

    @pytest.mark.asyncio
    async def test_call_anthropic_success(self):
        gateway = LLMGateway()
        with patch("app.modules.lessons.llm_gateway.get_settings") as mock_settings:
            mock_settings.return_value = SimpleNamespace(
                ANTHROPIC_API_KEY="sk-ant-test123",
                ANTHROPIC_MODEL="claude-3-5-sonnet",
            )
            mock_anthropic_client = MagicMock()
            mock_msg = MagicMock(
                content=[MagicMock(text="Claude lesson content")],
                usage=MagicMock(input_tokens=40, output_tokens=90),
            )
            mock_anthropic_client.messages.create = AsyncMock(return_value=mock_msg)

            with patch("anthropic.AsyncAnthropic", return_value=mock_anthropic_client):
                resp = await gateway._call_anthropic("prompt", system="", max_tokens=200)
                assert resp.content == "Claude lesson content"
                assert resp.provider == "anthropic"
                assert resp.prompt_tokens == 40
                assert resp.completion_tokens == 90


# ---------------------------------------------------------------------------
# Target 3: app/modules/lessons/lesson_coverage_router.py
# ---------------------------------------------------------------------------
from app.modules.lessons.lesson_coverage_router import (
    CapsRefCoverage,
    CoverageResponse,
    CoverageSummary,
    QualityScoreDistribution,
    _topic_rows,
    compute_coverage_status,
    compute_quality_distribution,
    get_lesson_coverage,
)


class TestLessonCoverageRouter:
    def test_compute_quality_distribution_empty(self):
        dist = compute_quality_distribution([])
        assert dist.count == 0
        assert dist.below_threshold == 0
        assert dist.mean is None

    def test_compute_quality_distribution_populated(self):
        scores = [0.5, 0.6, 0.7, 0.8, 0.9]
        dist = compute_quality_distribution(scores)
        assert dist.count == 5
        assert dist.min == 0.5
        assert dist.max == 0.9
        assert dist.below_threshold == 2  # 0.5 and 0.6
        assert dist.mean == 0.7

    def test_compute_coverage_status(self):
        assert compute_coverage_status(0, target=0) == "uncovered"
        assert compute_coverage_status(0, target=5) == "red"
        assert compute_coverage_status(3, target=5) == "amber"
        assert compute_coverage_status(8, target=5) == "green"
        assert compute_coverage_status(10, target=5) == "green"
        # total_count override
        assert compute_coverage_status(0, target=5, total_count=0) == "uncovered"

    def test_topic_rows_generation(self):
        mock_caps = MagicMock()
        mock_subtopic = MagicMock(caps_ref="4.M.1.1.1", subtopic="Counting")
        mock_topic = MagicMock(caps_ref="4.M.1.1", topic="Numbers", subtopics=[mock_subtopic])
        mock_caps.list_topics.return_value = [mock_topic]
        mock_caps.summary.return_value = {"scopes": ["Mathematics Grade 4"]}

        # Subject specified
        rows_math = _topic_rows(mock_caps, grade=4, subject="Mathematics")
        assert len(rows_math) == 2  # 1 topic + 1 subtopic
        assert rows_math[0]["caps_ref"] == "4.M.1.1"
        assert rows_math[0]["subtopic"] is None
        assert rows_math[1]["caps_ref"] == "4.M.1.1.1"
        assert rows_math[1]["subtopic"] == "Counting"

        # Subject None -> fallback to scopes[0]
        rows_none = _topic_rows(mock_caps, grade=4, subject=None)
        assert rows_none[0]["subject"] == "Mathematics Grade 4"

    @pytest.mark.asyncio
    async def test_get_lesson_coverage_endpoint(self):
        mock_service = AsyncMock()
        mock_caps_service = MagicMock()
        mock_subtopic = MagicMock(caps_ref="4.M.1.1.1", subtopic="Counting")
        mock_topic = MagicMock(caps_ref="4.M.1.1", topic="Numbers", subtopics=[mock_subtopic])
        mock_caps_service.list_topics.return_value = [mock_topic]
        mock_caps_service.summary.return_value = {"scopes": ["Mathematics"]}

        # Return mock lessons for list_by_caps_ref
        mock_lesson_app = SimpleNamespace(
            review_status="approved",
            answer_key_verified=True,
            quality_score=0.85,
            generation_latency_ms=120.0,
            provider="groq",
            llm_provider=None,
        )
        mock_lesson_gen = SimpleNamespace(
            review_status="ai_generated",
            answer_key_verified=False,
            quality_score=0.65,
            generation_latency_ms=150.0,
            provider=None,
            llm_provider="anthropic",
        )
        mock_lesson_rej = SimpleNamespace(
            review_status="rejected",
            answer_key_verified=False,
            quality_score=None,
            generation_latency_ms=None,
            provider=None,
            llm_provider=None,
        )
        mock_service.list_by_caps_ref.return_value = [mock_lesson_app, mock_lesson_gen, mock_lesson_rej]

        with patch("app.modules.lessons.lesson_coverage_router.ContentScopeRegistry") as mock_reg_cls:
            mock_reg = MagicMock()
            mock_reg.get_coverage_target.return_value = 5
            mock_reg_cls.return_value = mock_reg

            resp = await get_lesson_coverage(
                grade=4,
                subject="Mathematics",
                scope_id="default",
                service=mock_service,
                caps_service=mock_caps_service,
            )

            assert isinstance(resp, CoverageResponse)
            assert resp.summary.total_caps_refs_in_scope == 2
            assert resp.summary.total_approved_lessons == 2  # 1 approved per ref * 2 refs
            assert resp.summary.overall_review_queue_depth == 2
            assert len(resp.per_caps_ref) == 2
            assert resp.per_caps_ref[0].provider_breakdown == {"groq": 1, "anthropic": 1, "unknown": 1}

    @pytest.mark.asyncio
    async def test_get_lesson_coverage_endpoint_lookup_error(self):
        mock_service = AsyncMock()
        mock_caps_service = MagicMock()
        mock_topic = MagicMock(caps_ref="4.M.1.1", topic="Numbers", subtopics=[])
        mock_caps_service.list_topics.return_value = [mock_topic]
        mock_caps_service.summary.return_value = {"scopes": ["Mathematics"]}
        mock_service.list_by_caps_ref.return_value = []

        with patch("app.modules.lessons.lesson_coverage_router.ContentScopeRegistry") as mock_reg_cls:
            mock_reg = MagicMock()
            mock_reg.get_coverage_target.side_effect = LookupError("Not registered")
            mock_reg_cls.return_value = mock_reg

            resp = await get_lesson_coverage(
                grade=4,
                subject="Mathematics",
                scope_id="missing_scope",
                service=mock_service,
                caps_service=mock_caps_service,
            )

            assert resp.summary.total_caps_refs_in_scope == 1
            assert resp.summary.uncovered_refs == 1


# ---------------------------------------------------------------------------
# Target 4: app/modules/lessons/lesson_review_router.py
# ---------------------------------------------------------------------------
from app.domain.lesson import ReviewStatus, SafetyClassification
from app.modules.lessons.lesson_review_router import (
    CurrentUser,
    LessonReviewRequest,
    QueuedLessonSummary,
    ReviewActionResponse,
    ReviewDecision,
    ReviewQueueResponse,
    UserRole,
    _coerce_user,
    compute_auto_queue_reasons,
    get_review_queue,
    require_reviewer,
    review_lesson,
    should_auto_queue,
)


class TestLessonReviewRouter:
    def test_coerce_user(self):
        uid = uuid4()
        u1 = _coerce_user({"sub": str(uid), "role": "admin", "email": "admin@eduboost.za"})
        assert u1.user_id == uid
        assert u1.role == UserRole.ADMIN
        assert u1.email == "admin@eduboost.za"

        u2 = _coerce_user({"user_id": str(uid), "role": "REVIEWER"})
        assert u2.role == UserRole.REVIEWER

        u3 = _coerce_user({"id": str(uid)})
        assert u3.role == UserRole.LEARNER

    def test_compute_auto_queue_reasons_and_should_auto_queue(self):
        # All conditions triggered
        reasons1 = compute_auto_queue_reasons(
            quality_score=0.6,
            answer_key_verified=False,
            safety_classification="requires_review",
        )
        assert len(reasons1) == 3
        assert should_auto_queue(0.6, False, "requires_review") is True

        # None triggered
        reasons2 = compute_auto_queue_reasons(
            quality_score=0.85,
            answer_key_verified=True,
            safety_classification=SafetyClassification.SAFE,
        )
        assert len(reasons2) == 0
        assert should_auto_queue(0.85, True, SafetyClassification.SAFE) is False

        # quality_score None
        reasons3 = compute_auto_queue_reasons(
            quality_score=None,
            answer_key_verified=True,
            safety_classification=SafetyClassification.SAFE,
        )
        assert len(reasons3) == 1
        assert "Quality score N/A" in reasons3[0]

    @pytest.mark.asyncio
    async def test_require_reviewer(self):
        # Allowed roles
        u_rev = await require_reviewer({"sub": str(uuid4()), "role": "reviewer"})
        assert u_rev.role == UserRole.REVIEWER
        u_adm = await require_reviewer({"sub": str(uuid4()), "role": "admin"})
        assert u_adm.role == UserRole.ADMIN

        # Forbidden role
        with pytest.raises(HTTPException) as exc_info:
            await require_reviewer({"sub": str(uuid4()), "role": "learner"})
        assert exc_info.value.status_code == 403
        assert "Reviewer or admin role required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_review_queue(self):
        mock_service = AsyncMock()
        lesson_id = uuid4()
        now = datetime.now(timezone.utc)
        mock_lesson = SimpleNamespace(
            id=lesson_id,
            caps_ref="4.M.1.1",
            grade=4,
            subject="Mathematics",
            topic="Numbers",
            subtopic="Place Value",
            quality_score=0.65,
            answer_key_verified=False,
            safety_classification="requires_review",
            review_status="ai_generated",
            created_at=now,
            provider="groq",
            prompt_template_version="v1",
        )
        mock_service.list_pending_review.return_value = [mock_lesson]

        reviewer_user = CurrentUser(user_id=uuid4(), role=UserRole.REVIEWER)
        resp = await get_review_queue(
            grade=4,
            subject="Mathematics",
            caps_ref="4.M.1.1",
            limit=10,
            offset=0,
            _=reviewer_user,
            service=mock_service,
        )
        assert isinstance(resp, ReviewQueueResponse)
        assert resp.total_pending == 1
        assert resp.lessons[0].lesson_id == str(lesson_id)
        assert resp.lessons[0].quality_score == 0.65
        assert len(resp.lessons[0].auto_queue_reason) >= 1

    @pytest.mark.asyncio
    async def test_review_lesson_success(self):
        mock_service = AsyncMock()
        lesson_id = uuid4()
        reviewer_id = uuid4()
        now = datetime.now(timezone.utc)
        mock_updated = SimpleNamespace(
            id=lesson_id,
            review_status="approved",
            reviewed_at=now,
        )
        mock_service.review_lesson.return_value = mock_updated

        user = CurrentUser(user_id=reviewer_id, role=UserRole.REVIEWER)
        req = LessonReviewRequest(decision=ReviewDecision.APPROVED, reviewer_notes="Looks good")

        resp = await review_lesson(
            lesson_id=lesson_id,
            body=req,
            current_user=user,
            service=mock_service,
        )
        assert isinstance(resp, ReviewActionResponse)
        assert resp.lesson_id == str(lesson_id)
        assert resp.review_status == ReviewStatus.APPROVED
        assert resp.reviewer_id == str(reviewer_id)
        assert "approved" in resp.message

    @pytest.mark.asyncio
    async def test_review_lesson_not_found(self):
        mock_service = AsyncMock()
        mock_service.review_lesson.return_value = None

        lesson_id = uuid4()
        user = CurrentUser(user_id=uuid4(), role=UserRole.REVIEWER)
        req = LessonReviewRequest(decision=ReviewDecision.REJECTED)

        with pytest.raises(HTTPException) as exc_info:
            await review_lesson(
                lesson_id=lesson_id,
                body=req,
                current_user=user,
                service=mock_service,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Lesson not found"
