"""V2 append-only audit service."""

from __future__ import annotations

from app.domain.schemas import AuditLogEntry
from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, repository: AuditRepository | None = None) -> None:
        self.repository = repository or AuditRepository()

    async def log_event(self, event_type: str, payload: dict, learner_id: str | None = None) -> AuditLogEntry:
        event = await self.repository.append(event_type=event_type, payload=payload, learner_id=learner_id)
        return AuditLogEntry(
            event_id=event.event_id,
            learner_id=event.learner_id,
            event_type=event.event_type,
            occurred_at=event.occurred_at,
            payload=event.payload,
        )

    async def get_recent_events(self, limit: int = 20) -> list[AuditLogEntry]:
        events = await self.repository.latest(limit=limit)
        return [
            AuditLogEntry(
                event_id=event.event_id,
                learner_id=event.learner_id,
                event_type=event.event_type,
                occurred_at=event.occurred_at,
                payload=event.payload,
            )
            for event in events
        ]
