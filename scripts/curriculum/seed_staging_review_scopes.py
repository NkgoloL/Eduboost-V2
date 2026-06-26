#!/usr/bin/env python3
"""Execute staging database seeding for dev_approved review scopes."""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import AsyncSessionLocal
from app.domain.content_scope import ContentScopeStatus
from app.services.content_scope_registry import ContentScopeRegistry
from app.services.content_staging_seed_executor import ContentStagingSeedExecutor, MissingForeignKeyError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("seed_staging_review_scopes")


async def run_seeding(args: argparse.Namespace) -> int:
    registry = ContentScopeRegistry()

    # Resolve scope IDs
    if args.scope_id:
        scope_ids = args.scope_id
    elif getattr(args, "include_all_review_scopes", False):
        scope_ids = [
            scope.scope_id
            for scope in registry.list_scopes()
            if scope.status == ContentScopeStatus.REVIEW
        ]
    else:
        # Default seeding remains active-scope only. Review scopes from the
        # expanded registry are staging candidates, not default operational
        # seed targets; pass --include-all-review-scopes for the explicit
        # review-scope backfill workflow.
        scope_ids = [scope.scope_id for scope in registry.list_active_scopes()]

    if not scope_ids:
        logger.warning("No review scopes resolved to seed.")
        return 0

    batch_size = args.batch_size or int(os.environ.get("SEED_BATCH_SIZE", 500))
    dry_run = args.dry_run
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    summary_path = ROOT / "logs" / f"seed_run_{timestamp}.json"

    logger.info(f"Resolved {len(scope_ids)} scopes to process. dry_run={dry_run}, batch_size={batch_size}")

    if dry_run:
        # Dry run logic: resolve scopes and count planned items
        scopes_summary = []
        total_records = 0
        async with AsyncSessionLocal() as session:
            executor = ContentStagingSeedExecutor()
            for scope_id in scope_ids:
                plan = await executor.dry_run_seed(session, scope_id)
                record_count = len(plan.seedable)
                total_records += record_count
                scopes_summary.append({
                    "scope_id": scope_id,
                    "record_count": record_count,
                    "skipped_count": len(plan.skipped),
                })

        summary = {
            "schema_version": "1.0",
            "timestamp": timestamp,
            "dry_run": True,
            "summary": {
                "total_scopes": len(scope_ids),
                "total_records": total_records,
            },
            "scopes": scopes_summary,
        }

        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0

    # Real database run
    total_attempted = len(scope_ids)
    succeeded_scopes = []
    failed_scopes = []
    total_upserted = 0
    total_skipped = 0
    total_failed_records = 0
    scope_errors = {}
    scopes_run_ids = {}

    executor = ContentStagingSeedExecutor()

    for scope_id in scope_ids:
        logger.info(f"Starting seeding for scope: {scope_id}")
        async with AsyncSessionLocal() as session:
            try:
                res = await executor.seed_staging(
                    session,
                    scope_id,
                    actor_id=args.reviewer_id,
                    allow_partial=True,
                    batch_size=batch_size,
                )
                if res.status == "failed" or res.errors:
                    logger.error(f"Seeding completed with errors for scope {scope_id}: {res.errors}")
                    failed_scopes.append(scope_id)
                    scope_errors[scope_id] = res.errors
                    total_failed_records += res.skipped_count
                else:
                    logger.info(f"Successfully seeded scope {scope_id}: seeded={res.seeded_count}, skipped={res.skipped_count}")
                    succeeded_scopes.append(scope_id)
                    total_upserted += res.seeded_count
                    total_skipped += res.skipped_count
                    seed_run_id = getattr(res, "seed_run_id", None) or getattr(res, "id", None)
                    scopes_run_ids[scope_id] = str(seed_run_id) if seed_run_id is not None else "unreported"
            except MissingForeignKeyError as fkey_err:
                logger.error(f"Seeding aborted for scope {scope_id} due to missing foreign key: {fkey_err}")
                failed_scopes.append(scope_id)
                scope_errors[scope_id] = [str(fkey_err)]
            except Exception as exc:
                logger.exception(f"Unhandled exception during seeding for scope {scope_id}")
                failed_scopes.append(scope_id)
                scope_errors[scope_id] = [str(exc)]

    summary = {
        "schema_version": "1.0",
        "timestamp": timestamp,
        "dry_run": False,
        "summary": {
            "total_scopes_attempted": total_attempted,
            "total_scopes_succeeded": len(succeeded_scopes),
            "total_scopes_failed": len(failed_scopes),
            "total_records_upserted": total_upserted,
            "total_skipped": total_skipped,
            "total_records_failed": total_failed_records,
            "failed_scope_ids": failed_scopes,
        },
        "scopes": scopes_run_ids,
        "errors": scope_errors,
    }

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(str(summary_path.relative_to(ROOT)))

    return 1 if failed_scopes else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope-id", action="append", default=None, help="Process one or more specific scopes. Repeatable.")
    parser.add_argument("--include-all-review-scopes", action="store_true", help="Process every review/staging scope from the expanded registry. Default is active scopes only.")
    parser.add_argument("--dry-run", action="store_true", help="Print dry run summary of scopes and counts without writing to database.")
    parser.add_argument("--batch-size", type=int, default=None, help="Commit batch size.")
    parser.add_argument("--reviewer-id", default="dev-content-review-2026-06-03", help="Actor ID to assign for the run.")
    return asyncio.run(run_seeding(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
