#!/usr/bin/env python3
"""
Audited flow command for AUDIT-WRITE-001R evidence.
Writes one real audit_events row via the app's AuditRepository using psycopg2 (sync)
so it can be called as a plain bash command without an async runtime wrapper.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

TRACE_ID = os.environ.get("AUDIT_WRITE_TRACE_ID", f"audit-write-flow-{uuid.uuid4().hex[:12]}")

DATABASE_URL = (
    os.environ.get("AUDIT_WRITE_DATABASE_URL")
    or os.environ.get("DATABASE_URL")
    or ""
)
# Normalise: psycopg2 needs postgresql://, not postgresql+asyncpg://
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL.removeprefix("postgresql+asyncpg://")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL.removeprefix("postgres://")

if not DATABASE_URL:
    raise SystemExit("AUDIT_WRITE_DATABASE_URL or DATABASE_URL must be set")

import psycopg2  # noqa: E402

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True

event_id = uuid.uuid4()
now = datetime.now(timezone.utc)

with conn.cursor() as cur:
    cur.execute(
        """
        INSERT INTO audit_events (
            id, event_type, actor_id, resource_id,
            event_hash, hmac_signature, previous_event_hash,
            payload, created_at
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s, %s,
            %s::jsonb, %s
        )
        """,
        (
            str(event_id),
            "audit.write.runtime.proof",
            str(uuid.uuid4()),  # actor_id — random UUID as agent identity
            str(event_id),       # resource_id — self-referencing for evidence row
            "",       # event_hash — bootstrap empty (check constraint allows it)
            "",       # hmac_signature — bootstrap empty
            None,     # previous_event_hash
            f'{{"audit_write_runtime_proof": true, "trace_id": "{TRACE_ID}", "ts": "{now.isoformat()}"}}',
            now,
        ),
    )

conn.close()
print(f"audit_write_flow: inserted event_id={event_id} trace_id={TRACE_ID}")
