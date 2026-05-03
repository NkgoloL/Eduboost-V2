"""
tests/unit/test_audit_repository.py
─────────────────────────────────────────────────────────────────────────────
Task 23: AuditRepository unit tests

Validates:
  - append() correctly persists events
  - UPDATE on audit_events is a no-op (PostgreSQL RULE)
  - DELETE on audit_events is a no-op (PostgreSQL RULE)
  - PII in payload is rejected at the repository layer
  - get_by_resource() and get_by_actor() query correctly
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditEvent
from app.repositories.audit_repository import AuditRepository


class TestAuditRepositoryAppend:

    @pytest.mark.asyncio
    async def test_append_creates_record(self, db_session: AsyncSession):
        """append() must persist an AuditEvent with correct fields."""
        repo = AuditRepository(db_session)
        actor_id = uuid.uuid4()
        resource_id = uuid.uuid4()

        event = await repo.append(
            event_type="consent.granted",
            actor_id=actor_id,
            resource_id=resource_id,
            payload={"consent_version": "2.0", "pseudonym_id": str(uuid.uuid4())},
        )

        assert event.id is not None
        assert event.event_type == "consent.granted"
        assert event.actor_id == actor_id
        assert event.resource_id == resource_id
        assert event.payload["consent_version"] == "2.0"

    @pytest.mark.asyncio
    async def test_append_sets_created_at_via_db(self, db_session: AsyncSession):
        """created_at must be set by the database server, not the application."""
        repo = AuditRepository(db_session)
        event = await repo.append(
            event_type="system.test",
            payload={"test": True},
        )
        # After flush, created_at should be populated by the DB
        assert event.created_at is not None

    @pytest.mark.asyncio
    async def test_append_without_actor_or_resource(self, db_session: AsyncSession):
        """System events may have no actor_id or resource_id — must be accepted."""
        repo = AuditRepository(db_session)
        event = await repo.append(
            event_type="system.startup",
            payload={"app_version": "0.2.0-rc1"},
        )
        assert event.actor_id is None
        assert event.resource_id is None

    @pytest.mark.asyncio
    async def test_append_raises_on_empty_event_type(self, db_session: AsyncSession):
        repo = AuditRepository(db_session)
        with pytest.raises(ValueError, match="event_type"):
            await repo.append(event_type="", payload={})

    @pytest.mark.asyncio
    async def test_append_raises_on_pii_fields_in_payload(self, db_session: AsyncSession):
        """PII field names in payload must be rejected at the repository layer."""
        repo = AuditRepository(db_session)

        with pytest.raises(ValueError, match="PII"):
            await repo.append(
                event_type="consent.granted",
                payload={"email": "user@example.com", "consent_version": "2.0"},
            )

        with pytest.raises(ValueError, match="PII"):
            await repo.append(
                event_type="learner.erased",
                payload={"date_of_birth": "2016-01-01"},
            )

        with pytest.raises(ValueError, match="PII"):
            await repo.append(
                event_type="consent.granted",
                payload={"display_name": "Sipho Dlamini"},
            )


class TestAuditImmutability:

    @pytest.mark.asyncio
    async def test_update_audit_event_is_noop(self, db_session: AsyncSession):
        """
        PostgreSQL RULE audit_events_no_update must make UPDATE a no-op.
        The event_type must remain unchanged after an attempted UPDATE.
        """
        repo = AuditRepository(db_session)
        event = await repo.append(
            event_type="consent.granted",
            payload={"original": True},
        )

        # Attempt direct SQL UPDATE
        await db_session.execute(
            text("UPDATE audit_events SET event_type = 'tampered' WHERE id = :id"),
            {"id": event.id},
        )
        await db_session.flush()

        # Reload and verify no change
        result = await db_session.execute(
            select(AuditEvent).where(AuditEvent.id == event.id)
        )
        unchanged = result.scalar_one()
        assert unchanged.event_type == "consent.granted", (
            "UPDATE on audit_events must be a no-op due to PostgreSQL RULE"
        )

    @pytest.mark.asyncio
    async def test_delete_audit_event_is_noop(self, db_session: AsyncSession):
        """
        PostgreSQL RULE audit_events_no_delete must make DELETE a no-op.
        The record must still exist after an attempted DELETE.
        """
        repo = AuditRepository(db_session)
        event = await repo.append(
            event_type="consent.revoked",
            payload={"reason": "test"},
        )

        # Attempt direct SQL DELETE
        await db_session.execute(
            text("DELETE FROM audit_events WHERE id = :id"),
            {"id": event.id},
        )
        await db_session.flush()

        # Reload and verify record still exists
        result = await db_session.execute(
            select(AuditEvent).where(AuditEvent.id == event.id)
        )
        surviving = result.scalar_one_or_none()
        assert surviving is not None, (
            "DELETE on audit_events must be a no-op due to PostgreSQL RULE"
        )


class TestAuditRepositoryQueries:

    @pytest.mark.asyncio
    async def test_get_by_resource(self, db_session: AsyncSession):
        repo = AuditRepository(db_session)
        resource_id = uuid.uuid4()
        other_resource_id = uuid.uuid4()

        await repo.append("consent.granted", payload={}, resource_id=resource_id)
        await repo.append("consent.revoked", payload={}, resource_id=resource_id)
        await repo.append("consent.granted", payload={}, resource_id=other_resource_id)

        events = await repo.get_by_resource(resource_id)
        assert len(events) == 2
        assert all(e.resource_id == resource_id for e in events)

    @pytest.mark.asyncio
    async def test_get_by_resource_filtered_by_event_type(self, db_session: AsyncSession):
        repo = AuditRepository(db_session)
        resource_id = uuid.uuid4()

        await repo.append("consent.granted", payload={}, resource_id=resource_id)
        await repo.append("consent.revoked", payload={}, resource_id=resource_id)

        events = await repo.get_by_resource(resource_id, event_type="consent.granted")
        assert len(events) == 1
        assert events[0].event_type == "consent.granted"

    @pytest.mark.asyncio
    async def test_get_by_actor(self, db_session: AsyncSession):
        repo = AuditRepository(db_session)
        actor_id = uuid.uuid4()

        await repo.append("consent.granted", payload={}, actor_id=actor_id)
        await repo.append("consent.revoked", payload={}, actor_id=actor_id)

        events = await repo.get_by_actor(actor_id)
        assert len(events) == 2
        assert all(e.actor_id == actor_id for e in events)
