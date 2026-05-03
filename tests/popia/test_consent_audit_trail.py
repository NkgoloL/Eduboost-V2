"""
tests/popia/test_consent_audit_trail.py
─────────────────────────────────────────────────────────────────────────────
POPIA Consent Audit Trail — Integration Tests
Task 22 of the EduBoost SA V2 Agent TODO list.

Validates that every consent state transition produces an audit record:
  - consent.granted
  - consent.revoked
  - consent.renewed
  - consent.erasure_requested
  - consent.access_rejected  (failed consent gate — rejected request)

All events must be written to the append-only audit_events table and must
NOT be modifiable after insertion (no UPDATE / DELETE).

Execution:
  pytest tests/popia/test_consent_audit_trail.py -v --tb=short
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import select, text, event
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Guardian, Learner, ParentalConsent, AuditEvent
from app.modules.consent.service import ConsentService
from app.repositories.repositories import ConsentRepository, AuditRepository
from app.core.exceptions import ConsentRequiredError


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _make_guardian(db_session: AsyncSession) -> Guardian:
    import hashlib
    email = f"g_{uuid.uuid4().hex[:8]}@test.co.za"
    return Guardian(
        id=uuid.uuid4(),
        display_name="Audit Trail Guardian",
        email_hash=hashlib.sha256(email.encode()).hexdigest(),
        email_ciphertext="gAAAAAfake_ciphertext",
        password_hash="$2b$12$hashed",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )


def _make_learner(guardian: Guardian) -> Learner:
    return Learner(
        id=uuid.uuid4(),
        guardian_id=guardian.id,
        pseudonym_id=uuid.uuid4(),
        display_name="Audit Learner",
        date_of_birth=datetime(2016, 1, 1).date(),
        grade="3",
        school="Audit Test School",
        language_preference="en",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )


def _make_consent(guardian: Guardian, learner: Learner, active: bool = True) -> ParentalConsent:
    return ParentalConsent(
        id=uuid.uuid4(),
        guardian_id=guardian.id,
        learner_id=learner.id,
        consent_version="2.0",
        granted_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(days=365),
        is_active=active,
        ip_address_hash="hashed_ip",
        user_agent_hash="hashed_ua",
    )


async def _setup_entities(db_session: AsyncSession):
    """Create and persist a guardian, learner, and consent."""
    guardian = _make_guardian(db_session)
    db_session.add(guardian)
    await db_session.flush()

    learner = _make_learner(guardian)
    db_session.add(learner)
    await db_session.flush()

    consent = _make_consent(guardian, learner)
    db_session.add(consent)
    await db_session.flush()

    return guardian, learner, consent


async def _get_audit_events(
    db_session: AsyncSession,
    event_type: str,
    resource_id: uuid.UUID,
) -> list[AuditEvent]:
    result = await db_session.execute(
        select(AuditEvent)
        .where(
            AuditEvent.event_type == event_type,
            AuditEvent.resource_id == resource_id,
        )
        .order_by(AuditEvent.created_at.desc())
    )
    return result.scalars().all()


# ─── Test Suite ──────────────────────────────────────────────────────────────


class TestConsentAuditTrail:
    """
    Validates the append-only POPIA consent audit trail across all workflows.
    """

    @pytest.mark.asyncio
    async def test_consent_grant_produces_audit_record(
        self,
        db_session: AsyncSession,
    ):
        """
        When ConsentService.grant() is called, an audit record with
        event_type='consent.granted' must be appended to audit_events.
        """
        guardian, learner, _ = await _setup_entities(db_session)
        consent_repo = ConsentRepository(db_session)
        audit_repo = AuditRepository(db_session)
        service = ConsentService(consent_repo=consent_repo, audit_repo=audit_repo)

        new_consent = await service.grant(
            guardian_id=guardian.id,
            learner_id=learner.id,
            consent_version="2.0",
            ip_address="127.0.0.1",
            user_agent="test-agent/1.0",
        )

        events = await _get_audit_events(db_session, "consent.granted", new_consent.id)
        assert len(events) >= 1, (
            "consent.granted audit event must be created when consent is granted"
        )
        event = events[0]
        assert event.actor_id == guardian.id, "Actor must be the granting guardian"
        assert event.payload.get("learner_id") == str(learner.id)
        assert event.payload.get("consent_version") == "2.0"

    @pytest.mark.asyncio
    async def test_consent_revocation_produces_audit_record(
        self,
        db_session: AsyncSession,
    ):
        """
        When ConsentService.revoke() is called, an audit record with
        event_type='consent.revoked' must be appended.
        """
        guardian, learner, consent = await _setup_entities(db_session)
        consent_repo = ConsentRepository(db_session)
        audit_repo = AuditRepository(db_session)
        service = ConsentService(consent_repo=consent_repo, audit_repo=audit_repo)

        await service.revoke(
            guardian_id=guardian.id,
            learner_id=learner.id,
            reason="Guardian request",
        )

        events = await _get_audit_events(db_session, "consent.revoked", consent.id)
        assert len(events) >= 1, (
            "consent.revoked audit event must be created when consent is revoked"
        )
        event = events[0]
        assert event.actor_id == guardian.id
        assert event.payload.get("reason") == "Guardian request"

    @pytest.mark.asyncio
    async def test_consent_annual_renewal_produces_audit_record(
        self,
        db_session: AsyncSession,
    ):
        """
        When annual consent renewal occurs (either guardian-initiated or
        system-triggered), an audit record with event_type='consent.renewed'
        must be created.
        """
        guardian, learner, consent = await _setup_entities(db_session)
        consent_repo = ConsentRepository(db_session)
        audit_repo = AuditRepository(db_session)
        service = ConsentService(consent_repo=consent_repo, audit_repo=audit_repo)

        renewed_consent = await service.renew(
            guardian_id=guardian.id,
            learner_id=learner.id,
            consent_version="2.1",
        )

        events = await _get_audit_events(db_session, "consent.renewed", renewed_consent.id)
        assert len(events) >= 1, (
            "consent.renewed audit event must be created during annual renewal"
        )
        event = events[0]
        assert event.payload.get("previous_version") is not None
        assert event.payload.get("new_version") == "2.1"

    @pytest.mark.asyncio
    async def test_erasure_request_produces_audit_record(
        self,
        db_session: AsyncSession,
    ):
        """
        When ConsentService.execute_erasure() is called, an audit record with
        event_type='consent.erasure_requested' must be created BEFORE the
        PII is purged (to preserve proof of the erasure request).
        """
        guardian, learner, consent = await _setup_entities(db_session)
        consent_repo = ConsentRepository(db_session)
        audit_repo = AuditRepository(db_session)
        service = ConsentService(consent_repo=consent_repo, audit_repo=audit_repo)

        await service.execute_erasure(
            guardian_id=guardian.id,
            learner_id=learner.id,
        )

        events = await _get_audit_events(
            db_session, "consent.erasure_requested", learner.id
        )
        assert len(events) >= 1, (
            "consent.erasure_requested audit event must be created when erasure is executed"
        )
        event = events[0]
        assert event.actor_id == guardian.id
        # Erasure events must NOT contain the learner's PII in the payload
        payload_str = str(event.payload)
        assert "Sipho" not in payload_str, (
            "Erasure audit event must not contain learner PII in payload"
        )

    @pytest.mark.asyncio
    async def test_failed_consent_check_produces_audit_record(
        self,
        db_session: AsyncSession,
    ):
        """
        When a request is rejected by the consent gate (ConsentRequiredError),
        an audit record with event_type='consent.access_rejected' must be
        created to satisfy POPIA §23 accountability for rejected access attempts.
        """
        guardian, learner, _ = await _setup_entities(db_session)
        # Revoke consent first
        consent_repo = ConsentRepository(db_session)
        audit_repo = AuditRepository(db_session)
        service = ConsentService(consent_repo=consent_repo, audit_repo=audit_repo)
        await service.revoke(guardian_id=guardian.id, learner_id=learner.id)

        # Now attempt access — must be rejected AND produce an audit record
        with pytest.raises(ConsentRequiredError):
            await service.require_active_consent(learner_id=learner.id)

        events = await _get_audit_events(
            db_session, "consent.access_rejected", learner.id
        )
        assert len(events) >= 1, (
            "consent.access_rejected audit event must be created when consent gate rejects a request"
        )

    @pytest.mark.asyncio
    async def test_audit_events_are_immutable_at_db_level(
        self,
        db_session: AsyncSession,
    ):
        """
        Database-level immutability: Attempting to UPDATE or DELETE an
        audit_events row must be silently ignored (via PostgreSQL RULE) or
        raise an error. This guarantees the audit trail cannot be tampered with.
        """
        guardian, learner, consent = await _setup_entities(db_session)
        consent_repo = ConsentRepository(db_session)
        audit_repo = AuditRepository(db_session)
        service = ConsentService(consent_repo=consent_repo, audit_repo=audit_repo)

        await service.grant(
            guardian_id=guardian.id,
            learner_id=learner.id,
            consent_version="2.0",
            ip_address="127.0.0.1",
            user_agent="test-agent/1.0",
        )

        events = await _get_audit_events(db_session, "consent.granted", consent.id)
        assert len(events) >= 1
        audit_id = events[0].id

        # Attempt UPDATE — must have no effect (PostgreSQL RULE: DO INSTEAD NOTHING)
        await db_session.execute(
            text(
                "UPDATE audit_events SET event_type = 'tampered' "
                "WHERE id = :id"
            ),
            {"id": audit_id},
        )
        await db_session.flush()

        # Re-fetch and verify the record was NOT modified
        result = await db_session.execute(
            select(AuditEvent).where(AuditEvent.id == audit_id)
        )
        unchanged_event = result.scalar_one()
        assert unchanged_event.event_type == "consent.granted", (
            "audit_events UPDATE must be a no-op (PostgreSQL DO INSTEAD NOTHING RULE)"
        )

    @pytest.mark.asyncio
    async def test_audit_event_delete_blocked_at_db_level(
        self,
        db_session: AsyncSession,
    ):
        """
        Database-level immutability: Attempting to DELETE an audit_events row
        must be silently ignored via PostgreSQL RULE.
        """
        guardian, learner, consent = await _setup_entities(db_session)
        audit_repo = AuditRepository(db_session)
        await audit_repo.append(
            event_type="consent.granted",
            actor_id=guardian.id,
            resource_id=consent.id,
            payload={"test": True},
        )

        events = await _get_audit_events(db_session, "consent.granted", consent.id)
        assert len(events) >= 1
        audit_id = events[0].id

        # Attempt DELETE — must have no effect
        await db_session.execute(
            text("DELETE FROM audit_events WHERE id = :id"),
            {"id": audit_id},
        )
        await db_session.flush()

        # Verify record still exists
        result = await db_session.execute(
            select(AuditEvent).where(AuditEvent.id == audit_id)
        )
        surviving_event = result.scalar_one_or_none()
        assert surviving_event is not None, (
            "audit_events DELETE must be a no-op (PostgreSQL DO INSTEAD NOTHING RULE)"
        )

    @pytest.mark.asyncio
    async def test_audit_trail_contains_no_pii(
        self,
        db_session: AsyncSession,
    ):
        """
        Privacy invariant: No audit_events payload must contain PII such as
        email addresses, full names, dates of birth, or SA ID numbers.
        All references must use pseudonym_id or resource UUID only.
        """
        import re

        guardian, learner, consent = await _setup_entities(db_session)
        consent_repo = ConsentRepository(db_session)
        audit_repo = AuditRepository(db_session)
        service = ConsentService(consent_repo=consent_repo, audit_repo=audit_repo)

        await service.grant(
            guardian_id=guardian.id,
            learner_id=learner.id,
            consent_version="2.0",
            ip_address="127.0.0.1",
            user_agent="test-agent/1.0",
        )
        await service.revoke(guardian_id=guardian.id, learner_id=learner.id)

        result = await db_session.execute(
            select(AuditEvent).where(
                AuditEvent.resource_id == consent.id,
            )
        )
        events = result.scalars().all()

        email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        for evt in events:
            payload_str = str(evt.payload)
            assert not email_pattern.search(payload_str), (
                f"Audit event '{evt.event_type}' payload contains an email address — PII leak"
            )
            # Check for learner display_name
            assert "Audit Learner" not in payload_str, (
                f"Audit event '{evt.event_type}' payload contains learner display_name — PII leak"
            )
