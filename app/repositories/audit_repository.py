"""
app/repositories/audit_repository.py
─────────────────────────────────────────────────────────────────────────────
Task 23: V2 Append-Only Audit Repository

Replaces the RabbitMQ/Redis stream dependency (Fourth Estate legacy) with a
direct, async PostgreSQL append to the audit_events table created in migration
0006_v2_audit_events.py.

Design invariants:
  - append() is the ONLY write method. No update(), no delete().
  - All payloads must be pre-screened for PII before calling append().
  - actor_id and resource_id are optional (system events have no actor).
  - created_at is set by the database server clock, never the application.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import uuid
import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditEvent

logger = logging.getLogger(__name__)


class AuditRepository:
    """
    Append-only repository for the audit_events table.

    Injection pattern:
        audit_repo = AuditRepository(session)
        await audit_repo.append(
            event_type="consent.granted",
            actor_id=guardian_id,
            resource_id=consent_id,
            payload={"learner_id": str(learner_id), "consent_version": "2.0"},
        )
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ─── Write ───────────────────────────────────────────────────────────────

    async def append(
        self,
        event_type: str,
        payload: dict[str, Any],
        actor_id: Optional[UUID] = None,
        resource_id: Optional[UUID] = None,
    ) -> AuditEvent:
        """
        Append an immutable audit event to the audit_events table.

        Args:
            event_type:   Dot-notation identifier, e.g. 'consent.granted'.
                          Must be non-empty and follow the pattern:
                          '<domain>.<action>' or '<domain>.<entity>.<action>'.
            payload:      Arbitrary JSON-serialisable dict. MUST NOT contain PII.
                          Use pseudonym_id, resource UUIDs, and anonymised fields only.
            actor_id:     UUID of the entity that triggered the event.
                          None for system-generated events.
            resource_id:  UUID of the primary resource this event concerns.
                          None for events without a specific resource.

        Returns:
            The newly created AuditEvent ORM instance (id and created_at are
            populated after flush).

        Raises:
            ValueError: If event_type is empty or payload contains suspicious
                        PII-like fields (email, date_of_birth, full_name).
        """
        if not event_type or not event_type.strip():
            raise ValueError("event_type must be a non-empty string")

        self._validate_payload_no_pii(event_type, payload)

        audit_event = AuditEvent(
            id=uuid.uuid4(),
            event_type=event_type,
            actor_id=actor_id,
            resource_id=resource_id,
            payload=payload,
            # created_at intentionally NOT set here — database sets it via NOW()
        )

        self._session.add(audit_event)
        await self._session.flush()

        logger.info(
            "audit_event.appended",
            extra={
                "event_type": event_type,
                "audit_id": str(audit_event.id),
                "actor_id": str(actor_id) if actor_id else None,
                "resource_id": str(resource_id) if resource_id else None,
            },
        )

        return audit_event

    # ─── Read ────────────────────────────────────────────────────────────────

    async def get_by_id(self, audit_id: UUID) -> Optional[AuditEvent]:
        """Retrieve a single audit event by its primary key."""
        result = await self._session.execute(
            select(AuditEvent).where(AuditEvent.id == audit_id)
        )
        return result.scalar_one_or_none()

    async def get_by_resource(
        self,
        resource_id: UUID,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """
        Retrieve audit events for a specific resource, optionally filtered by
        event_type. Returns results ordered newest-first.
        """
        conditions = [AuditEvent.resource_id == resource_id]
        if event_type:
            conditions.append(AuditEvent.event_type == event_type)

        result = await self._session.execute(
            select(AuditEvent)
            .where(and_(*conditions))
            .order_by(AuditEvent.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_actor(
        self,
        actor_id: UUID,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """
        Retrieve audit events triggered by a specific actor (guardian, admin).
        Used for right-of-access exports (POPIA §23).
        """
        conditions = [AuditEvent.actor_id == actor_id]
        if event_type:
            conditions.append(AuditEvent.event_type == event_type)

        result = await self._session.execute(
            select(AuditEvent)
            .where(and_(*conditions))
            .order_by(AuditEvent.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_popia_events_for_learner(
        self,
        pseudonym_id: UUID,
        limit: int = 500,
    ) -> list[AuditEvent]:
        """
        Retrieve all POPIA-relevant audit events for a learner, identified
        by pseudonym_id (never learner real UUID — POPIA §14 data minimisation).

        Used for: right-of-access export, POPIA §23 data subject requests.
        """
        result = await self._session.execute(
            select(AuditEvent)
            .where(
                AuditEvent.payload["pseudonym_id"].astext == str(pseudonym_id)
            )
            .order_by(AuditEvent.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

    # ─── Internal helpers ────────────────────────────────────────────────────

    _PII_FIELD_NAMES = frozenset(
        {
            "email",
            "email_address",
            "full_name",
            "display_name",
            "date_of_birth",
            "dob",
            "phone",
            "phone_number",
            "id_number",
            "sa_id",
            "national_id",
            "address",
            "physical_address",
            "street_address",
        }
    )

    def _validate_payload_no_pii(
        self, event_type: str, payload: dict[str, Any]
    ) -> None:
        """
        Lightweight PII field name scan. Raises ValueError if the payload
        dict contains keys that are known PII field names.

        This is a defence-in-depth check — the primary PII scrubbing must
        happen upstream in the service layer.
        """
        payload_keys = {k.lower() for k in payload.keys()}
        pii_found = payload_keys & self._PII_FIELD_NAMES

        if pii_found:
            raise ValueError(
                f"AuditRepository.append() received payload with suspected PII fields "
                f"for event '{event_type}': {sorted(pii_found)}. "
                f"Remove PII before appending to the audit trail."
            )
