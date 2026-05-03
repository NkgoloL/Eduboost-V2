from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.schemas import AuditLogEntry


class AuditService:
    def __init__(self, repository: Any | None = None) -> None:
        self.repository = repository

    async def log_event(
        self,
        event_type: str,
        payload: dict | None = None,
        learner_id: str | None = None,
        actor_id: str | None = None,
    ) -> AuditLogEntry:
        if self.repository is not None and hasattr(self.repository, "append"):
            row = await self.repository.append(event_type=event_type, payload=payload or {}, learner_id=learner_id, actor_id=actor_id)
            return _entry_from_row(row)
        if self.repository is not None and hasattr(self.repository, "log"):
            row = await self.repository.log(event_type=event_type, payload=payload or {}, actor_id=actor_id, learner_pseudonym=learner_id)
            return _entry_from_row(row)
        return AuditLogEntry(
            event_id=f"local-{int(datetime.now(UTC).timestamp() * 1000)}",
            learner_id=learner_id,
            event_type=event_type,
            occurred_at=datetime.now(UTC),
            payload=payload or {},
        )

    async def get_recent_events(self, limit: int = 50) -> list[AuditLogEntry]:
        if self.repository is not None and hasattr(self.repository, "latest"):
            rows = await self.repository.latest(limit=limit)
            return [_entry_from_row(row) for row in rows]
        return []


def _entry_from_row(row: Any) -> AuditLogEntry:
    return AuditLogEntry(
        event_id=str(getattr(row, "event_id", getattr(row, "id", ""))),
        learner_id=getattr(row, "learner_id", getattr(row, "learner_pseudonym", None)),
        event_type=getattr(row, "event_type", ""),
        occurred_at=getattr(row, "occurred_at", getattr(row, "created_at", datetime.now(UTC))),
        payload=getattr(row, "payload", {}) or {},
    )
