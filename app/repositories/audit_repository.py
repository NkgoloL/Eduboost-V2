"""
app/repositories/audit_repository.py
Append-only PostgreSQL audit repository.
Implements §4.5: event hash, previous-hash chain, HMAC signature.
The DB role used at runtime must NOT have UPDATE/DELETE on this table.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import asyncpg

from app.domain.consent import AuditEventType


_HMAC_SECRET: bytes = b""   # injected at startup from settings.AUDIT_HMAC_SECRET


def configure_hmac_secret(secret: bytes) -> None:
    global _HMAC_SECRET
    _HMAC_SECRET = secret


def _compute_hash(payload: dict[str, Any]) -> str:
    """SHA-256 of the canonical JSON payload."""
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _compute_hmac(event_hash: str, previous_hash: str) -> str:
    """HMAC-SHA256 over '{event_hash}:{previous_hash}'."""
    message = f"{event_hash}:{previous_hash}".encode()
    return hmac.new(_HMAC_SECRET, message, hashlib.sha256).hexdigest()


class AuditRepository:
    """
    §4.5 – append-only audit log.
    Every INSERT chains hashes to form a tamper-evident log.
    The underlying table must have:
      - NO DELETE privilege for the app role
      - NO UPDATE privilege for the app role
      - A row-level trigger that raises on UPDATE/DELETE as a belt-and-suspenders guard
    """

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    # ------------------------------------------------------------------
    # Public write API (INSERT only)
    # ------------------------------------------------------------------

    async def record(
        self,
        event_type: AuditEventType,
        actor_id: Optional[uuid.UUID],
        learner_id: Optional[uuid.UUID],
        payload: dict[str, Any],
        *,
        conn: Optional[asyncpg.Connection] = None,
    ) -> uuid.UUID:
        """
        Append one audit event.  Returns the new event's UUID.
        Automatically chains the hash to the previous event for the learner
        (or global tail if learner_id is None).
        """
        event_id = uuid.uuid4()
        occurred_at = datetime.now(timezone.utc)

        # Build the hashable payload
        hash_payload = {
            "event_id": str(event_id),
            "event_type": event_type.value,
            "actor_id": str(actor_id) if actor_id else None,
            "learner_id": str(learner_id) if learner_id else None,
            "occurred_at": occurred_at.isoformat(),
            "payload": payload,
        }
        event_hash = _compute_hash(hash_payload)

        # Fetch previous hash (chain tail) – GENESIS sentinel for first record
        previous_hash = await self._latest_hash(learner_id, conn=conn)

        signature = _compute_hmac(event_hash, previous_hash)

        sql = """
            INSERT INTO audit_events (
                id, event_type, actor_id, learner_id,
                payload, occurred_at,
                event_hash, previous_hash, hmac_signature
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        execute = (conn or self._pool).execute
        await execute(
            sql,
            event_id,
            event_type.value,
            actor_id,
            learner_id,
            json.dumps(payload, default=str),
            occurred_at,
            event_hash,
            previous_hash,
            signature,
        )
        return event_id

    # ------------------------------------------------------------------
    # Chain verification (§4.5 – audit-chain verification script)
    # ------------------------------------------------------------------

    async def verify_chain(
        self,
        learner_id: Optional[uuid.UUID] = None,
        limit: int = 10_000,
    ) -> tuple[bool, list[str]]:
        """
        Walk the audit chain for a learner (or globally) and verify:
          1. event_hash matches re-computed hash of payload columns
          2. hmac_signature matches re-computed HMAC
          3. previous_hash equals prior row's event_hash
        Returns (ok, list_of_errors).
        """
        sql = """
            SELECT id, event_type, actor_id, learner_id, payload,
                   occurred_at, event_hash, previous_hash, hmac_signature
            FROM audit_events
            WHERE ($1::uuid IS NULL OR learner_id = $1)
            ORDER BY occurred_at ASC, id ASC
            LIMIT $2
        """
        rows = await self._pool.fetch(sql, learner_id, limit)
        errors: list[str] = []
        prev_hash = "GENESIS"

        for row in rows:
            eid = str(row["id"])
            hash_payload = {
                "event_id": eid,
                "event_type": row["event_type"],
                "actor_id": str(row["actor_id"]) if row["actor_id"] else None,
                "learner_id": str(row["learner_id"]) if row["learner_id"] else None,
                "occurred_at": row["occurred_at"].isoformat(),
                "payload": json.loads(row["payload"]),
            }
            expected_hash = _compute_hash(hash_payload)
            expected_hmac = _compute_hmac(expected_hash, row["previous_hash"])

            if row["event_hash"] != expected_hash:
                errors.append(f"[{eid}] event_hash mismatch")
            if row["hmac_signature"] != expected_hmac:
                errors.append(f"[{eid}] HMAC mismatch")
            if row["previous_hash"] != prev_hash:
                errors.append(
                    f"[{eid}] chain broken: expected previous_hash={prev_hash!r}, "
                    f"got {row['previous_hash']!r}"
                )
            prev_hash = row["event_hash"]

        return (len(errors) == 0, errors)

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    async def _latest_hash(
        self,
        learner_id: Optional[uuid.UUID],
        *,
        conn: Optional[asyncpg.Connection] = None,
    ) -> str:
        sql = """
            SELECT event_hash FROM audit_events
            WHERE ($1::uuid IS NULL OR learner_id = $1)
            ORDER BY occurred_at DESC, id DESC
            LIMIT 1
        """
        fetch_one = (conn or self._pool).fetchrow
        row = await fetch_one(sql, learner_id)
        return row["event_hash"] if row else "GENESIS"
