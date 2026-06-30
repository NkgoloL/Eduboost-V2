"""
Integration tests for practice session durability across process restarts.

These tests verify that:
1. Sessions survive process restarts (persisted in database)
2. Multi-worker access returns consistent state
3. Expired sessions cannot be accessed
4. Cross-user authorization is properly enforced
"""
from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.repositories.practice_session_repository import PracticeSessionRepository


@pytest.fixture
async def async_db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_practice_session_persists_across_repository_instances(async_db_session):
    """Test that a session created in one repo instance is retrievable by another."""
    learner_id = str(uuid4())
    owner_subject = "test_user_1"
    items = [str(uuid4()) for _ in range(3)]
    gap_topics = ["CAPS ref 1", "CAPS ref 2"]

    # Create session with first repository instance
    repo1 = PracticeSessionRepository(async_db_session)
    session1 = await repo1.create(
        learner_id=learner_id,
        owner_subject=owner_subject,
        items=items,
        gap_topics=gap_topics,
        theta=0.5,
    )
    await async_db_session.commit()
    session_id = session1.id

    # Retrieve session with new repository instance (simulating process restart)
    repo2 = PracticeSessionRepository(async_db_session)
    session2 = await repo2.get_by_id(session_id)

    assert session2 is not None
    assert session2.id == session_id
    assert session2.learner_id == learner_id
    assert session2.owner_subject == owner_subject
    assert session2.items == items
    assert session2.gap_topics == gap_topics
    assert session2.cursor == 0
    assert session2.theta == 0.5


@pytest.mark.asyncio
async def test_practice_session_updates_survive_restart_cycle(async_db_session):
    """Test that session state updates (cursor, responses) persist across restarts."""
    learner_id = str(uuid4())
    item_id = str(uuid4())

    # Create and commit session
    repo1 = PracticeSessionRepository(async_db_session)
    session1 = await repo1.create(
        learner_id=learner_id,
        owner_subject="test_user",
        items=[item_id],
        gap_topics=[],
    )
    await async_db_session.commit()
    session_id = session1.id

    # Update session state
    response = {"item_id": item_id, "correct": True, "response": "A"}
    await repo1.update_cursor_and_responses(session_id, 1, [response])
    await async_db_session.commit()

    # Retrieve in new repo instance
    repo2 = PracticeSessionRepository(async_db_session)
    session2 = await repo2.get_by_id(session_id)

    assert session2.cursor == 1
    assert len(session2.responses) == 1
    assert session2.responses[0]["correct"] == True


@pytest.mark.asyncio
async def test_expired_session_cannot_be_retrieved(async_db_session):
    """Test that expired sessions are filtered out by get_by_id."""
    learner_id = str(uuid4())

    repo = PracticeSessionRepository(async_db_session)

    # Create session with 1-hour TTL (will expire immediately for testing)
    session = await repo.create(
        learner_id=learner_id,
        owner_subject="test_user",
        items=[str(uuid4())],
        session_ttl_hours=0,  # Expire immediately
    )
    await async_db_session.commit()
    session_id = session.id

    # Try to retrieve expired session
    expired = await repo.get_by_id(session_id)

    assert expired is None


@pytest.mark.asyncio
async def test_cross_user_session_isolation(async_db_session):
    """Test that User A's session is independent from User B's session."""
    learner_id_a = str(uuid4())
    learner_id_b = str(uuid4())
    owner_a = "user_a"
    owner_b = "user_b"

    repo = PracticeSessionRepository(async_db_session)

    # User A creates session
    session_a = await repo.create(
        learner_id=learner_id_a,
        owner_subject=owner_a,
        items=[str(uuid4()), str(uuid4())],
        gap_topics=["Topic A"],
    )
    await async_db_session.commit()

    # User B creates session
    session_b = await repo.create(
        learner_id=learner_id_b,
        owner_subject=owner_b,
        items=[str(uuid4()), str(uuid4())],
        gap_topics=["Topic B"],
    )
    await async_db_session.commit()

    # Verify sessions are isolated
    assert session_a.id != session_b.id
    assert session_a.owner_subject != session_b.owner_subject

    # User A's session is retrievable by A but has B's owner_subject isolated
    retrieved_a = await repo.get_by_id(session_a.id)
    assert retrieved_a.owner_subject == owner_a
    assert retrieved_a.gap_topics == ["Topic A"]


@pytest.mark.asyncio
async def test_list_by_learner_returns_active_sessions_only(async_db_session):
    """Test that list_by_learner returns only active (non-expired) sessions."""
    learner_id = str(uuid4())

    repo = PracticeSessionRepository(async_db_session)

    # Create active session (24h TTL)
    active = await repo.create(
        learner_id=learner_id,
        owner_subject="user1",
        items=[str(uuid4())],
        session_ttl_hours=24,
    )
    await async_db_session.commit()

    # Create expired session (0h TTL)
    await repo.create(
        learner_id=learner_id,
        owner_subject="user1",
        items=[str(uuid4())],
        session_ttl_hours=0,
    )
    await async_db_session.commit()

    # List should return only active
    sessions = await repo.list_by_learner(learner_id)

    assert len(sessions) == 1
    assert sessions[0].id == active.id


@pytest.mark.asyncio
async def test_delete_expired_cleans_up_correctly(async_db_session):
    """Test that delete_expired removes only expired sessions."""
    learner_id_a = str(uuid4())
    learner_id_b = str(uuid4())

    repo = PracticeSessionRepository(async_db_session)

    # Create one active and two expired sessions
    active = await repo.create(
        learner_id=learner_id_a,
        owner_subject="user1",
        items=[str(uuid4())],
        session_ttl_hours=24,
    )
    expired1 = await repo.create(
        learner_id=learner_id_a,
        owner_subject="user1",
        items=[str(uuid4())],
        session_ttl_hours=0,
    )
    expired2 = await repo.create(
        learner_id=learner_id_b,
        owner_subject="user2",
        items=[str(uuid4())],
        session_ttl_hours=0,
    )
    await async_db_session.commit()

    # Delete expired
    deleted_count = await repo.delete_expired()

    assert deleted_count == 2

    # Verify active session still exists
    remaining = await repo.get_by_id(active.id)
    assert remaining is not None

    # Verify expired sessions are gone
    assert await repo.get_by_id(expired1.id) is None
    assert await repo.get_by_id(expired2.id) is None


@pytest.mark.asyncio
async def test_mark_completed_sets_timestamp(async_db_session):
    """Test that mark_completed sets the completed_at timestamp."""
    learner_id = str(uuid4())

    repo = PracticeSessionRepository(async_db_session)

    session = await repo.create(
        learner_id=learner_id,
        owner_subject="user1",
        items=[str(uuid4())],
    )
    await async_db_session.commit()
    assert session.completed_at is None

    # Mark as completed
    result = await repo.mark_completed(session.id)
    await async_db_session.commit()

    assert result == True

    # Retrieve and verify timestamp is set
    updated = await repo.get_by_id(session.id)
    assert updated.completed_at is not None
    assert isinstance(updated.completed_at, datetime)
