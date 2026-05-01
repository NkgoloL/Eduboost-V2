"""Append-only audit repository for EduBoost V2."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import insert, select

from app.api.core.database import AsyncSessionFactory
from app.api.models.db_models import AuditLogEntryRecord
from app.domain.entities import AuditLog


class AuditRepository:
    async def append(self, event_type: str, payload: dict, learner_id: str | None = None) -> AuditLog:
        event_id = str(uuid.uuid4())
        occurred_at = datetime.now(timezone.utc)
        async with AsyncSessionFactory() as session:
            await session.execute(
                insert(AuditLogEntryRecord).values(
                    event_id=event_id,
                    learner_id=learner_id,
                    event_type=event_type,
                    payload=payload,
                    occurred_at=occurred_at,
                )
            )
            await session.commit()
        return AuditLog(
            event_id=event_id,
            learner_id=learner_id,
            event_type=event_type,
            occurred_at=occurred_at,
            payload=payload,
        )

    async def latest(self, limit: int = 20) -> list[AuditLog]:
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(AuditLogEntryRecord).order_by(AuditLogEntryRecord.occurred_at.desc()).limit(limit)
            )
            rows = result.scalars().all()
        return [
            AuditLog(
                event_id=row.event_id,
                learner_id=row.learner_id,
                event_type=row.event_type,
                occurred_at=row.occurred_at,
                payload=row.payload or {},
            )
            for row in rows
        ]
