"""Append-only audit repository for EduBoost V2."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditEvent


def _as_uuid(value: str | uuid.UUID | None) -> uuid.UUID | None:
    if value is None:
        return None
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(str(value))


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def append(
        self,
        event_type: str,
        payload: dict[str, Any],
        actor_id: str | uuid.UUID | None = None,
        resource_id: str | uuid.UUID | None = None,
    ) -> AuditEvent:
        if not event_type or not event_type.strip():
            raise ValueError("event_type must be a non-empty string")
        self._validate_payload_no_pii(payload)

        audit_event = AuditEvent(
            id=uuid.uuid4(),
            event_type=event_type.strip(),
            actor_id=_as_uuid(actor_id),
            resource_id=_as_uuid(resource_id),
            payload=payload,
        )
        self._session.add(audit_event)
        await self._session.flush()
        await self._session.refresh(audit_event)
        return audit_event

    async def log(
        self,
        event_type: str,
        actor_id: str | uuid.UUID | None = None,
        learner_pseudonym: str | None = None,
        payload: dict[str, Any] | None = None,
        constitutional_outcome: str | None = None,
    ) -> AuditEvent:
        data = dict(payload or {})
        if learner_pseudonym is not None:
            data.setdefault("learner_pseudonym", learner_pseudonym)
        if constitutional_outcome is not None:
            data.setdefault("constitutional_outcome", constitutional_outcome)
        return await self.append(
            event_type=event_type,
            actor_id=actor_id,
            payload=data,
        )

    async def latest(self, limit: int = 20) -> list[AuditEvent]:
        result = await self._session.execute(
            select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, audit_id: str | uuid.UUID) -> AuditEvent | None:
        result = await self._session.execute(
            select(AuditEvent).where(AuditEvent.id == _as_uuid(audit_id))
        )
        return result.scalar_one_or_none()

    async def get_by_resource(
        self,
        resource_id: str | uuid.UUID,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        stmt = select(AuditEvent).where(AuditEvent.resource_id == _as_uuid(resource_id))
        if event_type:
            stmt = stmt.where(AuditEvent.event_type == event_type)
        stmt = stmt.order_by(AuditEvent.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_actor(
        self,
        actor_id: str | uuid.UUID,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        stmt = select(AuditEvent).where(AuditEvent.actor_id == _as_uuid(actor_id))
        if event_type:
            stmt = stmt.where(AuditEvent.event_type == event_type)
        stmt = stmt.order_by(AuditEvent.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

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

    def _validate_payload_no_pii(self, payload: dict[str, Any]) -> None:
        payload_keys = {str(key).lower() for key in payload.keys()}
        pii_found = payload_keys & self._PII_FIELD_NAMES
        if pii_found:
            raise ValueError(f"PII-like fields not allowed in audit payload: {sorted(pii_found)}")
