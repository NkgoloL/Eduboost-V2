import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException

from app.api_v2_deps.auth import AuthContext

from app.services.lesson_authorization import (
    _call_authz,
    _construct_repo,
    _current_user_claims,
    _import_dotted,
    _owner_from_result,
    iter_sync_lesson_ids,
    lesson_owner_learner_id,
    require_lesson_read_access_for_current_user,
    require_lesson_write_access_for_current_user,
)
from app.services.lesson_service_v2 import LessonServiceV2
from app.services.lesson_transactional_completion import (
    LessonCompletionInput,
    LessonCompletionNotFoundError,
    LessonCompletionTransactionError,
    TransactionalLessonCompletionService,
)


def test_lesson_authorization_helpers_complete():
    # 1. _import_dotted failure (lines 49-50)
    assert _import_dotted("nonexistent.module.symbol") is None

    # 2. _owner_from_result branches (lines 65, 70-71, 73-76)
    # Tuple branch (line 65)
    assert _owner_from_result(("lesson_row", "learner-tuple-1")) == "learner-tuple-1"

    # Nested dict 'lesson' branch (lines 70-71)
    nested_dict = {"lesson": {"learner_id": "learner-nested-1"}}
    assert _owner_from_result(nested_dict) == "learner-nested-1"

    # Object attribute branch (lines 73-76)
    obj_owner = SimpleNamespace(student_id="student-attr-1")
    assert _owner_from_result(obj_owner) == "student-attr-1"

    # 3. _construct_repo failure (lines 102-104)
    class BrokenRepo:
        def __init__(self, a, b, c, d, e):
            pass
    with pytest.raises(RuntimeError, match="Cannot construct lesson repository"):
        _construct_repo(BrokenRepo, db=None)

    # 4. _call_authz failure (lines 144-145)
    def bad_authz(a, b, c, d, e):
        pass
    with pytest.raises(RuntimeError, match="Could not call learner authorization helper"):
        import asyncio
        asyncio.run(_call_authz(bad_authz, "user", "learner"))

    # 5. _current_user_claims with AuthContext (line 150)
    auth_ctx = AuthContext(
        user_id="user-123",
        token_type="access",
        jti="jti-123",
        raw_claims={"sub": "user-123", "role": "learner"},
    )
    assert _current_user_claims(auth_ctx) == {"sub": "user-123", "role": "learner"}

    # 6. iter_sync_lesson_ids cycle and UUID (lines 175-180)
    cycle_obj = SimpleNamespace()
    cycle_obj.self_ref = cycle_obj
    cycle_obj.uuid_val = uuid.uuid4()
    cycle_obj.lesson_id = "lesson-123"
    assert iter_sync_lesson_ids(cycle_obj) == ["lesson-123"]


@pytest.mark.asyncio
async def test_lesson_authorization_db_fallback_and_no_helper():
    db = AsyncMock()

    # 1. DB select fallback (lines 124-129)
    # Force repo to fail to fall through to model select
    from app.models import Lesson
    with patch("app.services.lesson_authorization._first_import") as mock_import:
        mock_lesson = SimpleNamespace(learner_id="learner-db-fallback")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_lesson
        db.execute.return_value = mock_result

        # Return None for repo candidates, then real Lesson model for model candidates
        mock_import.side_effect = [None, Lesson]

        owner = await lesson_owner_learner_id(db, "lesson-123")
        assert owner == "learner-db-fallback"

    # 2. No read/write authz helper found (lines 158, 166)
    with patch("app.services.lesson_authorization.lesson_owner_learner_id", return_value="l1"), \
         patch("app.services.lesson_authorization._first_import", return_value=None):
        with pytest.raises(RuntimeError, match="No learner-read authorization helper found"):
            await require_lesson_read_access_for_current_user(db, "user", "lesson-123")

        with pytest.raises(RuntimeError, match="No learner-write authorization helper found"):
            await require_lesson_write_access_for_current_user(db, "user", "lesson-123")



@pytest.mark.asyncio
async def test_lesson_service_v2_redis_miss():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None  # Cache miss

    mock_repo = AsyncMock()
    mock_row = SimpleNamespace(lesson_id="les-1", title="Lesson 1")
    mock_repo.get_by_id.return_value = mock_row

    svc = LessonServiceV2(lesson_repository=mock_repo, redis_client=mock_redis)
    lesson = await svc.get_lesson("les-1")
    assert lesson is not None
    assert lesson["lesson_id"] == "les-1"
    assert lesson["title"] == "Lesson 1"



@pytest.mark.asyncio
async def test_transactional_lesson_completion_complete():
    session = AsyncMock()
    mock_context = AsyncMock()
    session.begin = MagicMock(return_value=mock_context)

    lessons_table = MagicMock()
    lessons_table.c.id = "c_id"
    lessons_table.c.learner_id = "c_learner_id"

    profiles_table = MagicMock()
    profiles_table.c.learner_id = "c_learner_id"
    profiles_table.c.xp = 100

    audit_table = MagicMock()

    service = TransactionalLessonCompletionService(
        session=session,
        lessons_table=lessons_table,
        profiles_table=profiles_table,
        audit_events_table=audit_table,
    )

    base_input = {
        "lesson_id": "les-1",
        "learner_id": "learner-1",
        "xp_award": 50,
        "audit_actor_id": "actor-1",
    }

    # 1. Lesson rowcount != 1 (lines 66-67)
    session.execute.return_value = SimpleNamespace(rowcount=0)
    with pytest.raises(LessonCompletionNotFoundError, match="lesson not found for learner"):
        await service.complete_lesson(LessonCompletionInput(**base_input))

    # 2. fail_after_lesson (lines 68-69)
    session.execute.return_value = SimpleNamespace(rowcount=1)
    with pytest.raises(LessonCompletionTransactionError, match="simulated failure after lesson completion"):
        await service.complete_lesson(LessonCompletionInput(**base_input, fail_after_lesson=True))

    # 3. Profile rowcount != 1 (lines 76-77)
    session.execute.side_effect = [
        SimpleNamespace(rowcount=1),  # lesson update succeeds
        SimpleNamespace(rowcount=0),  # profile update rowcount=0
    ]
    with pytest.raises(LessonCompletionNotFoundError, match="gamification profile not found for learner"):
        await service.complete_lesson(LessonCompletionInput(**base_input))

    # 4. fail_after_xp (lines 78-79)
    session.execute.side_effect = [
        SimpleNamespace(rowcount=1),  # lesson
        SimpleNamespace(rowcount=1),  # profile
    ]
    with pytest.raises(LessonCompletionTransactionError, match="simulated failure after XP update"):
        await service.complete_lesson(LessonCompletionInput(**base_input, fail_after_xp=True))

    # 5. fail_after_audit (lines 91-92)
    session.execute.side_effect = [
        SimpleNamespace(rowcount=1),  # lesson
        SimpleNamespace(rowcount=1),  # profile
        SimpleNamespace(rowcount=1),  # audit
    ]
    with pytest.raises(LessonCompletionTransactionError, match="simulated failure after audit write"):
        await service.complete_lesson(LessonCompletionInput(**base_input, fail_after_audit=True))

    # 6. Success (lines 97-101)
    session.execute.side_effect = [
        SimpleNamespace(rowcount=1),
        SimpleNamespace(rowcount=1),
        SimpleNamespace(rowcount=1),
    ]
    res = await service.complete_lesson(LessonCompletionInput(**base_input))
    assert res.lesson_id == "les-1"
    assert res.learner_id == "learner-1"
    assert res.xp_award == 50
