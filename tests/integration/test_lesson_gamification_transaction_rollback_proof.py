from __future__ import annotations

import pytest
from sqlalchemy import Boolean, Column, DateTime, Integer, MetaData, String, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.services.lesson_transactional_completion import (
    LessonCompletionInput,
    LessonCompletionNotFoundError,
    LessonCompletionTransactionError,
    TransactionalLessonCompletionService,
)


pytestmark = pytest.mark.asyncio

metadata = MetaData()

lessons = Table = __import__("sqlalchemy").Table(
    "lesson_tx_lessons",
    metadata,
    Column("id", String, primary_key=True),
    Column("learner_id", String, nullable=False),
    Column("completed", Boolean, nullable=False, default=False),
    Column("completed_at", DateTime(timezone=True), nullable=True),
)

profiles = __import__("sqlalchemy").Table(
    "lesson_tx_profiles",
    metadata,
    Column("learner_id", String, primary_key=True),
    Column("xp", Integer, nullable=False, default=0),
    Column("updated_at", DateTime(timezone=True), nullable=True),
)

audit_events = __import__("sqlalchemy").Table(
    "lesson_tx_audit_events",
    metadata,
    Column("id", String, primary_key=True),
    Column("event_type", String, nullable=False),
    Column("actor_id", String, nullable=False),
    Column("learner_id", String, nullable=False),
    Column("resource_id", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as db:
        yield db

    await engine.dispose()


async def _seed(session, *, lesson_id: str = "lesson-1", learner_id: str = "learner-1", xp: int = 10) -> None:
    async with session.begin():
        await session.execute(
            lessons.insert().values(id=lesson_id, learner_id=learner_id, completed=False, completed_at=None)
        )
        await session.execute(profiles.insert().values(learner_id=learner_id, xp=xp, updated_at=None))


async def _lesson_completed(session, lesson_id: str = "lesson-1") -> bool:
    result = await session.execute(select(lessons.c.completed).where(lessons.c.id == lesson_id))
    return bool(result.scalar_one())


async def _xp(session, learner_id: str = "learner-1") -> int:
    result = await session.execute(select(profiles.c.xp).where(profiles.c.learner_id == learner_id))
    return int(result.scalar_one())


async def _audit_count(session) -> int:
    result = await session.execute(select(func.count()).select_from(audit_events))
    return int(result.scalar_one())


def _service(session) -> TransactionalLessonCompletionService:
    return TransactionalLessonCompletionService(
        session,
        lessons_table=lessons,
        profiles_table=profiles,
        audit_events_table=audit_events,
    )


def _input(**overrides) -> LessonCompletionInput:
    data = {
        "lesson_id": "lesson-1",
        "learner_id": "learner-1",
        "xp_award": 25,
        "audit_actor_id": "guardian-1",
    }
    data.update(overrides)
    return LessonCompletionInput(**data)


async def test_lesson_completion_success_commits_lesson_xp_and_audit(session):
    await _seed(session)
    service = _service(session)

    result = await service.complete_lesson(_input())

    assert result.lesson_id == "lesson-1"
    assert await _lesson_completed(session) is True
    assert await _xp(session) == 35
    assert await _audit_count(session) == 1


@pytest.mark.parametrize("flag", ["fail_after_lesson", "fail_after_xp", "fail_after_audit"])
async def test_lesson_completion_failure_rolls_back_all_rows(session, flag):
    await _seed(session)
    service = _service(session)

    with pytest.raises(LessonCompletionTransactionError):
        await service.complete_lesson(_input(**{flag: True}))

    assert await _lesson_completed(session) is False
    assert await _xp(session) == 10
    assert await _audit_count(session) == 0


async def test_lesson_completion_failure_does_not_damage_prior_committed_rows(session):
    await _seed(session, lesson_id="lesson-1", learner_id="learner-1", xp=10)
    await _seed(session, lesson_id="lesson-2", learner_id="learner-2", xp=5)
    service = _service(session)

    await service.complete_lesson(
        _input(lesson_id="lesson-1", learner_id="learner-1", xp_award=20, audit_actor_id="guardian-1")
    )

    with pytest.raises(LessonCompletionTransactionError):
        await service.complete_lesson(
            _input(
                lesson_id="lesson-2",
                learner_id="learner-2",
                xp_award=30,
                audit_actor_id="guardian-2",
                fail_after_xp=True,
            )
        )

    assert await _lesson_completed(session, "lesson-1") is True
    assert await _xp(session, "learner-1") == 30
    assert await _lesson_completed(session, "lesson-2") is False
    assert await _xp(session, "learner-2") == 5
    assert await _audit_count(session) == 1


async def test_missing_profile_rolls_back_lesson_completion(session):
    async with session.begin():
        await session.execute(
            lessons.insert().values(id="lesson-1", learner_id="learner-1", completed=False, completed_at=None)
        )
    service = _service(session)

    with pytest.raises(LessonCompletionNotFoundError):
        await service.complete_lesson(_input())

    assert await _lesson_completed(session) is False
    assert await _audit_count(session) == 0
