from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v2 import app
from app.api_v2_routers import learners as learners_router
from app.core.database import get_db
from app.core.exceptions import ConsentRequiredError
from app.core.security import create_access_token
from app.models import (
    AuditEvent,
    DiagnosticSession,
    Guardian,
    LearnerProfile,
    Lesson,
    ParentalConsent,
    UserRole,
)
from app.modules.consent.service import ConsentService


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def guardian_record(db_session: AsyncSession) -> tuple[Guardian, str]:
    raw_email = "guardian.right.to.erasure@test.co.za"
    guardian = Guardian(
        email_hash="guardian-right-to-erasure-hash",
        email_encrypted="gAAAAABguardian-erasure-ciphertext",
        display_name="Guardian Erasure",
        password_hash="not-used-in-test",
        role=UserRole.PARENT,
    )
    db_session.add(guardian)
    await db_session.flush()
    return guardian, raw_email


@pytest_asyncio.fixture
async def learner_record(
    db_session: AsyncSession,
    guardian_record: tuple[Guardian, str],
) -> LearnerProfile:
    guardian, _ = guardian_record
    learner = LearnerProfile(
        guardian_id=guardian.id,
        display_name="Sipho Dlamini",
        grade=3,
        language="en",
    )
    db_session.add(learner)
    await db_session.flush()
    return learner


@pytest_asyncio.fixture
async def active_consent(
    db_session: AsyncSession,
    guardian_record: tuple[Guardian, str],
    learner_record: LearnerProfile,
) -> ParentalConsent:
    guardian, _ = guardian_record
    consent = ParentalConsent(
        guardian_id=guardian.id,
        learner_id=learner_record.id,
        policy_version="2.0",
        granted_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=365),
        ip_address_hash="hashed-ip",
    )
    db_session.add(consent)
    await db_session.flush()
    return consent


@pytest_asyncio.fixture
async def lesson_record(
    db_session: AsyncSession,
    learner_record: LearnerProfile,
) -> Lesson:
    lesson = Lesson(
        learner_id=learner_record.id,
        grade=3,
        subject="Mathematics",
        topic="Addition",
        language="en",
        content="Count and add the apples together.",
    )
    db_session.add(lesson)
    await db_session.flush()
    return lesson


@pytest_asyncio.fixture
async def diagnostic_record(
    db_session: AsyncSession,
    learner_record: LearnerProfile,
) -> DiagnosticSession:
    diagnostic = DiagnosticSession(
        learner_id=learner_record.id,
        responses={"item-1": True},
        theta_before=0.1,
        theta_after=0.4,
        completed_at=datetime.now(UTC),
    )
    db_session.add(diagnostic)
    await db_session.flush()
    return diagnostic


@pytest.mark.asyncio
async def test_right_to_erasure_flow(
    client: AsyncClient,
    db_session: AsyncSession,
    guardian_record: tuple[Guardian, str],
    learner_record: LearnerProfile,
    active_consent: ParentalConsent,
    lesson_record: Lesson,
    diagnostic_record: DiagnosticSession,
    monkeypatch: pytest.MonkeyPatch,
):
    guardian, raw_email = guardian_record
    purge_mock = AsyncMock()
    monkeypatch.setattr(learners_router, "enqueue_data_purge", purge_mock)

    token = create_access_token(guardian.id, UserRole.PARENT)
    response = await client.delete(
        f"/api/v2/learners/{learner_record.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204

    consent = await db_session.scalar(
        select(ParentalConsent).where(ParentalConsent.id == active_consent.id)
    )
    assert consent is not None
    assert consent.revoked_at is not None
    assert consent.is_active is False

    learner = await db_session.scalar(
        select(LearnerProfile).where(LearnerProfile.id == learner_record.id)
    )
    assert learner is not None
    assert learner.is_deleted is True
    assert learner.deletion_requested_at is not None
    assert learner.display_name == "[erased]"

    assert guardian.email_encrypted != raw_email
    assert raw_email not in guardian.email_encrypted

    purge_mock.assert_awaited_once_with(learner_record.id, learner_record.pseudonym_id)

    with pytest.raises(ConsentRequiredError):
        await ConsentService(db_session).require_active_consent(
            learner_record.id,
            actor_id=guardian.id,
        )

    audit_events = (
        await db_session.execute(
            select(AuditEvent)
            .where(AuditEvent.event_type == "learner.erased")
            .order_by(AuditEvent.created_at.desc())
        )
    ).scalars().all()
    assert len(audit_events) == 1
    assert str(audit_events[0].resource_id) == learner_record.id
    assert audit_events[0].payload["learner_id"] == learner_record.id

