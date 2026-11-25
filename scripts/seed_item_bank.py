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

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("seed_item_bank")

from app.modules.diagnostics.item_validator import ItemValidator
from app.services.content_scope_registry import ContentScopeRegistry

TOPIC_MAP_PATHS = [
    REPO_ROOT / "data" / "caps" / "topic_maps" / "caps_topic_map_grade4_maths.json",
    REPO_ROOT / "data" / "caps" / "caps_topic_map_grade4_maths.json",
]
DEFAULT_INPUT  = REPO_ROOT / "data" / "caps" / "grade4_maths_item_bank.json"
DEFAULT_REVIEW_REGISTER = REPO_ROOT / "data" / "caps" / "external_content_review_register.json"
DEFAULT_SCOPE_ID = "grade4_mathematics_en"
DEFAULT_TARGET = 40


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_topic_map(*, scope_id: str, registry: ContentScopeRegistry) -> dict:
    scope = registry.get_scope(scope_id)
    if scope.topic_map_path:
        topic_map_path = REPO_ROOT / scope.topic_map_path
        if topic_map_path.exists():
            with open(topic_map_path) as f:
                return json.load(f)
        logger.warning("Configured topic map missing for scope %s: %s", scope_id, topic_map_path)
    for path in TOPIC_MAP_PATHS:
        if path.exists():
            with open(path) as f:
                return json.load(f)
    logger.warning("Topic map not found — CAPS ref validation will be skipped.")
    return {}


def load_seed(input_path: Path) -> list[dict]:
    if not input_path.exists():
        logger.error("Seed file not found: %s", input_path)
        sys.exit(2)
    with open(input_path) as f:
        data = json.load(f)
    items = data.get("items", [])
    logger.info("Loaded %d items from %s", len(items), input_path)
    return items


SYNTHETIC_REVIEWER_IDS = {
    "00000000-0000-0000-0000-000000000001",
    "00000000-0000-0000-0000-000000000002",
}


def filter_items(items: list[dict], status: Optional[str]) -> list[dict]:
    filtered = [item for item in items if not status or item.get("review_status") == status]
    if status == "approved":
        invalid = [
            item for item in filtered
            if not item.get("reviewer_id")
            or str(item.get("reviewer_id")) in SYNTHETIC_REVIEWER_IDS
            or not item.get("reviewed_at")
        ]
        if invalid:
            raise ValueError(
                f"Refusing to seed {len(invalid)} approved item(s) without a non-synthetic "
                "reviewer_id and reviewed_at. Generated quality checks do not count as educator review."
            )
    logger.info(
        "Filtered to %d items%s", len(filtered),
        f" with review_status='{status}'" if status else "",
    )
    return filtered


def require_approved_for_seeding(items: list[dict]) -> None:
    non_approved = [item for item in items if item.get("review_status") != "approved"]
    if non_approved:
        raise ValueError(
            f"Refusing to seed {len(non_approved)} non-approved item(s) into the learner item bank."
        )


def validate_external_review_register(
    items: list[dict], register_path: Path
) -> None:
    """Require independently reviewed item/reviewer pairs before any DB seed."""
    approved = [item for item in items if item.get("review_status") == "approved"]
    if not approved:
        return
    if not register_path.is_file():
        raise ValueError(
            f"Refusing to seed approved content: independent review register is absent ({register_path})."
        )
    data = json.loads(register_path.read_text(encoding="utf-8"))
    entries = data.get("entries", []) if isinstance(data, dict) else []
    allowed = {
        (str(entry.get("item_id")), str(entry.get("reviewer_id")))
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("decision") == "approved"
        and entry.get("independent") is True
        and entry.get("reviewer_id")
        and str(entry.get("reviewer_id")) not in SYNTHETIC_REVIEWER_IDS
    }
    missing = [
        item for item in approved
        if (str(item.get("item_id")), str(item.get("reviewer_id"))) not in allowed
    ]
    if missing:
        raise ValueError(
            f"Refusing to seed {len(missing)} approved item(s) without a matching "
            "independent approval entry in the external review register."
        )


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


def _target_for_ref(scope_id: str, caps_ref: str, *, registry: ContentScopeRegistry) -> int:
    for target in registry.get_scope_targets(scope_id):
        if target.caps_ref == caps_ref:
            value = target.targets.get("diagnostic_items.approved")
            if value is not None:
                return int(value)
    return DEFAULT_TARGET


def print_coverage(items: list[dict], *, scope_id: str, registry: ContentScopeRegistry) -> None:
    print(f"\n{'─'*60}")
    print(f"  Coverage Summary ({scope_id} — approved items vs target)")
    print(f"{'─'*60}")
    scope = registry.get_scope(scope_id)
    refs = scope.caps_refs or sorted({str(item.get("caps_ref")) for item in items if item.get("caps_ref")})
    for ref in refs:
        ref_items = [i for i in items if i.get("caps_ref") == ref]
        approved  = [i for i in ref_items if i.get("review_status") == "approved"]
        target = _target_for_ref(scope_id, ref, registry=registry)
        status = "✅" if len(approved) >= target else "⚠️ "
        print(
            f"  {status}  {ref:10s}  approved={len(approved):3d}/{target}  "
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
    registry = ContentScopeRegistry()
    topic_map = load_topic_map(scope_id=args.scope_id, registry=registry)
    all_items = load_seed(args.input)
    items     = filter_items(all_items, args.status)
    require_approved_for_seeding(items)
    validate_external_review_register(items, args.review_register)

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

    print_coverage(all_items, scope_id=args.scope_id, registry=registry)

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
    parser.add_argument("--input", "--path", dest="input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument(
        "--review-register",
        type=Path,
        default=DEFAULT_REVIEW_REGISTER,
        help="Read-only independent educator approval register; the generator/seeder never writes this file.",
    )
    parser.add_argument(
        "--scope-id",
        default=DEFAULT_SCOPE_ID,
        help="Registry scope to use for topic-map and coverage-target lookup.",
    )
    parser.add_argument(
        "--db-url",
        help="Accepted for Phase 5 CI compatibility; DATABASE_URL remains the app source of truth.",
    )
    parser.add_argument(
        "--status",
        default="approved",
        help="Only seed items with this review_status (default: approved)",
    )
    parser.add_argument(
        "--dry-run", nargs="?", const="true", default="false",
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
    parser.add_argument(
        "--status-filter",
        dest="status",
        default=argparse.SUPPRESS,
        help="Phase 5 alias for --status.",
    )
    args = parser.parse_args()
    args.dry_run = str(args.dry_run).lower() in {"1", "true", "yes", "on"}
    return args


def main() -> None:
    args = parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
