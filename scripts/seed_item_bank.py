#!/usr/bin/env python3
"""
P1-09 — scripts/seed_item_bank.py
==================================
Reads the canonical seed JSON file, validates every item against the Pydantic
schema, then upserts them into the database via the SQLAlchemy ORM.

Usage
-----
    # Dry run (validate only, no DB writes):
    python scripts/seed_item_bank.py --dry-run

    # Seed all items from the default file:
    python scripts/seed_item_bank.py

    # Seed from an explicit file:
    python scripts/seed_item_bank.py --seed-file data/caps/grade4_maths_item_bank.json

    # Seed only approved items:
    python scripts/seed_item_bank.py --approved-only

    # Via Makefile:
    make seed-items

Exit codes
----------
    0 — all items seeded (or dry-run passed)
    1 — one or more validation failures
    2 — database error

Place this file at: scripts/seed_item_bank.py
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Path setup — allow running from repo root without installing the package
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from pydantic import ValidationError
from sqlalchemy import create_engine, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.item_schema import ItemCreate, ReviewStatus
from app.models.diagnostic_item import DiagnosticItem, ReviewStatusEnum

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_SEED_FILE = _REPO_ROOT / "data" / "caps" / "grade4_maths_item_bank.json"

CAPS_REF_PATTERN_HELP = "Grade.SubjectCode.Term.TopicIdx.SubtopicIdx  e.g. 4.M.1.1.1"

# ANSI colours for terminal output
_GREEN = "\033[92m"
_RED = "\033[91m"
_YELLOW = "\033[93m"
_BLUE = "\033[94m"
_RESET = "\033[0m"
_BOLD = "\033[1m"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print_header(text: str) -> None:
    print(f"\n{_BOLD}{_BLUE}{'=' * 60}{_RESET}")
    print(f"{_BOLD}{_BLUE}  {text}{_RESET}")
    print(f"{_BOLD}{_BLUE}{'=' * 60}{_RESET}")


def _ok(msg: str) -> None:
    print(f"  {_GREEN}✓{_RESET} {msg}")


def _warn(msg: str) -> None:
    print(f"  {_YELLOW}⚠{_RESET} {msg}")


def _fail(msg: str) -> None:
    print(f"  {_RED}✗{_RESET} {msg}", file=sys.stderr)


def _load_seed_file(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Load and return the seed file metadata and items list."""
    if not path.exists():
        _fail(f"Seed file not found: {path}")
        sys.exit(1)

    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    if "items" not in data:
        _fail("Seed file has no 'items' key.")
        sys.exit(1)

    return data, data["items"]


def _validate_items(
    raw_items: list[dict[str, Any]],
    approved_only: bool,
) -> tuple[list[ItemCreate], list[tuple[int, str]]]:
    """
    Validate every raw item dict against the ItemCreate Pydantic schema.

    Returns:
        valid_items   — list of ItemCreate instances
        errors        — list of (index, error_message) for failed items
    """
    valid: list[ItemCreate] = []
    errors: list[tuple[int, str]] = []

    for i, raw in enumerate(raw_items):
        try:
            item = ItemCreate(**raw)
            if approved_only and raw.get("review_status") != ReviewStatus.APPROVED.value:
                continue
            valid.append(item)
        except ValidationError as exc:
            errors.append((i, str(exc)))

    return valid, errors


def _upsert_items(
    session: Session,
    items: list[ItemCreate],
    raw_items: list[dict[str, Any]],
) -> tuple[int, int, int]:
    """
    Upsert items into diagnostic_items using PostgreSQL ON CONFLICT DO UPDATE.

    Returns:
        (inserted, updated, skipped) counts
    """
    inserted = 0
    updated = 0
    skipped = 0

    # Build a lookup from ItemCreate to the raw dict (for review metadata)
    # We need item_id if supplied in the seed file
    raw_by_index = {i: r for i, r in enumerate(raw_items)}

    for idx, item in enumerate(items):
        raw = {}
        # Match by position (items and raw_items are parallel after filtering)
        # In practice, the seed file should include item_id for idempotency
        for i, r in raw_by_index.items():
            try:
                ItemCreate(**r)
            except Exception:
                continue
            raw = r
            del raw_by_index[i]
            break

        item_id = raw.get("item_id") or str(uuid.uuid4())

        values: dict[str, Any] = {
            "item_id": item_id,
            "caps_ref": item.caps_ref,
            "grade": item.grade,
            "subject": item.subject.value,
            "term": item.term,
            "topic": item.topic,
            "subtopic": item.subtopic,
            "skill": item.skill,
            "stem": item.stem,
            "answer_key": item.answer_key,
            "options": (
                [o.model_dump() for o in item.options] if item.options else None
            ),
            "explanation": item.explanation,
            "distractor_rationale": (
                [d.model_dump() for d in item.distractor_rationale]
                if item.distractor_rationale
                else None
            ),
            "misconception_tags": item.misconception_tags,
            "item_type": item.item_type.value,
            "language": item.language.value,
            "difficulty_b": float(item.difficulty_b),
            "discrimination_a": float(item.discrimination_a),
            "guessing_c": float(item.guessing_c),
            "difficulty_band": item.difficulty_band.value,
            "review_status": raw.get("review_status", "draft"),
            "reviewer_id": raw.get("reviewer_id"),
            "reviewed_at": raw.get("reviewed_at"),
            "exposure_count": raw.get("exposure_count", 0),
            "max_exposure": item.max_exposure,
            "quality_score": raw.get("quality_score"),
            "safety_passed": item.safety_passed,
            "source": item.source.value,
            "created_at": raw.get("created_at", datetime.now(timezone.utc).isoformat()),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        stmt = (
            pg_insert(DiagnosticItem)
            .values(**values)
            .on_conflict_do_update(
                index_elements=["item_id"],
                set_={
                    # Update content fields; preserve exposure_count and created_at
                    "caps_ref": values["caps_ref"],
                    "stem": values["stem"],
                    "answer_key": values["answer_key"],
                    "options": values["options"],
                    "explanation": values["explanation"],
                    "distractor_rationale": values["distractor_rationale"],
                    "misconception_tags": values["misconception_tags"],
                    "difficulty_b": values["difficulty_b"],
                    "discrimination_a": values["discrimination_a"],
                    "guessing_c": values["guessing_c"],
                    "difficulty_band": values["difficulty_band"],
                    "review_status": values["review_status"],
                    "reviewer_id": values["reviewer_id"],
                    "reviewed_at": values["reviewed_at"],
                    "quality_score": values["quality_score"],
                    "safety_passed": values["safety_passed"],
                    "updated_at": values["updated_at"],
                },
            )
        )

        result = session.execute(stmt)
        # rowcount=1 on insert, 1 on update; we distinguish via the RETURNING clause
        # For simplicity, track as inserted (upsert semantics)
        inserted += 1

    return inserted, updated, skipped


def _print_coverage_summary(session: Session) -> None:
    """Print a per-CAPS-ref coverage table after seeding."""
    _print_header("Item Bank Coverage Summary")

    rows = session.execute(
        text(
            """
            SELECT
                caps_ref,
                COUNT(*) FILTER (WHERE review_status = 'approved')  AS approved,
                COUNT(*) FILTER (WHERE review_status = 'draft')      AS draft,
                COUNT(*) FILTER (WHERE review_status = 'ai_generated') AS ai_gen,
                COUNT(*) FILTER (WHERE review_status = 'retired')    AS retired,
                COUNT(*)                                              AS total
            FROM diagnostic_items
            WHERE grade = 4 AND subject = 'Mathematics'
            GROUP BY caps_ref
            ORDER BY caps_ref
            """
        )
    ).fetchall()

    if not rows:
        _warn("No Grade 4 Mathematics items found in the database.")
        return

    TARGET = 40
    print(f"\n  {'CAPS Ref':<14} {'Approved':>8} {'Draft':>6} {'AI Gen':>7} {'Retired':>8} {'Total':>6} {'Coverage':>9}")
    print(f"  {'-' * 14} {'-' * 8} {'-' * 6} {'-' * 7} {'-' * 8} {'-' * 6} {'-' * 9}")

    total_approved = 0
    for row in rows:
        coverage = row.approved / TARGET * 100
        indicator = _GREEN if row.approved >= TARGET else (_YELLOW if row.approved > 0 else _RED)
        total_approved += row.approved
        print(
            f"  {row.caps_ref:<14} "
            f"{indicator}{row.approved:>8}{_RESET} "
            f"{row.draft:>6} "
            f"{row.ai_gen:>7} "
            f"{row.retired:>8} "
            f"{row.total:>6} "
            f"{indicator}{coverage:>8.1f}%{_RESET}"
        )

    print()
    launch_refs = {"4.M.1.1", "4.M.1.2", "4.M.1.3"}
    launch_ready = all(
        any(row.caps_ref.startswith(ref) and row.approved >= TARGET for row in rows)
        for ref in launch_refs
    )
    if launch_ready:
        _ok(f"MVP launch scope complete: {total_approved} approved items ≥ {TARGET * 3} target")
    else:
        _warn(f"MVP launch scope NOT yet complete: {total_approved} / {TARGET * 3} approved items")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed the EduBoost CAPS item bank from a JSON file into the database.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--seed-file",
        type=Path,
        default=DEFAULT_SEED_FILE,
        help=f"Path to the seed JSON file (default: {DEFAULT_SEED_FILE})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate items against the schema without writing to the database",
    )
    parser.add_argument(
        "--approved-only",
        action="store_true",
        help="Only seed items with review_status=approved",
    )
    parser.add_argument(
        "--database-url",
        type=str,
        default=None,
        help="Override DATABASE_URL from environment (useful for CI)",
    )
    args = parser.parse_args()

    _print_header("EduBoost — CAPS Item Bank Seeder")
    print(f"  Seed file   : {args.seed_file}")
    print(f"  Dry run     : {args.dry_run}")
    print(f"  Approved only: {args.approved_only}")

    # ------------------------------------------------------------------
    # 1. Load seed file
    # ------------------------------------------------------------------
    metadata, raw_items = _load_seed_file(args.seed_file)
    print(f"\n  Schema version : {metadata.get('schema_version', 'unknown')}")
    print(f"  Grade/Subject  : {metadata.get('grade')} {metadata.get('subject')}")
    print(f"  Items in file  : {len(raw_items)}")

    if not raw_items:
        _warn("Seed file contains 0 items. Nothing to do.")
        print()
        sys.exit(0)

    # ------------------------------------------------------------------
    # 2. Validate all items
    # ------------------------------------------------------------------
    _print_header("Validating Items")
    valid_items, errors = _validate_items(raw_items, args.approved_only)

    if errors:
        for idx, msg in errors:
            _fail(f"Item index {idx}: {msg}")
        print(f"\n  {_RED}{len(errors)} validation error(s) — aborting.{_RESET}")
        sys.exit(1)

    _ok(f"{len(valid_items)} items passed schema validation")

    if args.dry_run:
        _ok("Dry run complete — no database writes.")
        _print_header("Done")
        sys.exit(0)

    # ------------------------------------------------------------------
    # 3. Connect to database and upsert
    # ------------------------------------------------------------------
    db_url = args.database_url or settings.DATABASE_URL
    _print_header("Seeding Database")
    print(f"  Connecting to database …")

    try:
        # Use synchronous engine for the CLI seed script
        sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        engine = create_engine(sync_url, echo=False)

        with Session(engine) as session:
            inserted, updated, skipped = _upsert_items(session, valid_items, raw_items)
            session.commit()

        _ok(f"Upserted {inserted} items (inserted/updated)")
        if skipped:
            _warn(f"Skipped {skipped} items (already at max or filtered out)")

        # ------------------------------------------------------------------
        # 4. Print coverage summary
        # ------------------------------------------------------------------
        with Session(engine) as session:
            _print_coverage_summary(session)

    except Exception as exc:
        _fail(f"Database error: {exc}")
        sys.exit(2)

    _print_header("Done")
    print(f"  {_GREEN}{_BOLD}Item bank seeding complete.{_RESET}")
    print()


if __name__ == "__main__":
    main()
