#!/usr/bin/env python3
"""
scripts/verify_audit_chain.py
§4.5 – Audit-chain verification script.
Walks the audit_events table and checks hash/HMAC integrity.

Usage:
    python scripts/verify_audit_chain.py
    python scripts/verify_audit_chain.py --learner-id <uuid>
    python scripts/verify_audit_chain.py --limit 50000
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
import uuid

import asyncpg

# Patch HMAC secret before importing repository
SECRET = os.environ.get("AUDIT_HMAC_SECRET", "").encode()
if not SECRET:
    print("ERROR: AUDIT_HMAC_SECRET environment variable is not set.", file=sys.stderr)
    sys.exit(2)

from app.repositories.audit_repository import AuditRepository, configure_hmac_secret

configure_hmac_secret(SECRET)


async def main(learner_id: uuid.UUID | None, limit: int) -> int:
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("ERROR: DATABASE_URL environment variable is not set.", file=sys.stderr)
        return 2

    pool = await asyncpg.create_pool(dsn)
    repo = AuditRepository(pool)

    print(f"Verifying audit chain (learner={learner_id}, limit={limit}) …")
    ok, errors = await repo.verify_chain(learner_id=learner_id, limit=limit)
    await pool.close()

    if ok:
        print("✅  Audit chain intact — no integrity violations found.")
        return 0
    else:
        print(f"❌  {len(errors)} integrity violation(s) detected:")
        for e in errors:
            print(f"   {e}")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify POPIA audit chain integrity.")
    parser.add_argument("--learner-id", type=uuid.UUID, default=None)
    parser.add_argument("--limit", type=int, default=10_000)
    args = parser.parse_args()
    sys.exit(asyncio.run(main(args.learner_id, args.limit)))
