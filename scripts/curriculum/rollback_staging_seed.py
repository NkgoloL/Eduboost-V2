#!/usr/bin/env python3
"""Roll back staging database seeding items by run timestamp log or scope ID."""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import AsyncSessionLocal
from app.models.content_factory import ContentSeedRun
from app.services.content_staging_seed_executor import ContentStagingSeedExecutor
from sqlalchemy import select

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("rollback_staging_seed")


async def run_rollback(args: argparse.Namespace) -> int:
    executor = ContentStagingSeedExecutor()
    actor_id = args.actor_id
    reason = args.reason

    run_ids_to_rollback = []

    if args.run_id:
        # Load run log file
        log_path = ROOT / "logs" / f"seed_run_{args.run_id}.json"
        if not log_path.exists():
            logger.error(f"Seeding log file not found at {log_path}")
            return 1

        try:
            log_data = json.loads(log_path.read_text(encoding="utf-8"))
            scopes = log_data.get("scopes", {})
            for scope_id, run_id_str in scopes.items():
                run_ids_to_rollback.append((scope_id, UUID(run_id_str)))
        except Exception as e:
            logger.exception(f"Failed to parse seeding log file: {e}")
            return 1

    elif args.scope_id:
        async with AsyncSessionLocal() as session:
            stmt = select(ContentSeedRun).where(
                ContentSeedRun.scope_id == args.scope_id,
                ContentSeedRun.status != "rolled_back"
            )
            result = await session.execute(stmt)
            runs = result.scalars().all()
            for run in runs:
                run_ids_to_rollback.append((args.scope_id, run.seed_run_id))
    else:
        logger.error("Either --run-id <timestamp> or --scope-id <scope_id> must be specified.")
        return 1

    if not run_ids_to_rollback:
        logger.info("No active seed runs resolved to roll back.")
        return 0

    logger.info(f"Resolved {len(run_ids_to_rollback)} run(s) for rollback.")

    total_rolled_back = 0
    failed_rollbacks = []

    for scope_id, run_id in run_ids_to_rollback:
        logger.info(f"Rolling back run {run_id} for scope {scope_id}...")
        async with AsyncSessionLocal() as session:
            try:
                res = await executor.rollback_seed_run(
                    session,
                    run_id,
                    actor_id=actor_id,
                    reason=reason,
                )
                await session.commit()
                logger.info(f"Successfully rolled back run {run_id}: status={res.status}, rolled_back={res.rolled_back_count}")
                total_rolled_back += res.rolled_back_count
            except Exception:
                logger.exception(f"Failed to roll back run {run_id} for scope {scope_id}")
                failed_rollbacks.append(run_id)

    if failed_rollbacks:
        logger.error(f"Failed to roll back {len(failed_rollbacks)} run(s): {failed_rollbacks}")
        return 1

    logger.info(f"Rollback completed successfully. Total records affected: {total_rolled_back}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-id", help="Log timestamp YYYYMMDD_HHMMSS of the seeding run.")
    group.add_argument("--scope-id", help="Scope ID to roll back all active runs for.")
    parser.add_argument("--actor-id", default="dev-rollback-actor", help="Actor ID initiating the rollback.")
    parser.add_argument("--reason", default="Developer initiated rollback.", help="Reason for rollback.")
    return asyncio.run(run_rollback(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
