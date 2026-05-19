from __future__ import annotations

import pytest
from sqlalchemy import Column, DateTime, ForeignKey, MetaData, String, Table, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.services.auth_transactional_registration import (
    AuthRegistrationInput,
    AuthRegistrationTransactionError,
    TransactionalAuthRegistrationService,
)


pytestmark = pytest.mark.asyncio


metadata = MetaData()

users = Table(
    "auth_tx_users",
    metadata,
    Column("id", String, primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("password_hash", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

guardians = Table(
    "auth_tx_guardians",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, ForeignKey("auth_tx_users.id"), nullable=False),
    Column("name", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

learners = Table(
    "auth_tx_learners",
    metadata,
    Column("id", String, primary_key=True),
    Column("guardian_id", String, ForeignKey("auth_tx_guardians.id"), nullable=False),
    Column("name", String, nullable=False),
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


async def _count(session, table) -> int:
    result = await session.execute(select(func.count()).select_from(table))
    return int(result.scalar_one())


def _service(session) -> TransactionalAuthRegistrationService:
    return TransactionalAuthRegistrationService(
        session,
        users_table=users,
        guardians_table=guardians,
        learners_table=learners,
    )


async def test_auth_registration_success_commits_all_rows(session):
    service = _service(session)

    result = await service.register(
        AuthRegistrationInput(
            email="guardian@example.test",
            name="Guardian",
            password_hash="hash",
            learner_name="Learner",
        )
    )

    assert result.email == "guardian@example.test"
    assert await _count(session, users) == 1
    assert await _count(session, guardians) == 1
    assert await _count(session, learners) == 1


@pytest.mark.parametrize(
    "flag",
    ["fail_after_user", "fail_after_guardian", "fail_after_learner"],
)
async def test_auth_registration_failure_rolls_back_all_rows(session, flag):
    service = _service(session)

    with pytest.raises(AuthRegistrationTransactionError):
        await service.register(
            AuthRegistrationInput(
                email=f"{flag}@example.test",
                name="Guardian",
                password_hash="hash",
                learner_name="Learner",
                **{flag: True},
            )
        )

    assert await _count(session, users) == 0
    assert await _count(session, guardians) == 0
    assert await _count(session, learners) == 0


async def test_multiple_successful_registrations_do_not_share_partial_state(session):
    service = _service(session)

    await service.register(
        AuthRegistrationInput(
            email="first@example.test",
            name="First",
            password_hash="hash-1",
            learner_name="Learner One",
        )
    )

    with pytest.raises(AuthRegistrationTransactionError):
        await service.register(
            AuthRegistrationInput(
                email="second@example.test",
                name="Second",
                password_hash="hash-2",
                learner_name="Learner Two",
                fail_after_guardian=True,
            )
        )

    assert await _count(session, users) == 1
    assert await _count(session, guardians) == 1
    assert await _count(session, learners) == 1
