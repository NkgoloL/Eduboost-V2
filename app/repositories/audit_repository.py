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
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.consent import AuditEventType
from app.models import AuditEvent


_HMAC_SECRET: bytes = b""   # injected at startup from settings.AUDIT_HMAC_SECRET


def configure_hmac_secret(secret: bytes) -> None:
    global _HMAC_SECRET
    _HMAC_SECRET = secret


def compute_audit_hash(
    *,
    event_id: object,
    event_type: str,
    actor_id: object | None,
    resource_id: object | None,
    previous_event_hash: str | None,
    payload: dict[str, Any],
) -> str:
    """Return deterministic SHA-256 hash for audit-chain tests."""
    canonical = json.dumps(
        {
            "event_id": str(event_id),
            "event_type": event_type,
            "actor_id": str(actor_id) if actor_id is not None else None,
            "resource_id": str(resource_id) if resource_id is not None else None,
            "previous_event_hash": previous_event_hash,
            "payload": payload,
        },
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def sign_audit_hash(event_hash: str, secret: str | bytes) -> str:
    """Return HMAC-SHA256 signature for an audit hash."""
    key = secret.encode("utf-8") if isinstance(secret, str) else secret
    return hmac.new(key, event_hash.encode("utf-8"), hashlib.sha256).hexdigest()


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

    def __init__(self, db: AsyncSession | asyncpg.Pool) -> None:
        self._db = db

    @property
    def _is_async_session(self) -> bool:
        return isinstance(self._db, AsyncSession)

    # ------------------------------------------------------------------
    # Public write API (INSERT only)
    # ------------------------------------------------------------------

    async def record(
        self,
        event_type: AuditEventType | str,
        actor_id: Optional[uuid.UUID | str] = None,
        resource_id: Optional[uuid.UUID | str] = None,
        payload: dict[str, Any] | None = None,
        *,
        conn: Optional[asyncpg.Connection] = None,
    ) -> uuid.UUID:
        """
        Append one audit event. Returns the new event's UUID.
        Automatically chains the hash to the previous event for the same resource
        (or global tail if resource_id is None).
        """
        payload = payload or {}
        event_id = uuid.uuid4()

        event_type_value = event_type.value if isinstance(event_type, AuditEventType) else str(event_type)
        if not event_type_value.strip():
            raise ValueError("event_type must not be blank")
        self._validate_payload(payload)

        previous_event_hash = await self._latest_hash(resource_id, conn=conn)
        hash_payload = {
            "event_id": str(event_id),
            "event_type": event_type_value,
            "actor_id": str(actor_id) if actor_id else None,
            "resource_id": str(resource_id) if resource_id else None,
            "previous_event_hash": previous_event_hash,
            "payload": payload,
        }
        event_hash = _compute_hash(hash_payload)
        signature = _compute_hmac(event_hash, previous_event_hash)
        persisted_previous_event_hash = None if previous_event_hash == "GENESIS" else previous_event_hash

        if self._is_async_session:
            event = AuditEvent(
                id=event_id,
                event_type=event_type_value,
                actor_id=actor_id,
                resource_id=resource_id,
                payload=payload,
                event_hash=event_hash,
                previous_event_hash=persisted_previous_event_hash,
                hmac_signature=signature,
            )
            self._db.add(event)
            await self._db.flush()
            return event.id

        sql = """
            INSERT INTO audit_events (
                id, event_type, actor_id, resource_id,
                payload, created_at,
                event_hash, previous_event_hash, hmac_signature
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        execute = (conn or self._db).execute
        await execute(
            sql,
            event_id,
            event_type_value,
            actor_id,
            resource_id,
            json.dumps(payload, default=str),
            datetime.now(timezone.utc),
            event_hash,
            persisted_previous_event_hash,
            signature,
        )
        return event_id

    async def append(
        self,
        event_type: AuditEventType | str,
        actor_id: Optional[uuid.UUID | str] = None,
        resource_id: Optional[uuid.UUID | str] = None,
        payload: dict[str, Any] | None = None,
        *,
        conn: Optional[asyncpg.Connection] = None,
    ) -> AuditEvent | asyncpg.Record:
        """
        Append one audit event and return the inserted row.
        """
        payload = payload or {}
        event_id = uuid.uuid4()

        event_type_value = event_type.value if isinstance(event_type, AuditEventType) else str(event_type).strip()
        if not event_type_value:
            raise ValueError("event_type must not be blank")
        self._validate_payload(payload)

        previous_event_hash = await self._latest_hash(resource_id, conn=conn)
        hash_payload = {
            "event_id": str(event_id),
            "event_type": event_type_value,
            "actor_id": str(actor_id) if actor_id else None,
            "resource_id": str(resource_id) if resource_id else None,
            "previous_event_hash": previous_event_hash,
            "payload": payload,
        }
        event_hash = _compute_hash(hash_payload)
        signature = _compute_hmac(event_hash, previous_event_hash)
        persisted_previous_event_hash = None if previous_event_hash == "GENESIS" else previous_event_hash

        if self._is_async_session:
            event = AuditEvent(
                id=event_id,
                event_type=event_type_value,
                actor_id=actor_id,
                resource_id=resource_id,
                payload=payload,
                event_hash=event_hash,
                previous_event_hash=persisted_previous_event_hash,
                hmac_signature=signature,
            )
            self._db.add(event)
            await self._db.flush()
            return event

        sql = """
            INSERT INTO audit_events (
                id, event_type, actor_id, resource_id,
                payload, created_at,
                event_hash, previous_event_hash, hmac_signature
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, event_type, actor_id, resource_id,
                      payload, created_at, event_hash,
                      previous_event_hash, hmac_signature
        """
        fetchrow = (conn or self._db).fetchrow
        row = await fetchrow(
            sql,
            event_id,
            event_type_value,
            actor_id,
            resource_id,
            json.dumps(payload, default=str),
            datetime.now(timezone.utc),
            event_hash,
            persisted_previous_event_hash,
            signature,
        )
        assert row is not None
        return row

    async def get_by_resource(
        self,
        resource_id: uuid.UUID | str,
        event_type: str | None = None,
    ) -> list[AuditEvent] | list[asyncpg.Record]:
        if self._is_async_session:
            stmt = select(AuditEvent).where(AuditEvent.resource_id == resource_id)
            if event_type is not None:
                stmt = stmt.where(AuditEvent.event_type == event_type)
            result = await self._db.execute(stmt)
            return list(result.scalars().all())

        sql = """
            SELECT * FROM audit_events
            WHERE resource_id = $1
        """
        args: list[object] = [resource_id]
        if event_type is not None:
            sql += "\n            AND event_type = $2"
            args.append(event_type)
        return await self._db.fetch(sql, *args)

    async def get_by_actor(
        self,
        actor_id: uuid.UUID | str,
        event_type: str | None = None,
    ) -> list[AuditEvent] | list[asyncpg.Record]:
        if self._is_async_session:
            stmt = select(AuditEvent).where(AuditEvent.actor_id == actor_id)
            if event_type is not None:
                stmt = stmt.where(AuditEvent.event_type == event_type)
            result = await self._db.execute(stmt)
            return list(result.scalars().all())

        sql = """
            SELECT * FROM audit_events
            WHERE actor_id = $1
        """
        args: list[object] = [actor_id]
        if event_type is not None:
            sql += "\n            AND event_type = $2"
            args.append(event_type)
        return await self._db.fetch(sql, *args)

    # ------------------------------------------------------------------
    # Chain verification (§4.5 – audit-chain verification script)
    # ------------------------------------------------------------------

    async def verify_chain(
        self,
        resource_id: Optional[uuid.UUID] = None,
        limit: int = 10_000,
    ) -> tuple[bool, list[str]]:
        """
        Walk the audit chain for a resource (or globally) and verify:
          1. event_hash matches re-computed hash of payload columns
          2. hmac_signature matches re-computed HMAC
          3. previous_event_hash equals prior row's event_hash
        Returns (ok, list_of_errors).
        """
        errors: list[str] = []
        prev_hash = "GENESIS"

        if self._is_async_session:
            stmt = select(AuditEvent).where(
                AuditEvent.resource_id == resource_id if resource_id is not None else AuditEvent.resource_id.is_(None)
            ).order_by(AuditEvent.created_at.asc(), AuditEvent.id.asc()).limit(limit)
            result = await self._db.execute(stmt)
            rows = result.scalars().all()
        else:
            sql = """
                SELECT id, event_type, actor_id, resource_id, payload,
                       created_at, event_hash, previous_event_hash, hmac_signature
                FROM audit_events
                WHERE ($1::uuid IS NULL OR resource_id = $1)
                ORDER BY created_at ASC, id ASC
                LIMIT $2
            """
            rows = await self._db.fetch(sql, resource_id, limit)

        for row in rows:
            if self._is_async_session:
                eid = str(row.id)
                payload_value = row.payload
                event_type_value = row.event_type
                actor_id_value = str(row.actor_id) if row.actor_id else None
                resource_id_value = str(row.resource_id) if row.resource_id else None
                previous_event_hash_value = row.previous_event_hash
                event_hash_value = row.event_hash
                hmac_signature_value = row.hmac_signature
            else:
                eid = str(row["id"])
                payload_value = row["payload"] if isinstance(row["payload"], dict) else json.loads(row["payload"])
                event_type_value = row["event_type"]
                actor_id_value = str(row["actor_id"]) if row["actor_id"] else None
                resource_id_value = str(row["resource_id"]) if row["resource_id"] else None
                previous_event_hash_value = row["previous_event_hash"]
                event_hash_value = row["event_hash"]
                hmac_signature_value = row["hmac_signature"]

            hash_payload = {
                "event_id": eid,
                "event_type": event_type_value,
                "actor_id": actor_id_value,
                "resource_id": resource_id_value,
                "previous_event_hash": previous_event_hash_value,
                "payload": payload_value,
            }
            expected_hash = _compute_hash(hash_payload)
            expected_hmac = _compute_hmac(expected_hash, previous_event_hash_value)

            if event_hash_value != expected_hash:
                errors.append(f"[{eid}] event_hash mismatch")
            if hmac_signature_value != expected_hmac:
                errors.append(f"[{eid}] HMAC mismatch")
            if previous_event_hash_value != prev_hash:
                errors.append(
                    f"[{eid}] chain broken: expected previous_event_hash={prev_hash!r}, "
                    f"got {previous_event_hash_value!r}"
                )
            prev_hash = event_hash_value

        return (len(errors) == 0, errors)

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    async def _latest_hash(
        self,
        resource_id: Optional[uuid.UUID | str],
        *,
        conn: Optional[asyncpg.Connection] = None,
    ) -> str:
        if self._is_async_session:
            if resource_id is None:
                stmt = select(AuditEvent.event_hash).where(AuditEvent.resource_id.is_(None))
            else:
                stmt = select(AuditEvent.event_hash).where(AuditEvent.resource_id == resource_id)
            stmt = stmt.order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc()).limit(1)
            result = await self._db.execute(stmt)
            row = result.scalar_one_or_none()
            return row if row is not None else "GENESIS"

        sql = """
            SELECT event_hash FROM audit_events
            WHERE ($1::uuid IS NULL OR resource_id = $1)
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """
        fetch_one = (conn or self._db).fetchrow
        row = await fetch_one(sql, resource_id)
        return row["event_hash"] if row else "GENESIS"

    def _validate_payload(self, payload: dict[str, Any]) -> None:
        if payload is None:
            return
        pii_field_names = {
            "email",
            "email_address",
            "date_of_birth",
            "display_name",
            "full_name",
            "first_name",
            "last_name",
            "phone",
            "phone_number",
            "ssn",
            "identity_number",
            "national_id",
            "passport_number",
            "address",
            "street_address",
            "city",
            "zip",
            "postal_code",
        }

        def check(obj: Any, path: str = "") -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.lower() in pii_field_names:
                        raise ValueError(f"PII field names are not permitted in audit payload: {path + key}")
                    check(value, f"{path}{key}.")
            elif isinstance(obj, list):
                for index, item in enumerate(obj):
                    check(item, f"{path}[{index}].")

        check(payload)
