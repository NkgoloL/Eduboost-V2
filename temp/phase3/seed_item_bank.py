#!/usr/bin/env python3
"""
scripts/seed_item_bank.py
─────────────────────────────────────────────────────────────────────────────
Phase 3: Item Bank Seeder (P1-09, P3-12, P3-13)

Validates the seed JSON, upserts all approved items into the PostgreSQL
diagnostic_items table via SQLAlchemy, and prints a coverage summary.

Usage:
    python scripts/seed_item_bank.py
    python scripts/seed_item_bank.py --input data/caps/grade4_maths_item_bank.json
    python scripts/seed_item_bank.py --dry-run
    python scripts/seed_item_bank.py --status approved  # only seed approved items

Exit codes:
    0 — All items seeded successfully
    1 — Validation failures found — no items seeded
    2 — DB error or file not found
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional
from uuid import UUID

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("seed_item_bank")

from app.modules.diagnostics.item_validator import ItemValidator, ValidationError

TOPIC_MAP_PATH = REPO_ROOT / "data" / "caps" / "caps_topic_map_grade4_maths.json"
DEFAULT_INPUT  = REPO_ROOT / "data" / "caps" / "grade4_maths_item_bank.json"

LAUNCH_REFS   = ["4.M.1.1", "4.M.1.2", "4.M.1.3"]
LAUNCH_TARGET = 40


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_topic_map() -> dict:
    if not TOPIC_MAP_PATH.exists():
        logger.warning("Topic map not found — CAPS ref validation will be skipped.")
        return {}
    with open(TOPIC_MAP_PATH) as f:
        return json.load(f)


def load_seed(input_path: Path) -> list[dict]:
    if not input_path.exists():
        logger.error("Seed file not found: %s", input_path)
        sys.exit(2)
    with open(input_path) as f:
        data = json.load(f)
    items = data.get("items", [])
    logger.info("Loaded %d items from %s", len(items), input_path)
    return items


def filter_items(items: list[dict], status: Optional[str]) -> list[dict]:
    if status:
        filtered = [i for i in items if i.get("review_status") == status]
        logger.info(
            "Filtered to %d items with review_status='%s'", len(filtered), status
        )
        return filtered
    return items


def run_validation(
    items: list[dict], topic_map: dict, abort_on_failure: bool
) -> tuple[list[dict], list[dict]]:
    """
    Returns (passing_items, failing_items).
    If abort_on_failure is True, exits immediately on any failure.
    """
    validator = ItemValidator(topic_map=topic_map)
    passing, failing = [], []

    for item in items:
        errors = validator.validate_all(item)
        if errors:
            failing.append({"item": item, "errors": errors})
            logger.warning(
                "FAIL %s: %s",
                item.get("item_id", "??")[:12],
                "; ".join(f"[{e.rule}] {e.detail}" for e in errors),
            )
            if abort_on_failure:
                logger.error("Aborting due to validation failure (--abort-on-failure).")
                sys.exit(1)
        else:
            passing.append(item)

    return passing, failing


def print_coverage(items: list[dict]) -> None:
    print(f"\n{'─'*60}")
    print("  Coverage Summary (approved items vs launch target)")
    print(f"{'─'*60}")
    for ref in LAUNCH_REFS:
        ref_items = [i for i in items if i.get("caps_ref") == ref]
        approved  = [i for i in ref_items if i.get("review_status") == "approved"]
        status = "✅" if len(approved) >= LAUNCH_TARGET else "⚠️ "
        print(
            f"  {status}  {ref:10s}  approved={len(approved):3d}/{LAUNCH_TARGET}  "
            f"total={len(ref_items)}"
        )
    print()


# ---------------------------------------------------------------------------
# DB upsert
# ---------------------------------------------------------------------------

async def upsert_items(items: list[dict], dry_run: bool) -> int:
    """
    Upserts items into the diagnostic_items table.
    Returns the count of rows inserted/updated.
    """
    if dry_run:
        logger.info("[DRY RUN] Would upsert %d items (no DB writes).", len(items))
        return len(items)

    try:
        from app.core.database import get_async_engine
        from app.repositories.item_bank_repository import ItemBankRepository
        from sqlalchemy.ext.asyncio import AsyncSession
    except ImportError as exc:
        logger.error("Cannot import DB dependencies: %s", exc)
        logger.error("Ensure the virtual environment is active and migrations have run.")
        sys.exit(2)

    engine = get_async_engine()
    count  = 0

    async with AsyncSession(engine, expire_on_commit=False) as session:
        repo = ItemBankRepository(session)
        for item in items:
            try:
                await repo.upsert(item)
                count += 1
            except Exception as exc:
                logger.error(
                    "Failed to upsert item %s: %s",
                    item.get("item_id", "??")[:12], exc,
                )
        await session.commit()

    logger.info("Upserted %d items into diagnostic_items.", count)
    return count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def run(args: argparse.Namespace) -> None:
    topic_map = load_topic_map()
    all_items = load_seed(args.input)
    items     = filter_items(all_items, args.status)

    if not items:
        logger.warning("No items to seed after filtering.")
        sys.exit(0)

    # Validate all items first
    passing, failing = run_validation(
        items, topic_map, abort_on_failure=args.abort_on_failure
    )

    if failing:
        logger.warning(
            "%d item(s) failed validation and will be skipped.", len(failing)
        )
        if not args.seed_valid_only:
            logger.error(
                "Use --seed-valid-only to seed passing items despite failures, "
                "or fix the failures first."
            )
            sys.exit(1)

    seed_items = passing if failing else items
    count = await upsert_items(seed_items, dry_run=args.dry_run)

    print_coverage(all_items)

    print(f"{'='*60}")
    print(f"  Seeding {'[DRY RUN] ' if args.dry_run else ''}Complete")
    print(f"{'='*60}")
    print(f"  Items loaded:      {len(all_items)}")
    print(f"  Items filtered:    {len(items)}")
    print(f"  Passed validation: {len(passing)}")
    print(f"  Failed validation: {len(failing)}")
    print(f"  Seeded to DB:      {count}")
    print(f"{'='*60}\n")

    if failing:
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and seed the CAPS item bank into PostgreSQL."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument(
        "--status",
        default="approved",
        help="Only seed items with this review_status (default: approved)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Validate only — do not write to the database",
    )
    parser.add_argument(
        "--seed-valid-only", action="store_true",
        help="Seed passing items even if some items fail validation",
    )
    parser.add_argument(
        "--abort-on-failure", action="store_true",
        help="Stop at the first validation failure",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
