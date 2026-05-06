from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConsentRequiredError
from app.models import AuditEvent, Guardian, LearnerProfile, UserRole
from app.modules.consent.service import ConsentService


@pytest_asyncio.fixture
async def guardian(db_session: AsyncSession) -> Guardian:
    record = Guardian(
        email_hash="consent-audit-guardian-hash",
        email_encrypted="gAAAAABconsent-audit-ciphertext",
        display_name="Guardian Audit",
        password_hash="not-used-in-test",
        role=UserRole.PARENT,
    )
    db_session.add(record)
    await db_session.flush()
    return record


@pytest_asyncio.fixture
async def learner(db_session: AsyncSession, guardian: Guardian) -> LearnerProfile:
    record = LearnerProfile(
        guardian_id=guardian.id,
        display_name="Lerato Audit",
        grade=4,
        language="en",
    )
    db_session.add(record)
    await db_session.flush()
    return record


async def _event_types(db_session: AsyncSession) -> list[str]:
    result = await db_session.execute(select(AuditEvent.event_type).order_by(AuditEvent.created_at.asc()))
    return list(result.scalars().all())


@pytest.mark.asyncio
async def test_grant_writes_audit_event(
    db_session: AsyncSession,
    guardian: Guardian,
    learner: LearnerProfile,
):
    service = ConsentService(db_session)
    await service.grant(guardian.id, learner.id, "2.0", ip_hash="hashed-ip")

    assert "consent.granted" in await _event_types(db_session)


@pytest.mark.asyncio
async def test_revoke_writes_audit_event(
    db_session: AsyncSession,
    guardian: Guardian,
    learner: LearnerProfile,
):
    service = ConsentService(db_session)
    await service.grant(guardian.id, learner.id, "2.0")
    await service.revoke(learner.id, guardian_id=guardian.id, reason="guardian_request")

    events = await _event_types(db_session)
    assert "consent.granted" in events
    assert "consent.revoked" in events


@pytest.mark.asyncio
async def test_renew_writes_audit_event(
    db_session: AsyncSession,
    guardian: Guardian,
    learner: LearnerProfile,
):
    service = ConsentService(db_session)
    await service.grant(guardian.id, learner.id, "2.0")
    renewed = await service.renew(guardian.id, learner.id, "2.1")

    events = await _event_types(db_session)
    assert renewed.policy_version == "2.1"
    assert "consent.renewed" in events


@pytest.mark.asyncio
async def test_execute_erasure_writes_erasure_audit_event(
    db_session: AsyncSession,
    guardian: Guardian,
    learner: LearnerProfile,
):
    service = ConsentService(db_session)
    await service.grant(guardian.id, learner.id, "2.0")
    await service.execute_erasure(guardian.id, learner.id)

    events = await _event_types(db_session)
    assert "consent.erasure_requested" in events


@pytest.mark.asyncio
async def test_missing_consent_writes_rejected_access_audit_event(
    db_session: AsyncSession,
    guardian: Guardian,
    learner: LearnerProfile,
):
    service = ConsentService(db_session)

    with pytest.raises(ConsentRequiredError):
        await service.require_active_consent(learner.id, actor_id=guardian.id)

    result = await db_session.execute(
        select(AuditEvent).where(AuditEvent.event_type == "consent.access_rejected")
    )
    event = result.scalar_one()
    assert str(event.actor_id) == guardian.id
    assert str(event.resource_id) == learner.id
    assert event.payload["reason"] == "missing_or_expired"

