"""
app/repositories/consent_repository.py
PostgreSQL persistence for ConsentRecord.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Optional

import asyncpg

from app.domain.consent import ConsentRecord, ConsentState


class ConsentRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def get_active_for_learner(
        self, learner_id: uuid.UUID
    ) -> Optional[ConsentRecord]:
        row = await self._pool.fetchrow(
            """
            SELECT * FROM consent_records
            WHERE learner_id = $1
            ORDER BY created_at DESC
            LIMIT 1
            """,
            learner_id,
        )
        return self._row_to_model(row) if row else None

    async def get_by_id(self, record_id: uuid.UUID) -> Optional[ConsentRecord]:
        row = await self._pool.fetchrow(
            "SELECT * FROM consent_records WHERE id = $1", record_id
        )
        return self._row_to_model(row) if row else None

    async def create(self, record: ConsentRecord) -> ConsentRecord:
        await self._pool.execute(
            """
            INSERT INTO consent_records (
                id, learner_id, guardian_id, privacy_notice_version,
                state, granted_at, expires_at, withdrawn_at,
                denial_reason, created_at, updated_at
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
            """,
            record.id, record.learner_id, record.guardian_id,
            record.privacy_notice_version, record.state.value,
            record.granted_at, record.expires_at, record.withdrawn_at,
            record.denial_reason, record.created_at, record.updated_at,
        )
        return record

    async def update(self, record: ConsentRecord) -> ConsentRecord:
        await self._pool.execute(
            """
            UPDATE consent_records SET
                state = $2, granted_at = $3, expires_at = $4,
                withdrawn_at = $5, denial_reason = $6,
                privacy_notice_version = $7, updated_at = $8
            WHERE id = $1
            """,
            record.id, record.state.value, record.granted_at,
            record.expires_at, record.withdrawn_at, record.denial_reason,
            record.privacy_notice_version,
            datetime.now(timezone.utc),
        )
        return record

    async def list_expiring_soon(self, within_days: int = 30) -> list[ConsentRecord]:
        rows = await self._pool.fetch(
            """
            SELECT * FROM consent_records
            WHERE state = 'granted'
              AND expires_at <= NOW() + ($1 || ' days')::interval
              AND expires_at > NOW()
            """,
            str(within_days),
        )
        return [self._row_to_model(r) for r in rows]

    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_model(row: asyncpg.Record) -> ConsentRecord:
        return ConsentRecord(
            id=row["id"],
            learner_id=row["learner_id"],
            guardian_id=row["guardian_id"],
            privacy_notice_version=row["privacy_notice_version"],
            state=ConsentState(row["state"]),
            granted_at=row["granted_at"],
            expires_at=row["expires_at"],
            withdrawn_at=row["withdrawn_at"],
            denial_reason=row["denial_reason"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
