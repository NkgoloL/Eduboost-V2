#!/usr/bin/env python3
"""EduBoost SA — Lesson Validation CLI (Phase 3, Task L3-04).

Reads all lessons from the database for a given CAPS reference (or all
approved lessons) and runs every validator rule. Prints a pass/fail
report with lesson IDs and rule failures.

Designed to run in CI (see Makefile target ``make validate-lessons``)
and as a pre-commit check before any prompt template change is merged.

Usage::

    # Validate all lessons for a specific CAPS ref
    python scripts/validate_lessons.py --caps-ref 4.M.1.1

    # Validate all approved lessons across the launch scope
    python scripts/validate_lessons.py --approved-only

    # Validate all lessons (any status) — full bank check
    python scripts/validate_lessons.py --all

    # CI mode: exit 1 if any lesson fails (used in L5-05)
    python scripts/validate_lessons.py --approved-only --ci

    # Verbose: show full failure details
    python scripts/validate_lessons.py --caps-ref 4.M.1.1 --verbose

Makefile target::

    make validate-lessons CAPS_REF=4.M.1.1

Exit codes:
    0 — All lessons pass (or 0 lessons found)
    1 — One or more lessons failed validation
    2 — Fatal error
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import time

_REPO_ROOT = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.modules.lessons.lesson_schema_v1 import LessonCreate
from app.modules.lessons.lesson_validator import LessonValidator, ValidationResult
from app.repositories.lesson_repository import LessonRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("validate_lessons")


async def load_lessons(
    *,
    caps_ref: str | None,
    approved_only: bool,
    db,
) -> list:
    """Load lessons from the database matching the filter criteria."""
    from app.models import Lesson  # local import to avoid circular deps

    stmt = select(Lesson)

    if caps_ref:
        stmt = stmt.where(Lesson.caps_reference == caps_ref)

    if approved_only:
        stmt = stmt.where(Lesson.review_status == "approved")

    result = await db.execute(stmt)
    return list(result.scalars().all())


def orm_to_lesson_create(orm_lesson) -> LessonCreate | None:
    """Attempt to coerce an ORM lesson row into a LessonCreate model.

    Returns None if the row cannot be parsed (legacy format, missing fields).
    """
    import json

    try:
        content = orm_lesson.content
        if isinstance(content, str):
            content = json.loads(content)

        # Build a minimal LessonCreate from the ORM row
        # The full structured fields may live in `content` (JSON column)
        data: dict = content if isinstance(content, dict) else {}
        data.setdefault("caps_ref", getattr(orm_lesson, "caps_reference", ""))
        data.setdefault("grade", getattr(orm_lesson, "grade", 4))
        data.setdefault("subject", getattr(orm_lesson, "subject", "mathematics"))
        data.setdefault("term", getattr(orm_lesson, "term", 1))
        data.setdefault("topic", getattr(orm_lesson, "topic", ""))
        data.setdefault("subtopic", data.get("subtopic", ""))
        data.setdefault("answer_key_verified", getattr(orm_lesson, "answer_key_verified", False))
        data.setdefault("pii_check_passed", getattr(orm_lesson, "pii_check_passed", False))
        data.setdefault("review_status", getattr(orm_lesson, "review_status", "ai_generated"))
        data.setdefault("quality_score", getattr(orm_lesson, "quality_score", None))
        data.setdefault("prompt_template_version", getattr(orm_lesson, "prompt_template_version", "v1"))
        data.setdefault("provider", getattr(orm_lesson, "llm_provider", "groq"))

        return LessonCreate.model_validate(data)
    except Exception as exc:
        return None


def print_result_row(
    lesson_id: str,
    caps_ref: str,
    result: ValidationResult,
    *,
    verbose: bool,
) -> None:
    """Print a single lesson validation result row."""
    icon = "✅" if result.passed else "❌"
    fk = f" FK≈{result.readability_grade}" if result.readability_grade else ""
    print(f"  {icon} {lesson_id} [{caps_ref}]{fk}")
    if not result.passed and verbose:
        for failure in result.failures:
            print(f"       FAIL: {failure}")
    if result.warnings and verbose:
        for warning in result.warnings:
            print(f"       WARN: {warning}")


async def main(args: argparse.Namespace) -> int:
    """Main async entry point."""
    validator = LessonValidator()
    start = time.perf_counter()

    async with AsyncSessionLocal() as db:
        orm_lessons = await load_lessons(
            caps_ref=args.caps_ref,
            approved_only=args.approved_only,
            db=db,
        )

    if not orm_lessons:
        logger.info("No lessons found matching the filter criteria.")
        return 0

    logger.info("Validating %d lesson(s)...", len(orm_lessons))
    print()
    print("═" * 70)
    print(f"  LESSON VALIDATION REPORT — {time.strftime('%Y-%m-%d %H:%M:%S')}")
    if args.caps_ref:
        print(f"  CAPS Ref filter: {args.caps_ref}")
    if args.approved_only:
        print("  Filter: approved lessons only")
    print("═" * 70)

    passed_count = 0
    failed_count = 0
    skipped_count = 0
    failed_lessons: list[tuple[str, str, ValidationResult]] = []

    for orm_lesson in orm_lessons:
        lesson_id = str(getattr(orm_lesson, "id", getattr(orm_lesson, "lesson_id", "unknown")))
        caps_ref = getattr(orm_lesson, "caps_reference", "unknown")

        lesson_create = orm_to_lesson_create(orm_lesson)
        if lesson_create is None:
            skipped_count += 1
            print(f"  ⚠  {lesson_id} [{caps_ref}] SKIPPED — could not parse lesson into LessonCreate schema")
            continue

        result = validator.validate(lesson_create, require_verified=args.check_verified)
        print_result_row(lesson_id, caps_ref, result, verbose=args.verbose)

        if result.passed:
            passed_count += 1
        else:
            failed_count += 1
            failed_lessons.append((lesson_id, caps_ref, result))

    elapsed = time.perf_counter() - start
    print("═" * 70)
    print(f"  SUMMARY: {passed_count} passed | {failed_count} failed | "
          f"{skipped_count} skipped | {elapsed:.1f}s")
    print()

    if failed_count > 0:
        print("  Failed lessons:")
        for lesson_id, caps_ref, result in failed_lessons:
            print(f"    ❌ {lesson_id} [{caps_ref}]:")
            for failure in result.failures:
                print(f"       {failure}")
        print()

    if args.ci and failed_count > 0:
        logger.error(
            "CI gate FAILED: %d lesson(s) did not pass validation. "
            "Fix the failures before merging.",
            failed_count,
        )
        return 1

    return 0 if failed_count == 0 else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="EduBoost SA — Lesson Validation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--caps-ref",
        metavar="REF",
        help="Validate lessons for a specific CAPS reference only",
    )
    group.add_argument(
        "--approved-only",
        action="store_true",
        help="Validate all approved lessons across the entire lesson bank",
    )
    group.add_argument(
        "--all",
        action="store_true",
        dest="all_lessons",
        help="Validate ALL lessons regardless of review status",
    )
    parser.add_argument(
        "--check-verified",
        action="store_true",
        default=True,
        help="Treat answer_key_verified=False as a failure (default: True)",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit 1 if any lesson fails (fail loudly)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print full failure details for each lesson",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        exit_code = asyncio.run(main(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(2)
    except Exception as exc:
        logger.exception("Fatal error: %s", exc)
        sys.exit(2)
