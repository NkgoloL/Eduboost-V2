"""Batch 225 — app/services/learner_tutor.py comprehensive branch coverage expansion.

Tests:
- create_session: learner/lesson missing or mismatched learner_id (404), existing active session return, IntegrityError concurrent race recovery
- get_session: 404 on missing, found return
- cancel_session: already cancelled idempotency, active session transition
- ask:
  - session 404
  - idempotency with prior assistant message (matched hash return vs 409 mismatch)
  - session status not active (409)
  - lesson or learner missing (409)
  - lesson context changed hash mismatch (409)
  - blocked input (high vs medium severity escalation)
  - durable budget exhausted (AIBudgetExceededError fallback)
  - ProviderContentPolicyError (cancels op, high severity escalation)
  - AllProvidersFailedError & general Provider error (cancels op, low severity fallback without escalation)
  - output validation failure (low_quality medium severity vs dangerous high severity)
  - successful answer generation, telemetry, metrics, and budget accounting
- Helper functions: session_language, serialize_session
"""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.models import KnowledgeGap, LearnerProfile, Lesson
from app.models.tutor import TutorMessage, TutorSession
from app.services.ai_operations import AIBudgetExceededError
from app.services.learner_tutor import (
    LearnerTutorService,
    _context_hash,
    serialize_session,
    session_language,
)
from app.services.llm_provider import (
    AllProvidersFailedError,
    GenerationResult,
    ProviderContentPolicyError,
    TokenUsage,
)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_router():
    router = MagicMock()
    router.generate = AsyncMock()
    return router


@pytest.fixture
def mock_budget():
    budget = MagicMock()
    budget.assert_budget = AsyncMock()
    budget.record_usage = AsyncMock()
    return budget


@pytest.fixture
def service(mock_db, mock_router, mock_budget):
    return LearnerTutorService(
        db=mock_db,
        provider_router=mock_router,
        budget_guardrails=mock_budget,
    )


def test_learner_tutor_default_budget(mock_db, mock_router):
    with patch("app.services.learner_tutor.get_redis", return_value=None), \
         patch("app.services.learner_tutor.BudgetGuardrails.from_settings") as mock_bg:
        mock_bg.return_value = MagicMock()
        svc = LearnerTutorService(db=mock_db, provider_router=mock_router)
        assert svc.budget is not None
        mock_bg.assert_called_once()



# ---------------------------------------------------------------------------
# Session Creation, Retrieval, Cancellation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_session_learner_lesson_checks(service, mock_db):
    # 1. Missing learner or lesson or mismatched learner_id raises 404
    mock_db.get.side_effect = [None, MagicMock()]
    with pytest.raises(HTTPException) as exc:
        await service.create_session(learner_id="l-1", lesson_id="les-1", actor_id="a-1", language="en")
    assert exc.value.status_code == 404

    # 2. Mismatched learner_id on lesson raises 404
    mock_learner = MagicMock(spec=LearnerProfile, id="l-1")
    mock_lesson_diff = MagicMock(spec=Lesson, id="les-1", learner_id="l-other")
    mock_db.get.side_effect = [mock_learner, mock_lesson_diff]
    with pytest.raises(HTTPException) as exc:
        await service.create_session(learner_id="l-1", lesson_id="les-1", actor_id="a-1", language="en")
    assert exc.value.status_code == 404

    # 3. Existing active session returns early
    mock_lesson = MagicMock(spec=Lesson, id="les-1", learner_id="l-1", subject="Math", topic="Fractions", content="text")
    mock_existing = MagicMock(spec=TutorSession)
    mock_db.get.side_effect = [mock_learner, mock_lesson]
    mock_db.scalar.return_value = mock_existing

    res_exist = await service.create_session(learner_id="l-1", lesson_id="les-1", actor_id="a-1", language="en")
    assert res_exist == mock_existing

    # 4. IntegrityError on commit retrieves concurrent session
    mock_db.get.side_effect = [mock_learner, mock_lesson]
    mock_db.scalar.side_effect = [None, mock_existing]
    mock_db.commit.side_effect = [IntegrityError("stmt", "params", Exception("unique"))]

    res_concurrent = await service.create_session(learner_id="l-1", lesson_id="les-1", actor_id="a-1", language="en")
    assert res_concurrent == mock_existing


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_and_cancel_session(service, mock_db):
    session_id = uuid.uuid4()

    # get_session 404
    mock_db.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        await service.get_session(session_id)
    assert exc.value.status_code == 404

    # cancel_session active -> cancelled
    mock_session = MagicMock(spec=TutorSession, status="active")
    mock_db.get.return_value = mock_session
    cancelled = await service.cancel_session(session_id)
    assert cancelled.status == "cancelled"

    # cancel_session already cancelled returns idempotently
    mock_session.status = "cancelled"
    assert await service.cancel_session(session_id) == mock_session


# ---------------------------------------------------------------------------
# ask() Idempotency & Validation Pre-conditions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_ask_idempotency_and_preconditions(service, mock_db):
    session_id = uuid.uuid4()

    # 1. Session not found -> 404
    mock_db.scalar.return_value = None
    with pytest.raises(HTTPException) as exc:
        await service.ask(session_id=session_id, question="What is 1+1?", client_message_id="msg-1")
    assert exc.value.status_code == 404

    # 2. Idempotency: prior assistant message with same hash -> return
    mock_session = MagicMock(spec=TutorSession, session_id=session_id, status="active", context_hash="hash-123")
    mock_prior_asst = MagicMock(spec=TutorMessage, provider="anthropic", safety_status="safe")
    mock_learner_msg = MagicMock(spec=TutorMessage, content_hash="hash_question")

    with patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep:
        mock_prep.return_value = MagicMock(content_hash="hash_question")
        mock_db.scalar.side_effect = [
            mock_session,      # session
            mock_prior_asst,   # prior assistant
            mock_learner_msg,  # prior learner
        ]
        res = await service.ask(session_id=session_id, question="What is 1+1?", client_message_id="msg-1")
        assert res["assistant"] == mock_prior_asst
        assert res["fallback"] is False

    # 3. Idempotency mismatch -> 409
    with patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep:
        mock_prep.return_value = MagicMock(content_hash="hash_different")
        mock_db.scalar.side_effect = [
            mock_session,
            mock_prior_asst,
            mock_learner_msg,
        ]
        with pytest.raises(HTTPException) as exc:
            await service.ask(session_id=session_id, question="Different?", client_message_id="msg-1")
        assert exc.value.status_code == 409


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ask_status_and_context_changed(service, mock_db):
    session_id = uuid.uuid4()
    mock_session = MagicMock(spec=TutorSession, session_id=session_id, status="cancelled", context_hash="hash-123")

    with patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep:
        mock_prep.return_value = MagicMock(content_hash="hash_1", blocked_reason=None)
        mock_db.scalar.side_effect = [mock_session, None]  # session, prior=None
        with pytest.raises(HTTPException) as exc:
            await service.ask(session_id=session_id, question="Hi", client_message_id="msg-2")
        assert exc.value.status_code == 409
        assert "not active" in exc.value.detail

    # Lesson context changed -> 409
    mock_session.status = "active"
    mock_lesson = MagicMock(spec=Lesson, id="les-1", subject="Math", topic="Fractions", content="changed content")
    mock_learner = MagicMock(spec=LearnerProfile, id="l-1")
    mock_db.get.side_effect = [mock_lesson, mock_learner]
    mock_db.scalar.side_effect = [mock_session, None]

    with patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep:
        mock_prep.return_value = MagicMock(content_hash="hash_1", blocked_reason=None)
        with pytest.raises(HTTPException) as exc:
            await service.ask(session_id=session_id, question="Hi", client_message_id="msg-2")
        assert exc.value.status_code == 409
        assert "Lesson changed" in exc.value.detail


# ---------------------------------------------------------------------------
# ask() Safety, Fallbacks & Success Generation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_ask_blocked_input_escalation(service, mock_db):
    session_id = uuid.uuid4()
    mock_lesson = MagicMock(spec=Lesson, id="les-1", subject="Math", topic="Fractions", content="text")
    c_hash = _context_hash(mock_lesson)
    mock_session = MagicMock(
        spec=TutorSession,
        session_id=session_id,
        status="active",
        language="en",
        lesson_id="les-1",
        learner_id="l-1",
        context_hash=c_hash,
        escalation_count=0,
        message_count=0,
    )
    mock_learner = MagicMock(spec=LearnerProfile, id="l-1", guardian_id="g-1")

    mock_db.scalar.side_effect = [mock_session, None]
    mock_db.get.side_effect = [mock_lesson, mock_learner]

    with patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep:
        mock_prep.return_value = MagicMock(
            text="forbidden query",
            content_hash="hash_blocked",
            blocked_reason="self_harm",
            pii_redacted=False,
        )
        res = await service.ask(session_id=session_id, question="forbidden", client_message_id="msg-block")
        assert res["fallback"] is True
        assert res["escalation"] is True
        assert mock_session.status == "escalated"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ask_budget_exhausted_fallback(service, mock_db):
    session_id = uuid.uuid4()
    mock_lesson = MagicMock(spec=Lesson, id="les-1", subject="Math", topic="Fractions", content="text")
    c_hash = _context_hash(mock_lesson)
    mock_session = MagicMock(
        spec=TutorSession,
        session_id=session_id,
        status="active",
        language="en",
        lesson_id="les-1",
        learner_id="l-1",
        context_hash=c_hash,
        escalation_count=0,
        message_count=0,
    )
    mock_learner = MagicMock(spec=LearnerProfile, id="l-1", guardian_id="g-1")

    mock_db.scalar.side_effect = [mock_session, None]
    mock_db.get.side_effect = [mock_lesson, mock_learner]

    service.ai_operations.reserve = AsyncMock(
        side_effect=AIBudgetExceededError(
            scope="user",
            used=400,
            reserved=100,
            requested=700,
            limit=500,
        )
    )

    with patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep:
        mock_prep.return_value = MagicMock(
            text="valid question",
            content_hash="hash_valid",
            blocked_reason=None,
            pii_redacted=False,
        )
        res = await service.ask(session_id=session_id, question="valid", client_message_id="msg-budget")
        assert res["fallback"] is True
        assert res["escalation"] is False


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ask_provider_content_policy_and_all_providers_failed(service, mock_db, mock_router):
    session_id = uuid.uuid4()
    mock_lesson = MagicMock(spec=Lesson, id="les-1", subject="Math", topic="Fractions", content="text", language="en")
    c_hash = _context_hash(mock_lesson)
    mock_learner = MagicMock(spec=LearnerProfile, id="l-1", guardian_id="g-1", grade=4)

    service.ai_operations.reserve = AsyncMock()
    service.ai_operations.cancel = AsyncMock()

    # Mock gaps
    res_gaps = MagicMock()
    res_gaps.all.return_value = [("Fractions", 0.5)]
    mock_db.execute.return_value = res_gaps

    # 1. ProviderContentPolicyError
    mock_session1 = MagicMock(
        spec=TutorSession,
        session_id=session_id,
        status="active",
        language="en",
        lesson_id="les-1",
        learner_id="l-1",
        context_hash=c_hash,
        escalation_count=0,
        message_count=0,
    )
    mock_db.scalar.side_effect = [mock_session1, None]
    mock_db.get.side_effect = [mock_lesson, mock_learner]
    mock_router.generate = AsyncMock(side_effect=ProviderContentPolicyError("Policy violation", "anthropic"))

    with patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep:
        mock_prep.return_value = MagicMock(text="question", content_hash="h1", blocked_reason=None, pii_redacted=False)
        res_pol = await service.ask(session_id=session_id, question="q", client_message_id="msg-pol")
        assert res_pol["fallback"] is True
        assert res_pol["escalation"] is True
        service.ai_operations.cancel.assert_called_with(f"tutor:{session_id}:msg-pol", "provider_policy")

    # 2. AllProvidersFailedError
    mock_session2 = MagicMock(
        spec=TutorSession,
        session_id=session_id,
        status="active",
        language="en",
        lesson_id="les-1",
        learner_id="l-1",
        context_hash=c_hash,
        escalation_count=0,
        message_count=0,
    )
    mock_db.scalar.side_effect = [mock_session2, None]
    mock_db.get.side_effect = [mock_lesson, mock_learner]
    mock_router.generate = AsyncMock(side_effect=AllProvidersFailedError("All failed"))

    with patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep:
        mock_prep.return_value = MagicMock(text="question", content_hash="h1", blocked_reason=None, pii_redacted=False)
        res_fail = await service.ask(session_id=session_id, question="q", client_message_id="msg-fail")
        assert res_fail["fallback"] is True
        assert res_fail["escalation"] is False
        service.ai_operations.cancel.assert_called_with(f"tutor:{session_id}:msg-fail", "providers_failed")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ask_success_generation_flow(service, mock_db, mock_router):
    session_id = uuid.uuid4()
    mock_lesson = MagicMock(spec=Lesson, id="les-1", subject="Math", topic="Fractions", content="text", language="en")
    c_hash = _context_hash(mock_lesson)
    mock_session = MagicMock(
        spec=TutorSession,
        session_id=session_id,
        status="active",
        language="en",
        lesson_id="les-1",
        learner_id="l-1",
        context_hash=c_hash,
        escalation_count=0,
        message_count=0,
    )
    mock_learner = MagicMock(spec=LearnerProfile, id="l-1", guardian_id="g-1", grade=4)

    mock_db.scalar.side_effect = [mock_session, None]
    mock_db.get.side_effect = [mock_lesson, mock_learner]

    service.ai_operations.reserve = AsyncMock()
    service.ai_operations.finalize = AsyncMock()

    res_gaps = MagicMock()
    res_gaps.all.return_value = []
    mock_db.execute.return_value = res_gaps

    gen_res = GenerationResult(
        text="A fraction is a part of a whole number!",
        provider="anthropic",
        model="claude-sonnet-4",
        usage=TokenUsage(prompt_tokens=50, completion_tokens=20, total_tokens=70),
        latency_ms=120.0,
    )
    mock_router.generate = AsyncMock(return_value=gen_res)

    with (
        patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep,
        patch("app.services.learner_tutor.validate_tutor_output") as mock_val,
    ):
        mock_prep.return_value = MagicMock(text="What is a fraction?", content_hash="h1", blocked_reason=None, pii_redacted=False)
        mock_val.return_value = MagicMock(
            text="A fraction is a part of a whole number!",
            blocked_reason=None,
            pii_redacted=False,
            quality_score=0.95,
        )

        res = await service.ask(session_id=session_id, question="What is a fraction?", client_message_id="msg-success")
        assert res["fallback"] is False
        assert res["escalation"] is False
        assert res["assistant"].content == "A fraction is a part of a whole number!"
        service.ai_operations.finalize.assert_called_once()


# ---------------------------------------------------------------------------
# Helpers: session_language, serialize_session
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_learner_tutor_helpers():
    assert session_language("zu") == "zu"
    assert session_language(None) == "en"

    mock_sess = MagicMock(
        spec=TutorSession,
        session_id=uuid.uuid4(),
        learner_id="l-1",
        lesson_id="les-1",
        language="en",
        status="active",
        message_count=2,
        escalation_count=0,
        created_at=None,
        last_activity_at=None,
    )
    mock_msg = MagicMock(
        spec=TutorMessage,
        message_id=uuid.uuid4(),
        role="assistant",
        content="Hint",
        safety_status="safe",
        quality_score=0.9,
        provider="anthropic",
        created_at=None,
    )
    data = serialize_session(mock_sess, [mock_msg])
    assert data["status"] == "active"
    assert len(data["messages"]) == 1
    assert data["messages"][0]["content"] == "Hint"


# ---------------------------------------------------------------------------
# Extra edge cases & remaining branch coverage
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_session_success_commit_and_integrity_error_reraise(service, mock_db):
    mock_learner = MagicMock(spec=LearnerProfile, id="l-1")
    mock_lesson = MagicMock(spec=Lesson, id="les-1", learner_id="l-1", subject="Math", topic="Fractions", content="text")

    # 1. Normal success creation (commit & refresh)
    mock_db.get.side_effect = [mock_learner, mock_lesson]
    mock_db.scalar.return_value = None
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    sess = await service.create_session(learner_id="l-1", lesson_id="les-1", actor_id="a-1", language="en")
    assert sess is not None
    assert sess.learner_id == "l-1"
    mock_db.refresh.assert_called_once()

    # 2. IntegrityError where existing is None -> reraises IntegrityError
    mock_db.get.side_effect = [mock_learner, mock_lesson]
    mock_db.scalar.side_effect = [None, None]
    mock_db.commit.side_effect = IntegrityError("stmt", "params", Exception("unique"))
    mock_db.rollback = AsyncMock()

    with pytest.raises(IntegrityError):
        await service.create_session(learner_id="l-1", lesson_id="les-1", actor_id="a-1", language="en")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ask_context_unavailable_and_budget_exceptions(service, mock_db, mock_router, mock_budget):
    session_id = uuid.uuid4()
    mock_session = MagicMock(
        spec=TutorSession,
        session_id=session_id,
        status="active",
        language="en",
        lesson_id="les-1",
        learner_id="l-1",
        context_hash="hash",
    )

    # 1. Lesson or learner is None -> 409 Context no longer available
    mock_db.scalar.side_effect = [mock_session, None]
    mock_db.get.side_effect = [None, None]

    with patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep:
        mock_prep.return_value = MagicMock(text="q", content_hash="h1", blocked_reason=None, pii_redacted=False)
        with pytest.raises(HTTPException) as exc:
            await service.ask(session_id=session_id, question="q", client_message_id="m-1")
        assert exc.value.status_code == 409
        assert "no longer available" in exc.value.detail

    # 2. Budget exceptions swallowed (assert_budget and record_usage)
    mock_lesson = MagicMock(spec=Lesson, id="les-1", subject="Math", topic="Fractions", content="text", language="en")
    c_hash = _context_hash(mock_lesson)
    mock_session.context_hash = c_hash
    mock_learner = MagicMock(spec=LearnerProfile, id="l-1", guardian_id="g-1", grade=4)

    mock_db.scalar.side_effect = [mock_session, None]
    mock_db.get.side_effect = [mock_lesson, mock_learner]
    mock_budget.assert_budget.side_effect = RuntimeError("Redis down")
    mock_budget.record_usage.side_effect = RuntimeError("Redis down")

    service.ai_operations.reserve = AsyncMock()
    service.ai_operations.finalize = AsyncMock()

    res_gaps = MagicMock()
    res_gaps.all.return_value = []
    mock_db.execute.return_value = res_gaps

    gen_res = GenerationResult(
        text="Helpful hint",
        provider="anthropic",
        model="claude-sonnet-4",
        usage=TokenUsage(prompt_tokens=50, completion_tokens=20, total_tokens=70),
        latency_ms=120.0,
    )
    mock_router.generate = AsyncMock(return_value=gen_res)

    with (
        patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep,
        patch("app.services.learner_tutor.validate_tutor_output") as mock_val,
    ):
        mock_prep.return_value = MagicMock(text="q", content_hash="h1", blocked_reason=None, pii_redacted=False)
        mock_val.return_value = MagicMock(text="Helpful hint", blocked_reason=None, pii_redacted=False, quality_score=0.9)
        res = await service.ask(session_id=session_id, question="q", client_message_id="m-budget-err")
        assert res["fallback"] is False
        assert res["assistant"].content == "Helpful hint"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ask_generic_provider_error_and_output_validation_rejection(service, mock_db, mock_router):
    session_id = uuid.uuid4()
    mock_lesson = MagicMock(spec=Lesson, id="les-1", subject="Math", topic="Fractions", content="text", language="en")
    c_hash = _context_hash(mock_lesson)
    mock_learner = MagicMock(spec=LearnerProfile, id="l-1", guardian_id="g-1", grade=4)

    service.ai_operations.reserve = AsyncMock()
    service.ai_operations.cancel = AsyncMock()

    res_gaps = MagicMock()
    res_gaps.all.return_value = []
    mock_db.execute.return_value = res_gaps

    # 1. Generic provider Exception
    mock_session1 = MagicMock(
        spec=TutorSession,
        session_id=session_id,
        status="active",
        language="en",
        lesson_id="les-1",
        learner_id="l-1",
        context_hash=c_hash,
        escalation_count=0,
        message_count=0,
    )
    mock_db.scalar.side_effect = [mock_session1, None]
    mock_db.get.side_effect = [mock_lesson, mock_learner]
    mock_router.generate = AsyncMock(side_effect=RuntimeError("Connection reset by peer"))

    with patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep:
        mock_prep.return_value = MagicMock(text="question", content_hash="h1", blocked_reason=None, pii_redacted=False)
        res_err = await service.ask(session_id=session_id, question="q", client_message_id="msg-err")
        assert res_err["fallback"] is True
        assert res_err["escalation"] is False
        service.ai_operations.cancel.assert_called_with(f"tutor:{session_id}:msg-err", "provider_error")

    # 2. Output validation blocked: low_quality (medium severity)
    mock_session2 = MagicMock(
        spec=TutorSession,
        session_id=session_id,
        status="active",
        language="en",
        lesson_id="les-1",
        learner_id="l-1",
        context_hash=c_hash,
        escalation_count=0,
        message_count=0,
    )
    mock_db.scalar.side_effect = [mock_session2, None]
    mock_db.get.side_effect = [mock_lesson, mock_learner]
    mock_router.generate = AsyncMock(return_value=GenerationResult(
        text="Bad answer",
        provider="anthropic",
        model="claude-sonnet-4",
        usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        latency_ms=50.0,
    ))

    with (
        patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep,
        patch("app.services.learner_tutor.validate_tutor_output") as mock_val,
    ):
        mock_prep.return_value = MagicMock(text="question", content_hash="h1", blocked_reason=None, pii_redacted=False)
        mock_val.return_value = MagicMock(text="Bad answer", blocked_reason="low_quality", pii_redacted=False, quality_score=0.2)
        res_low = await service.ask(session_id=session_id, question="q", client_message_id="msg-low")
        assert res_low["fallback"] is True
        assert res_low["escalation"] is True
        assert mock_session2.status == "active"  # medium severity does not set status to 'escalated'
        service.ai_operations.cancel.assert_called_with(f"tutor:{session_id}:msg-low", "output_low_quality")

    # 3. Output validation blocked: dangerous content (high severity -> session status escalated)
    mock_session3 = MagicMock(
        spec=TutorSession,
        session_id=session_id,
        status="active",
        language="en",
        lesson_id="les-1",
        learner_id="l-1",
        context_hash=c_hash,
        escalation_count=0,
        message_count=0,
    )
    mock_db.scalar.side_effect = [mock_session3, None]
    mock_db.get.side_effect = [mock_lesson, mock_learner]
    mock_router.generate = AsyncMock(return_value=GenerationResult(
        text="Dangerous answer",
        provider="anthropic",
        model="claude-sonnet-4",
        usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        latency_ms=50.0,
    ))

    with (
        patch("app.services.learner_tutor.prepare_tutor_input") as mock_prep,
        patch("app.services.learner_tutor.validate_tutor_output") as mock_val,
    ):
        mock_prep.return_value = MagicMock(text="question", content_hash="h1", blocked_reason=None, pii_redacted=False)
        mock_val.return_value = MagicMock(text="Dangerous answer", blocked_reason="toxic", pii_redacted=False, quality_score=0.0)
        res_tox = await service.ask(session_id=session_id, question="q", client_message_id="msg-tox")
        assert res_tox["fallback"] is True
        assert res_tox["escalation"] is True
        assert mock_session3.status == "escalated"  # high severity sets status to 'escalated'
        service.ai_operations.cancel.assert_called_with(f"tutor:{session_id}:msg-tox", "output_toxic")

