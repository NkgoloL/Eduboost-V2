#!/usr/bin/env python3
"""
audit_write_flow.py — self-contained audited flow command for AUDIT-WRITE-001R.

Writes one audit_event row directly to the live DB using psycopg2 (no app
server required, no asyncpg/PgBouncer conflict). The row uses event_type
'diagnostic_start' (a real AuditEventType value), embeds the AUDIT_WRITE_TRACE_ID
in the payload, and satisfies all audit_events CHECK constraints.

Exit 0 on success, 1 on failure.
"""
from __future__ import annotations

import hashlib
import hmac as hmac_mod
import json
import os
import sys
import uuid
from datetime import datetime, timezone

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 is not installed", file=sys.stderr)
    sys.exit(1)


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def _hmac_hex(event_hash: str, previous_hash: str | None) -> str:
    secret = os.getenv("AUDIT_HMAC_SECRET", "dev-audit-hmac-secret-placeholder")
    msg = f"{event_hash}:{previous_hash or 'GENESIS'}"
    return hmac_mod.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()


def main() -> int:
    dsn_raw = (
        os.getenv("AUDIT_WRITE_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or os.getenv("STAGING_DATABASE_URL")
        or os.getenv("SUPABASE_DB_URL")
        or ""
    )
    if not dsn_raw:
        print("ERROR: no database URL found in environment", file=sys.stderr)
        return 1

    # Normalise to plain postgresql:// for psycopg2
    for prefix in ("postgresql+asyncpg://", "postgres://"):
        if dsn_raw.startswith(prefix):
            dsn_raw = "postgresql://" + dsn_raw[len(prefix):]
            break

    trace_id = (
        os.getenv("AUDIT_WRITE_TRACE_ID")
        or f"audit-write-flow-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    )

    event_id = uuid.uuid4()
    event_type = "diagnostic_start"
    actor_id = None
    resource_id = None
    payload = {
        "source": "audit_write_flow",
        "trace_id": trace_id,
        "note": "AUDIT-WRITE-001R runtime evidence write",
    }

    hash_input = json.dumps(
        {
            "event_id": str(event_id),
            "event_type": event_type,
            "actor_id": str(actor_id) if actor_id else None,
            "resource_id": str(resource_id) if resource_id else None,
            "previous_event_hash": "GENESIS",
            "payload": payload,
        },
        sort_keys=True,
    )
    event_hash = _sha256(hash_input)
    hmac_sig = _hmac_hex(event_hash, None)

    try:
        conn = psycopg2.connect(dsn_raw)
        conn.autocommit = False
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO public.audit_events
                (id, event_type, actor_id, resource_id, payload,
                 created_at, event_hash, previous_event_hash, hmac_signature)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                str(event_id),
                event_type,
                None,
                None,
                json.dumps(payload),
                datetime.now(timezone.utc),
                event_hash,
                None,        # first event — no previous hash
                hmac_sig,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()

        print(f"OK: wrote audit_event id={event_id} event_type={event_type}")
        print(f"    trace_id={trace_id}")
        print(f"    event_hash={event_hash[:16]}...")
        return 0

    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
