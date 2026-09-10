"""Comprehensive unit tests for app/repositories to achieve >90% coverage across the package."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Assessment,
    AssessmentAttempt,
    AuditEvent,
    DiagnosticSession,
    Guardian,
    IRTItem,
    Language,
    Learner,
    LearnerProfile,
    Lesson,
    MasterySnapshot,
    ParentalConsent,
    PracticeSession,
    StudyPlan,
    SubjectMastery,
    TopicMastery,
)
from app.domain.consent import ConsentRecord, ConsentState, AuditEventType
from app.repositories.base import Repository
from app.repositories.audit_compat import (
    AuditEventInput,
    AuditRepositoryCompatAdapter,
    normalize_audit_kwargs,
    _maybe_await,
)
from app.repositories.irt_repository import IRTRepository
from app.repositories.mastery_repository import MasteryRepository
from app.repositories.diagnostic_session_repository import DiagnosticSessionRepository
from app.repositories.practice_session_repository import PracticeSessionRepository
from app.repositories.study_plan_repository import StudyPlanRepository
from app.repositories.auth_repository import GuardianRepository, AuthRepository
from app.repositories.learner_repository import LearnerRepository
from app.repositories.lesson_repository import LessonRepository, get_lesson_repository
from app.repositories.consent_repository import ConsentRepository
from app.repositories.diagnostic_repository import DiagnosticRepository
from app.repositories.assessment_repository import AssessmentRepository, AssessmentAttemptRepository
from app.repositories.gamification_repository import GamificationRepository, _optional_session
from app.repositories.audit_repository import AuditRepository
from app.repositories.repositories import ConsentRepository as RepositoriesConsentRepository


# =====================================================================
# 1. Base Repository Protocol
# =====================================================================

@pytest.mark.asyncio
async def test_base_repository_protocol():
    class DummyRepo(Repository[str]):
        async def get_by_id(self, entity_id: str) -> str | None:
            return f"item_{entity_id}"

    repo = DummyRepo()
    assert hasattr(repo, "get_by_id")
    assert await repo.get_by_id("123") == "item_123"


# =====================================================================
# 2. Audit Compat
# =====================================================================

def test_audit_event_input_canonical_payload():
    inp1 = AuditEventInput(
        action="update",
        actor_id="user-1",
        resource_type="report",
        resource_id="rep-1",
        learner_id="lrn-1",
        learner_pseudonym="pseudo-1",
        metadata={"extra": "val"},
    )
    payload1 = inp1.to_canonical_payload()
    assert payload1["action"] == "update"
    assert payload1["resource_id"] == "rep-1"
    assert payload1["payload"]["learner_id"] == "lrn-1"
    assert payload1["payload"]["learner_pseudonym"] == "pseudo-1"
    assert payload1["payload"]["extra"] == "val"

    # When resource_id is None, falls back to learner_id, then learner_pseudonym
    inp2 = AuditEventInput(action="test", learner_id="lrn-2")
    payload2 = inp2.to_canonical_payload()
    assert payload2["resource_id"] == "lrn-2"

    inp3 = AuditEventInput(action="test", learner_pseudonym="pseudo-3")
    payload3 = inp3.to_canonical_payload()
    assert payload3["resource_id"] == "pseudo-3"


def test_normalize_audit_kwargs():
    # Test action variants
    e1 = normalize_audit_kwargs(action="act1", actor_id="a1")
    assert e1.action == "act1"
    assert e1.actor_id == "a1"

    e2 = normalize_audit_kwargs(event_type="type1", metadata="non_dict_str")
    assert e2.action == "type1"
    assert e2.metadata == {"value": "non_dict_str"}

    e3 = normalize_audit_kwargs(event="evt1", payload={"key": "val"}, extra_foo="bar")
    assert e3.action == "evt1"
    assert e3.metadata["key"] == "val"
    assert e3.metadata["extra_foo"] == "bar"

    e4 = normalize_audit_kwargs(operation="op1")
    assert e4.action == "op1"

    with pytest.raises(ValueError, match="audit event requires"):
        normalize_audit_kwargs()


@pytest.mark.asyncio
async def test_maybe_await():
    async def sample_coro():
        return "async_res"

    assert await _maybe_await(sample_coro()) == "async_res"
    assert await _maybe_await("sync_res") == "sync_res"


@pytest.mark.asyncio
async def test_audit_repository_compat_adapter():
    # 1. Target with record()
    class TargetRecord:
        def __init__(self):
            self.calls = []
        async def record(self, **kwargs):
            self.calls.append(kwargs)
            return "record_done"

    t1 = TargetRecord()
    adapter1 = AuditRepositoryCompatAdapter(t1)
    res1 = await adapter1.record(action="user_login", actor_id="act-1")
    assert res1 == "record_done"
    assert len(t1.calls) == 1

    # Using append() delegating to record()
    res1_app = await adapter1.append(action="user_logout")
    assert res1_app == "record_done"

    # With pre-built AuditEventInput
    inp = AuditEventInput(action="audit_direct")
    res1_inp = await adapter1.record(inp)
    assert res1_inp == "record_done"

    # 2. Target with sync append()
    class TargetAppend:
        def __init__(self):
            self.calls = []
        def append(self, **kwargs):
            self.calls.append(kwargs)
            return "append_done"

    t2 = TargetAppend()
    adapter2 = AuditRepositoryCompatAdapter(t2)
    res2 = await adapter2.record(action="action2")
    assert res2 == "append_done"

    # 3. Target with sync create()
    class TargetCreate:
        def __init__(self):
            self.calls = []
        def create(self, **kwargs):
            self.calls.append(kwargs)
            return "create_done"

    t3 = TargetCreate()
    adapter3 = AuditRepositoryCompatAdapter(t3)
    res3 = await adapter3.record(action="action3")
    assert res3 == "create_done"

    # 4. Target missing all methods raises TypeError
    class EmptyTarget:
        pass

    adapter4 = AuditRepositoryCompatAdapter(EmptyTarget())
    with pytest.raises(TypeError, match="must expose record"):
        await adapter4.record(action="fail")


# =====================================================================
# 3. IRT Repository
# =====================================================================

@pytest.mark.asyncio
async def test_irt_repository():
    mock_db = AsyncMock()
    mock_item = MagicMock(spec=IRTItem)
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [mock_item]
    mock_db.execute.return_value = mock_res

    repo = IRTRepository()
    items_grade = await repo.get_items_for_grade(mock_db, grade=5, language=Language.AFRIKAANS, limit=10)
    assert items_grade == [mock_item]
    assert mock_db.execute.called

    items_sub = await repo.get_items_by_subject(mock_db, grade=5, subject="MATH", limit=5)
    assert items_sub == [mock_item]


# =====================================================================
# 4. Mastery Repository
# =====================================================================

@pytest.mark.asyncio
async def test_mastery_repository():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    repo = MasteryRepository(mock_db)

    # 1. upsert_topic_mastery when existing is None
    mock_res_none = MagicMock()
    mock_res_none.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res_none

    created = await repo.upsert_topic_mastery("learner-1", "CAPS-1", mastery_score=0.8, mastery_label="mastered")
    assert created.caps_ref == "CAPS-1"
    assert created.mastery_score == 0.8
    assert mock_db.add.called
    assert mock_db.flush.called
    assert mock_db.refresh.called

    # 2. upsert_topic_mastery when existing exists
    existing = TopicMastery(learner_id="learner-1", caps_ref="CAPS-1", mastery_score=0.4, mastery_label="emerging")
    mock_res_exist = MagicMock()
    mock_res_exist.scalar_one_or_none.return_value = existing
    mock_db.execute.return_value = mock_res_exist

    updated = await repo.upsert_topic_mastery("learner-1", "CAPS-1", mastery_score=0.9, mastery_label="mastered", theta=1.5, theta_se=0.2)
    assert updated.mastery_score == 0.9
    assert updated.theta_estimate == 1.5

    # 3. get_topic_mastery
    mock_db.execute.return_value = mock_res_exist
    got = await repo.get_topic_mastery("learner-1", "CAPS-1")
    assert got == existing

    # 4. list_topic_mastery_by_learner
    mock_res_list = MagicMock()
    mock_res_list.scalars.return_value.all.return_value = [existing]
    mock_db.execute.return_value = mock_res_list
    all_mastery = await repo.list_topic_mastery_by_learner("learner-1")
    assert all_mastery == [existing]

    # 5. create_snapshot
    snapshot = await repo.create_snapshot("learner-1", "CAPS-1", mastery_score=0.95, mastery_label="mastered", theta_estimate=1.2, theta_se=0.1, trigger="practice", practice_accuracy=1.0)
    assert snapshot.trigger == "practice"

    # 6. get_snapshots_for_learner_topic
    mock_snap = MagicMock(spec=MasterySnapshot)
    mock_res_snap = MagicMock()
    mock_res_snap.scalars.return_value.all.return_value = [mock_snap]
    mock_db.execute.return_value = mock_res_snap
    snaps = await repo.get_snapshots_for_learner_topic("learner-1", "CAPS-1")
    assert snaps == [mock_snap]


# =====================================================================
# 5. Diagnostic Session Repository
# =====================================================================

@pytest.mark.asyncio
async def test_diagnostic_session_repository():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    repo = DiagnosticSessionRepository(mock_db)

    # 1. create_session with caps_ref
    s1 = await repo.create_session("learner-1", theta=0.5, se=0.8, caps_ref="CAPS-1")
    assert s1.theta_before == 0.5
    assert s1.responses == {"caps_ref": "CAPS-1"}

    # create_session without caps_ref
    s2 = await repo.create_session("learner-2")
    assert s2.responses == {}

    # 2. get_session
    mock_res = MagicMock()
    mock_session = DiagnosticSession(id="sess-1", learner_id="learner-1", responses={"items": []})
    mock_res.scalar_one_or_none.return_value = mock_session
    mock_db.execute.return_value = mock_res

    sess = await repo.get_session("sess-1")
    assert sess == mock_session

    # 3. update_session_state
    # Not found case
    mock_res_none = MagicMock()
    mock_res_none.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res_none
    assert await repo.update_session_state("missing", "in_progress") is None

    # Found case
    mock_db.execute.return_value = mock_res
    updated = await repo.update_session_state("sess-1", "completed", theta_after=1.2)
    assert updated is not None
    assert updated.session_state == "completed"
    assert updated.theta_after == 1.2

    # 4. append_response
    # Not found case
    mock_db.execute.return_value = mock_res_none
    assert await repo.append_response("missing", {"item_id": "i1"}) is None

    # Found case
    mock_session.responses = {}
    mock_db.execute.return_value = mock_res
    appended = await repo.append_response("sess-1", {"item_id": "i1", "is_correct": True})
    assert appended is not None
    assert appended.items_served == 1
    assert appended.responses["items"] == [{"item_id": "i1", "is_correct": True}]

    # 5. list_incomplete_sessions
    mock_res_all = MagicMock()
    mock_res_all.scalars.return_value.all.return_value = [mock_session]
    mock_db.execute.return_value = mock_res_all
    incompletes = await repo.list_incomplete_sessions("learner-1")
    assert incompletes == [mock_session]


# =====================================================================
# 6. Practice Session Repository
# =====================================================================

@pytest.mark.asyncio
async def test_practice_session_repository():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    repo = PracticeSessionRepository(mock_db)

    # 1. create
    sess = await repo.create(
        learner_id="lrn-1",
        owner_subject="sub-1",
        items=["item-1", "item-2"],
        gap_topics=["GAP-1"],
        theta=0.2,
        session_ttl_hours=12,
    )
    assert sess.learner_id == "lrn-1"
    assert sess.gap_topics == ["GAP-1"]
    assert mock_db.flush.called

    # 2. get_by_id
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = sess
    mock_db.execute.return_value = mock_res
    got = await repo.get_by_id(sess.id)
    assert got == sess

    # 3. update_cursor_and_responses
    mock_exec_res = MagicMock()
    mock_exec_res.rowcount = 1
    mock_db.execute.return_value = mock_exec_res
    res_up = await repo.update_cursor_and_responses(sess.id, 1, [{"item": "1"}])
    assert res_up is True

    mock_exec_res.rowcount = 0
    assert await repo.update_cursor_and_responses(sess.id, 2, []) is False

    # 4. mark_completed
    mock_exec_res.rowcount = 1
    assert await repo.mark_completed(sess.id) is True
    mock_exec_res.rowcount = 0
    assert await repo.mark_completed(sess.id) is False

    # 5. delete_expired
    mock_exec_res.rowcount = 5
    deleted_cnt = await repo.delete_expired()
    assert deleted_cnt == 5
    assert mock_db.commit.called

    # 6. list_by_learner
    mock_res_list = MagicMock()
    mock_res_list.scalars.return_value.all.return_value = [sess]
    mock_db.execute.return_value = mock_res_list
    sessions = await repo.list_by_learner("lrn-1")
    assert sessions == [sess]


# =====================================================================
# 7. Study Plan Repository
# =====================================================================

@pytest.mark.asyncio
async def test_study_plan_repository():
    repo = StudyPlanRepository()

    mock_session = AsyncMock()
    mock_session.add = MagicMock()

    class MockContextManager:
        async def __aenter__(self):
            return mock_session
        async def __aexit__(self, exc_type, exc, tb):
            pass

    with patch("app.repositories.study_plan_repository.AsyncSessionFactory", return_value=MockContextManager()):
        # 1. create
        plan_dict = await repo.create(
            learner_id="lrn-1",
            schedule={"mon": ["math"]},
            gap_ratio=0.3,
            week_focus="Algebra",
        )
        assert plan_dict["learner_id"] == "lrn-1"
        assert plan_dict["gap_ratio"] == 0.3
        assert plan_dict["week_focus"] == "Algebra"

        # 2. get_by_id when plan exists
        mock_plan = MagicMock(spec=StudyPlan)
        mock_plan.id = "plan-123"
        mock_plan.learner_id = "lrn-1"
        mock_plan.week_start = datetime.now(timezone.utc)
        mock_plan.schedule = {"mon": ["math"]}
        mock_plan.gap_ratio = 0.2
        mock_plan.week_focus = "Trig"
        mock_plan.generated_by = "ALGO"

        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = mock_plan
        mock_session.execute.return_value = mock_res

        fetched = await repo.get_by_id("plan-123")
        assert fetched is not None
        assert fetched["plan_id"] == "plan-123"
        assert fetched["learner_id"] == "lrn-1"

        # get_by_id when plan does not exist
        mock_res.scalar_one_or_none.return_value = None
        assert await repo.get_by_id("missing") is None

        # 3. list_for_learner
        mock_res.scalars.return_value.all.return_value = [mock_plan]
        plan_list = await repo.list_for_learner("lrn-1", limit=5)
        assert len(plan_list) == 1
        assert plan_list[0]["plan_id"] == "plan-123"

        # 4. get_subject_mastery
        mock_mastery = MagicMock(spec=SubjectMastery)
        mock_mastery.subject_code = "MATH"
        mock_mastery.grade_level = 10
        mock_mastery.mastery_score = 0.75
        mock_mastery.knowledge_gaps = ["gap-1"]

        mock_res.scalars.return_value.all.return_value = [mock_mastery]
        mastery_list = await repo.get_subject_mastery("lrn-1")
        assert mastery_list == [
            {
                "subject_code": "MATH",
                "grade_level": 10,
                "mastery_score": 0.75,
                "knowledge_gaps": ["gap-1"],
            }
        ]


# =====================================================================
# 8. Auth Repository (GuardianRepository)
# =====================================================================

@pytest.mark.asyncio
async def test_auth_repository():
    mock_db = AsyncMock(spec=AsyncSession)
    repo_with_db = GuardianRepository(mock_db)
    repo_without_db = GuardianRepository()

    # _resolve_db error
    with pytest.raises(ValueError, match="GuardianRepository requires an AsyncSession"):
        repo_without_db._resolve_db()

    assert repo_with_db._resolve_db() is mock_db

    mock_guardian = MagicMock(spec=Guardian)
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_guardian
    mock_db.execute.return_value = mock_res

    # get_by_id
    assert await repo_with_db.get_by_id("g-1") == mock_guardian
    assert await repo_without_db.get_by_id("g-1", db=mock_db) == mock_guardian

    # get_by_email_hash
    assert await repo_with_db.get_by_email_hash("hash123") == mock_guardian

    # get_by_verification_token
    with patch.object(Guardian, "verification_token", create=True, new=MagicMock()):
        assert await repo_with_db.get_by_verification_token("tok123") == mock_guardian

    # get_guardian_by_id
    assert await repo_with_db.get_guardian_by_id("g-1") == mock_guardian

    # get_by_stripe_customer_id
    assert await repo_with_db.get_by_stripe_customer_id("cus_123") == mock_guardian

    # update_subscription
    await repo_with_db.update_subscription("g-1", "premium", "sub_123")
    assert mock_db.flush.called

    # revoke_jti
    exp = datetime.now(timezone.utc)
    await repo_with_db.revoke_jti("jti-1", exp)

    # is_jti_revoked True and False
    mock_first = MagicMock()
    mock_first.first.return_value = (1,)
    mock_db.execute.return_value = mock_first
    assert await repo_with_db.is_jti_revoked("jti-1") is True

    mock_first.first.return_value = None
    assert await repo_with_db.is_jti_revoked("jti-unknown") is False

    # Alias check
    assert AuthRepository is GuardianRepository


# =====================================================================
# 9. Learner Repository
# =====================================================================

@pytest.mark.asyncio
async def test_learner_repository():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.add = MagicMock()
    repo = LearnerRepository(mock_db)
    repo_no_db = LearnerRepository()

    with pytest.raises(ValueError, match="LearnerRepository requires an AsyncSession"):
        repo_no_db._db(None)

    learner_uuid = uuid.uuid4()
    mock_learner = MagicMock(spec=Learner)
    mock_learner.id = learner_uuid

    # get_by_id via mock patch of BaseRepository.get
    with patch.object(LearnerRepository, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_learner
        got = await repo.get_by_id(str(learner_uuid))
        assert got == mock_learner

    # delete_by_id
    mock_del_res = MagicMock()
    mock_del_res.rowcount = 1
    mock_db.execute.return_value = mock_del_res
    assert await repo.delete_by_id(learner_uuid) is True

    mock_del_res.rowcount = 0
    assert await repo.delete_by_id(learner_uuid) is False

    # soft_delete when learner is None
    with patch.object(repo, "get_by_id", new_callable=AsyncMock) as mock_get_by_id:
        mock_get_by_id.return_value = None
        await repo.soft_delete(learner_uuid)
        assert not mock_db.flush.called

        # soft_delete when learner exists (synchronous add)
        mock_get_by_id.return_value = mock_learner
        mock_db.add.return_value = None
        await repo.soft_delete(learner_uuid)
        assert mock_learner.display_name == "[erased]"
        assert mock_learner.is_deleted is True
        assert mock_db.flush.called

        # soft_delete when add is awaitable
        async def mock_async_add(entity):
            return None
        mock_db.add = mock_async_add
        await repo.soft_delete(learner_uuid)

    # purge_personal_data
    await repo.purge_personal_data(learner_uuid)
    assert mock_db.execute.called


# =====================================================================
# 10. Lesson Repository
# =====================================================================

@pytest.mark.asyncio
async def test_lesson_repository():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.add = MagicMock()
    repo = LessonRepository(mock_db)
    repo_no_db = LessonRepository()

    with pytest.raises(RuntimeError, match="LessonRepository requires an AsyncSession"):
        repo_no_db._db(None)

    # 1. create
    # pass db in args
    l1 = await repo_no_db.create(mock_db, topic="Lesson 1", content="intro", subject="MATH", grade=10)
    assert l1.topic == "Lesson 1"
    # pass db in kwargs
    l2 = await repo_no_db.create(topic="Lesson 2", content="intro 2", subject="MATH", grade=10, db=mock_db)
    assert l2.topic == "Lesson 2"

    # 2. get
    mock_lesson = MagicMock(spec=Lesson)
    mock_lesson.id = "lesson-1"
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_lesson
    mock_db.execute.return_value = mock_res
    assert await repo.get("lesson-1") == mock_lesson

    # 3. get_recent_for_learner with and without subject
    mock_res.scalars.return_value.all.return_value = [mock_lesson]
    r1 = await repo.get_recent_for_learner("lrn-1", subject="MATH", limit=5)
    assert r1 == [mock_lesson]
    r2 = await repo.get_recent_for_learner("lrn-1", subject=None, limit=5)
    assert r2 == [mock_lesson]

    # 4. get_recent with skip
    r3 = await repo.get_recent("lrn-1", skip=2, limit=5)
    assert r3 == [mock_lesson]

    # 5. list_pending_review with all filters
    p1 = await repo.list_pending_review(grade=10, subject="MATH", caps_ref="CAPS-1", limit=10, offset=0)
    assert p1 == [mock_lesson]

    # 6. list_by_caps_ref
    await repo.list_by_caps_ref("CAPS-1", include_all_statuses=True)
    await repo.list_by_caps_ref("CAPS-1", include_all_statuses=False)

    # 7. update_review_status
    # Not found
    with patch.object(repo, "get", new_callable=AsyncMock) as mock_repo_get:
        mock_repo_get.return_value = None
        assert await repo.update_review_status("missing", review_status="approved", reviewer_id=uuid.uuid4()) is None

        # Found
        mock_lesson.trust_label = {"existing": "val"}
        mock_repo_get.return_value = mock_lesson
        rev_id = uuid.uuid4()
        up_lesson = await repo.update_review_status(
            "lesson-1",
            review_status="approved",
            reviewer_id=rev_id,
            reviewer_notes="looks good",
        )
        assert up_lesson is not None
        assert up_lesson.review_status == "approved"
        assert up_lesson.reviewer_id == rev_id
        assert up_lesson.trust_label["reviewer_notes"] == "looks good"

    # 8. record_feedback
    await repo.record_feedback("lesson-1", 5)

    # 9. mark_completed
    await repo.mark_completed("lesson-1", completed_at=datetime.now(timezone.utc))
    await repo.mark_completed("lesson-1", completed_at=None)

    # 10. count_approved_by_caps_ref_async
    mock_cnt_res = MagicMock()
    mock_cnt_res.scalar_one.return_value = 42
    mock_db.execute.return_value = mock_cnt_res
    cnt = await repo.count_approved_by_caps_ref_async("CAPS-1")
    assert cnt == 42

    # 11. list_approved_lessons_async and _to_validator_payload
    mock_lesson.id = "lesson-1"
    mock_lesson.grade = 10
    mock_lesson.subject = "MATH"
    mock_lesson.topic = "Algebra"
    mock_lesson.caps_ref = "CAPS-1"
    mock_lesson.explanation = None
    mock_lesson.content = "Explanation fallback"
    mock_lesson.worked_examples = None
    mock_lesson.practice_questions = None
    mock_lesson.answer_key = None
    mock_lesson.answer_key_verified = True
    mock_lesson.provider = None
    mock_lesson.llm_provider = "anthropic"
    mock_lesson.model_version = None
    mock_lesson.generation_latency_ms = 350
    mock_lesson.token_usage = None
    mock_lesson.prompt_template_version = None
    mock_lesson.variant_type = None

    mock_res.scalars.return_value.all.return_value = [mock_lesson]
    mock_db.execute.return_value = mock_res
    val_list = await repo.list_approved_lessons_async()
    assert len(val_list) == 1
    assert val_list[0]["explanation"] == "Explanation fallback"
    assert val_list[0]["provider"] == "anthropic"
    assert val_list[0]["token_usage"] == {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    # 12. get_lesson_repository dependency helper
    dep = get_lesson_repository(mock_db)
    assert isinstance(dep, LessonRepository)
    assert dep.db is mock_db


# =====================================================================
# 11. Consent Repository
# =====================================================================

@pytest.mark.asyncio
async def test_consent_repository():
    mock_pool = AsyncMock()
    repo = ConsentRepository(mock_pool)

    cid = uuid.uuid4()
    lid = uuid.uuid4()
    gid = uuid.uuid4()
    now = datetime.now(timezone.utc)

    row_data = {
        "id": cid,
        "learner_id": lid,
        "guardian_id": gid,
        "privacy_notice_version": "v1.0",
        "state": "granted",
        "granted_at": now,
        "expires_at": now,
        "withdrawn_at": None,
        "denial_reason": None,
        "created_at": now,
        "updated_at": now,
    }

    # get_active_for_learner
    mock_pool.fetchrow.return_value = row_data
    rec = await repo.get_active_for_learner(lid)
    assert rec is not None
    assert rec.id == cid
    assert rec.state == ConsentState.GRANTED

    # when row is None
    mock_pool.fetchrow.return_value = None
    assert await repo.get_active_for_learner(lid) is None

    # get_by_id
    mock_pool.fetchrow.return_value = row_data
    rec_by_id = await repo.get_by_id(cid)
    assert rec_by_id is not None
    assert rec_by_id.id == cid

    mock_pool.fetchrow.return_value = None
    assert await repo.get_by_id(cid) is None

    # create
    model = ConsentRecord(
        id=cid,
        learner_id=lid,
        guardian_id=gid,
        privacy_notice_version="v1.0",
        state=ConsentState.GRANTED,
        granted_at=now,
        expires_at=now,
    )
    created = await repo.create(model)
    assert created is model
    assert mock_pool.execute.called

    # update
    updated = await repo.update(model)
    assert updated is model

    # list_expiring_soon
    mock_pool.fetch.return_value = [row_data]
    expiring = await repo.list_expiring_soon(within_days=15)
    assert len(expiring) == 1
    assert expiring[0].id == cid


# =====================================================================
# 12. Diagnostic Repository
# =====================================================================

@pytest.mark.asyncio
async def test_diagnostic_repository():
    repo = DiagnosticRepository()
    mock_db = AsyncMock()

    mock_sess = MagicMock(spec=DiagnosticSession)
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_sess
    mock_db.execute.return_value = mock_res

    # get_latest_for_learner
    class MockCol:
        def __eq__(self, other):
            return True
        def desc(self):
            return self

    with patch("app.repositories.diagnostic_repository.select") as mock_select, \
         patch.object(DiagnosticSession, "subject", MockCol(), create=True), \
         patch.object(DiagnosticSession, "started_at", MockCol(), create=True):
        mock_stmt = MagicMock()
        mock_select.return_value = mock_stmt
        mock_stmt.where.return_value = mock_stmt
        mock_stmt.order_by.return_value = mock_stmt
        mock_stmt.limit.return_value = mock_stmt
        latest = await repo.get_latest_for_learner(uuid.uuid4(), "MATH", mock_db)
        assert latest == mock_sess

    # create_session
    with patch.object(DiagnosticRepository, "create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_sess
        res = await repo.create_session(
            learner_id="lrn-1",
            subject_code="MATH",
            grade_level=10,
            theta=0.5,
            sem=0.2,
            items_administered=10,
            items_correct=8,
            items_total=10,
            final_mastery_score=0.8,
            knowledge_gaps=["gap1"],
            db=mock_db,
        )
        assert res == mock_sess
        assert mock_create.called


# =====================================================================
# 13. Assessment Repository
# =====================================================================

@pytest.mark.asyncio
async def test_assessment_repository():
    mock_db = AsyncMock()
    repo = AssessmentRepository(mock_db)
    repo_no_db = AssessmentRepository()

    with pytest.raises(ValueError, match="AssessmentRepository requires an AsyncSession"):
        repo_no_db._resolve_db()

    aid = uuid.uuid4()
    mock_assessment = MagicMock(spec=Assessment)
    mock_assessment.id = aid
    mock_assessment.title = "Math Midterm"
    mock_assessment.subject_code = "MATH"
    mock_assessment.grade_level = 10
    mock_assessment.assessment_type = "diagnostic"
    mock_assessment.total_marks = 100
    mock_assessment.questions = {"questions": [{"id": "q1"}]}
    mock_assessment.passing_score = 50.0
    mock_assessment.is_active = True

    # list_active
    with patch.object(AssessmentRepository, "list", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [mock_assessment]
        active = await repo.list_active(limit=10, offset=0)
        assert active == [mock_assessment]

    # get_by_id_str
    with patch.object(AssessmentRepository, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_assessment
        got = await repo.get_by_id_str(str(aid))
        assert got == mock_assessment

    # list_assessments
    with patch.object(repo, "list_active", new_callable=AsyncMock) as mock_list_active:
        mock_list_active.return_value = [mock_assessment]
        res_list = await repo.list_assessments()
        assert len(res_list) == 1
        assert res_list[0]["questions"] == [{"id": "q1"}]

    # get_assessment
    with patch.object(repo, "get_by_id_str", new_callable=AsyncMock) as mock_get_str:
        mock_get_str.return_value = mock_assessment
        res = await repo.get_assessment(str(aid))
        assert res is not None
        assert res["title"] == "Math Midterm"

        # None case
        mock_get_str.return_value = None
        assert await repo.get_assessment("missing") is None

    # to_payload with questions as list
    mock_assessment.questions = [{"id": "q2"}]
    payload = AssessmentRepository.to_payload(mock_assessment)
    assert payload["questions"] == [{"id": "q2"}]

    # create_attempt
    mock_attempt = MagicMock(spec=AssessmentAttempt)
    mock_attempt.id = uuid.uuid4()
    with patch.object(AssessmentAttemptRepository, "create_attempt", new_callable=AsyncMock) as mock_create_att:
        mock_create_att.return_value = mock_attempt
        att_id = await repo.create_attempt(
            assessment_id=aid,
            learner_id=uuid.uuid4(),
            responses=[{"q": 1}],
            score=85.0,
            marks_obtained=85,
            time_taken_seconds=1200,
        )
        assert att_id == str(mock_attempt.id)

    # AssessmentAttemptRepository directly
    att_repo = AssessmentAttemptRepository()
    with patch.object(AssessmentAttemptRepository, "create", new_callable=AsyncMock) as mock_base_create:
        mock_base_create.return_value = mock_attempt
        res_att = await att_repo.create_attempt(
            mock_db,
            assessment_id=aid,
            learner_id="lrn-1",
            score=90.0,
            marks_obtained=90,
            time_taken_seconds=1000,
            responses={"responses": []},
        )
        assert res_att == mock_attempt


# =====================================================================
# 14. Gamification Repository
# =====================================================================

@pytest.mark.asyncio
async def test_gamification_repository():
    mock_db = AsyncMock()
    repo = GamificationRepository(mock_db)

    # 1. _optional_session with provided db
    async with _optional_session(mock_db) as sess:
        assert sess is mock_db

    # 2. _optional_session with None db
    mock_owned = AsyncMock()
    with patch("app.repositories.gamification_repository.AsyncSessionLocal", return_value=mock_owned):
        opt = _optional_session(None)
        mock_owned.__aenter__.return_value = mock_owned
        async with opt as sess:
            assert sess is mock_owned
        assert mock_owned.__aexit__.called

    # 3. get_profile_rows
    # learner is None
    mock_db.get.return_value = None
    profile, badges = await repo.get_profile_rows("lrn-1")
    assert profile is None
    assert badges == []

    # learner is deleted
    mock_profile = MagicMock(spec=LearnerProfile)
    mock_profile.is_deleted = True
    mock_db.get.return_value = mock_profile
    profile, badges = await repo.get_profile_rows("lrn-1")
    assert profile is None

    # learner is active
    mock_profile.is_deleted = False
    mock_db.get.return_value = mock_profile
    profile, badges = await repo.get_profile_rows("lrn-1")
    assert profile == mock_profile
    assert badges == []

    # 4. get_leaderboard_rows
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [mock_profile]
    mock_db.execute.return_value = mock_res
    leaderboard = await repo.get_leaderboard_rows(limit=5)
    assert leaderboard == [mock_profile]


# =====================================================================
# 15. Audit Repository and Repositories Edge Branches
# =====================================================================

@pytest.mark.asyncio
async def test_audit_repository_edge_branches():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    repo_async = AuditRepository(mock_db)

    # 1. blank event_type raises ValueError
    with pytest.raises(ValueError, match="event_type must not be blank"):
        await repo_async.append(event_type="   ")

    # 2. PII check with nested list containing dict with forbidden keys
    with pytest.raises(ValueError, match="PII field names are not permitted"):
        await repo_async.append(
            event_type=AuditEventType.LOGIN_SUCCESS,
            payload={"records": [{"email": "test@example.com"}]},
        )

    # 3. _latest_hash with resource_id = None on AsyncSession
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = "hash-123"
    mock_db.execute.return_value = mock_res
    h = await repo_async._latest_hash(resource_id=None)
    assert h == "hash-123"

    # 4. get_by_resource with event_type specified on AsyncSession
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_res.scalars.return_value = mock_scalars
    await repo_async.get_by_resource("res-1", event_type="LOGIN")

    # 5. get_by_actor with event_type specified on AsyncSession
    await repo_async.get_by_actor("actor-1", event_type="LOGIN")

    # 6. asyncpg pool backend branch for get_by_actor and get_by_resource with event_type
    mock_pool = MagicMock()
    del mock_pool.add
    mock_pool.fetch = AsyncMock(return_value=[])
    mock_pool.fetchrow = AsyncMock(return_value=None)
    repo_pool = AuditRepository(mock_pool)
    await repo_pool.get_by_actor("actor-1", event_type="LOGIN")
    await repo_pool.get_by_resource("res-1", event_type="LOGIN")

    # 7. asyncpg append when fetchrow returns None raises AssertionError
    with pytest.raises(AssertionError):
        await repo_pool.append(event_type=AuditEventType.LOGIN_SUCCESS, payload={"msg": "hello"})


@pytest.mark.asyncio
async def test_parental_consent_repository_renew_without_previous():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    repo = RepositoriesConsentRepository(mock_db)

    # When get_active returns None
    with patch.object(repo, "get_active", new_callable=AsyncMock) as mock_get_active, \
         patch.object(repo, "grant", new_callable=AsyncMock) as mock_grant:
        mock_get_active.return_value = None
        new_consent = MagicMock(spec=ParentalConsent)
        mock_grant.return_value = new_consent

        prev, renewed = await repo.renew("learner-1", "guardian-1", "v1.0")
        assert prev is None
        assert renewed is new_consent
