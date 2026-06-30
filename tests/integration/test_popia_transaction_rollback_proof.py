from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.domain.consent import ConsentRecord, ConsentState
from app.services.popia_transactional_lifecycle import TransactionalPOPIAConsentLifecycleService


@pytest.fixture
async def tx_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
                CREATE TABLE consent_transition_probe (
                    id TEXT PRIMARY KEY,
                    learner_id TEXT NOT NULL,
                    guardian_id TEXT NOT NULL,
                    state TEXT NOT NULL
                )
                """
            )
        )
        await conn.execute(
            text(
                """
                CREATE TABLE consent_audit_probe (
                    id TEXT PRIMARY KEY,
                    consent_id TEXT NOT NULL,
                    action TEXT NOT NULL
                )
                """
            )
        )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


async def _count(session, table: str) -> int:
    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
    return int(result.scalar_one())


class ProbeConsentService:
    def __init__(self, session, *, fail: bool = False):
        self.session = session
        self.fail = fail

    async def grant(self, *, guardian_id, learner_id, privacy_notice_version="v1", **kwargs):
        if self.fail:
            raise RuntimeError("consent write failed")
        record = ConsentRecord(
            id=uuid.uuid4(),
            learner_id=learner_id,
            guardian_id=guardian_id,
            privacy_notice_version=privacy_notice_version,
            state=ConsentState.GRANTED,
            granted_at=datetime.now(timezone.utc),
            expires_at=None,
            withdrawn_at=None,
            denial_reason=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        await self.session.execute(
            text(
                "INSERT INTO consent_transition_probe (id, learner_id, guardian_id, state) "
                "VALUES (:id, :learner_id, :guardian_id, :state)"
            ),
            {
                "id": str(record.id),
                "learner_id": str(record.learner_id),
                "guardian_id": str(record.guardian_id),
                "state": record.state.value,
            },
        )
        return record


class ProbeAuditService:
    def __init__(self, session, *, fail: bool = False):
        self.session = session
        self.fail = fail

    async def record_consent_lifecycle_event(self, *, action, consent_record, **kwargs):
        if self.fail:
            raise RuntimeError("audit write failed")
        await self.session.execute(
            text("INSERT INTO consent_audit_probe (id, consent_id, action) VALUES (:id, :consent_id, :action)"),
            {"id": str(uuid.uuid4()), "consent_id": str(consent_record.id), "action": action},
        )


@pytest.mark.asyncio
async def test_consent_transition_and_audit_write_commit_atomically(tx_session):
    service = TransactionalPOPIAConsentLifecycleService(
        db=tx_session,
        consent_service=ProbeConsentService(tx_session),
        audit_service=ProbeAuditService(tx_session),
    )

    await service.grant(guardian_id=uuid.uuid4(), learner_id=uuid.uuid4(), privacy_notice_version="v1")

    assert await _count(tx_session, "consent_transition_probe") == 1
    assert await _count(tx_session, "consent_audit_probe") == 1


@pytest.mark.asyncio
async def test_audit_failure_rolls_back_consent_transition(tx_session):
    service = TransactionalPOPIAConsentLifecycleService(
        db=tx_session,
        consent_service=ProbeConsentService(tx_session),
        audit_service=ProbeAuditService(tx_session, fail=True),
    )

    with pytest.raises(RuntimeError, match="audit write failed"):
        await service.grant(guardian_id=uuid.uuid4(), learner_id=uuid.uuid4(), privacy_notice_version="v1")

    assert await _count(tx_session, "consent_transition_probe") == 0
    assert await _count(tx_session, "consent_audit_probe") == 0


@pytest.mark.asyncio
async def test_consent_failure_does_not_write_audit_orphan(tx_session):
    service = TransactionalPOPIAConsentLifecycleService(
        db=tx_session,
        consent_service=ProbeConsentService(tx_session, fail=True),
        audit_service=ProbeAuditService(tx_session),
    )

    with pytest.raises(RuntimeError, match="consent write failed"):
        await service.grant(guardian_id=uuid.uuid4(), learner_id=uuid.uuid4(), privacy_notice_version="v1")

    assert await _count(tx_session, "consent_transition_probe") == 0
    assert await _count(tx_session, "consent_audit_probe") == 0
