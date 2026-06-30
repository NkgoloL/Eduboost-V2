#!/usr/bin/env python3
"""EduBoost SA — Batch Lesson Generation CLI (Phase 3, Task L3-03).

Generates lessons for one or more CAPS references, validates them,
and writes passing lessons to the database.

Usage::

    # Generate 15 candidates for 4.M.1.1 (Whole Numbers), keep those that pass
    python scripts/generate_lessons.py --caps-ref 4.M.1.1 --n-lessons 15

    # Dry run — validate without persisting to DB
    python scripts/generate_lessons.py --caps-ref 4.M.1.1 --dry-run

    # Generate across all Grade 4 Maths launch scope refs
    python scripts/generate_lessons.py --grade 4 --subject M

    # Full launch scope batch with verbose output
    python scripts/generate_lessons.py \\
        --caps-ref 4.M.1.1 4.M.1.2 4.M.1.3 \\
        --n-lessons 15 \\
        --difficulty on_level \\
        --verbose

Makefile target::

    make generate-lessons CAPS_REF=4.M.1.1

Exit codes:
    0 — All attempted refs produced ≥ min-passing lessons
    1 — One or more refs fell below the min-passing threshold
    2 — Fatal error (DB connection, import error, etc.)
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import time
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Bootstrap Django-style: ensure project root is on sys.path before imports
# ---------------------------------------------------------------------------
import os

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from app.core.database import AsyncSessionLocal
from app.modules.lessons.lesson_generator import LessonGenerator, LessonGenerationError
from app.modules.lessons.lesson_validator import LessonValidationError
from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("generate_lessons")


@dataclass
class RefResult:
    """Generation result for a single CAPS reference."""

    caps_ref: str
    attempted: int = 0
    passed: int = 0
    failed_schema: int = 0
    failed_validation: int = 0
    failed_llm: int = 0
    queued_for_review: int = 0
    errors: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0

    @property
    def pass_rate(self) -> float:
        return self.passed / self.attempted if self.attempted else 0.0

    def summary_line(self) -> str:
        return (
            f"  {self.caps_ref}: {self.passed}/{self.attempted} passed "
            f"({self.pass_rate:.0%}) | "
            f"schema_fail={self.failed_schema} "
            f"validation_fail={self.failed_validation} "
            f"llm_fail={self.failed_llm} "
            f"review_queue={self.queued_for_review} "
            f"elapsed={self.elapsed_seconds:.1f}s"
        )


async def generate_for_ref(
    caps_ref: str,
    *,
    n_lessons: int,
    difficulty: str,
    dry_run: bool,
    verbose: bool,
    misconception_tags: list[str],
) -> RefResult:
    """Generate ``n_lessons`` candidates for a single CAPS reference.

    Stops early if ``n_lessons`` have been attempted. Counts pass/fail
    per error type. Does not raise — all errors are captured in the result.
    """
    result = RefResult(caps_ref=caps_ref)
    start = time.perf_counter()

    async with AsyncSessionLocal() as db:
        generator = LessonGenerator(db)

        for attempt in range(1, n_lessons + 1):
            result.attempted += 1
            if verbose:
                logger.info("[%s] Attempt %d/%d ...", caps_ref, attempt, n_lessons)

            try:
                lesson = await generator.generate(
                    caps_ref,
                    difficulty=difficulty,
                    misconception_tags=misconception_tags,
                    dry_run=dry_run,
                )
                result.passed += 1

                if not lesson.answer_key_verified:
                    result.queued_for_review += 1
                    if verbose:
                        logger.warning(
                            "[%s] Attempt %d: PASSED validation but queued for "
                            "human review (answer_key_verified=False)",
                            caps_ref,
                            attempt,
                        )
                elif verbose:
                    logger.info(
                        "[%s] Attempt %d: PASSED quality=%.2f verified=%s",
                        caps_ref,
                        attempt,
                        lesson.quality_score or 0.0,
                        lesson.answer_key_verified,
                    )

            except LessonValidationError as exc:
                result.failed_validation += 1
                msg = f"Attempt {attempt} validation fail: {exc.failures}"
                result.errors.append(msg)
                if verbose:
                    logger.warning("[%s] %s", caps_ref, msg)

            except LessonGenerationError as exc:
                result.failed_llm += 1
                msg = f"Attempt {attempt} LLM/schema fail: {exc}"
                result.errors.append(msg)
                if verbose:
                    logger.warning("[%s] %s", caps_ref, msg)

            except Exception as exc:
                result.failed_schema += 1
                msg = f"Attempt {attempt} unexpected error: {type(exc).__name__}: {exc}"
                result.errors.append(msg)
                logger.error("[%s] %s", caps_ref, msg, exc_info=True)

            # Small delay between calls to avoid provider rate limits
            if attempt < n_lessons:
                await asyncio.sleep(0.5)

    result.elapsed_seconds = time.perf_counter() - start
    return result


async def main(args: argparse.Namespace) -> int:
    """Main async entry point. Returns process exit code."""
    caps_service = CAPSTopicMapService()

    # Resolve caps refs
    caps_refs: list[str] = []
    if args.caps_ref:
        caps_refs = list(args.caps_ref)
    elif args.grade and args.subject:
        caps_refs = [
            meta["caps_ref"]
            for meta in caps_service.list_topics(args.grade, args.subject)
        ]
        if not caps_refs:
            logger.error(
                "No CAPS refs found for grade=%s subject=%s", args.grade, args.subject
            )
            return 2
    else:
        logger.error("Must specify --caps-ref or both --grade and --subject")
        return 2

    # Validate all refs exist in topic map before generating
    unknown = [r for r in caps_refs if not caps_service.validate_caps_ref(r)]
    if unknown:
        logger.error(
            "Unknown CAPS references (not in topic map): %s. "
            "Update data/caps/caps_topic_map_grade4_maths.json first.",
            unknown,
        )
        return 2

    logger.info(
        "Starting lesson generation: %d ref(s), %d candidates each, difficulty=%s %s",
        len(caps_refs),
        args.n_lessons,
        args.difficulty,
        "(DRY RUN — no DB writes)" if args.dry_run else "",
    )

    results: list[RefResult] = []

    for caps_ref in caps_refs:
        logger.info("── Generating for %s ──", caps_ref)
        result = await generate_for_ref(
            caps_ref,
            n_lessons=args.n_lessons,
            difficulty=args.difficulty,
            dry_run=args.dry_run,
            verbose=args.verbose,
            misconception_tags=args.misconception_tags or [],
        )
        results.append(result)

        logger.info(result.summary_line())

        if args.verbose and result.errors:
            logger.info("  Errors for %s:", caps_ref)
            for err in result.errors[:5]:  # Show first 5 errors
                logger.info("    %s", err)

    # ── Final report ──────────────────────────────────────────────────────
    print("\n" + "═" * 70)
    print(f"  LESSON GENERATION REPORT — {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 70)
    for r in results:
        status_icon = "✅" if r.passed >= args.min_passing else "❌"
        print(f"  {status_icon} {r.summary_line()}")
    print("═" * 70)

    total_passed = sum(r.passed for r in results)
    total_attempted = sum(r.attempted for r in results)
    total_review = sum(r.queued_for_review for r in results)
    print(f"  TOTAL: {total_passed}/{total_attempted} passed | "
          f"{total_review} queued for review")

    if args.dry_run:
        print("  ⚠  DRY RUN — no lessons were persisted to the database.")
    print()

    # Exit 1 if any ref fell below the min-passing threshold
    below_threshold = [r for r in results if r.passed < args.min_passing]
    if below_threshold:
        logger.warning(
            "%d ref(s) below min-passing threshold (%d): %s",
            len(below_threshold),
            args.min_passing,
            [r.caps_ref for r in below_threshold],
        )
        return 1

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="EduBoost SA — Batch Lesson Generation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ref_group = parser.add_mutually_exclusive_group()
    ref_group.add_argument(
        "--caps-ref",
        nargs="+",
        metavar="REF",
        help="One or more CAPS references (e.g. 4.M.1.1 4.M.1.2)",
    )
    parser.add_argument(
        "--grade",
        type=int,
        metavar="N",
        help="Grade level (used with --subject to list all refs)",
    )
    parser.add_argument(
        "--subject",
        metavar="CODE",
        help="Subject code: M=Maths, E=English, etc. (used with --grade)",
    )
    parser.add_argument(
        "--n-lessons",
        type=int,
        default=15,
        metavar="N",
        help="Number of lesson candidates to attempt per caps-ref (default: 15)",
    )
    parser.add_argument(
        "--min-passing",
        type=int,
        default=8,
        metavar="N",
        help="Minimum passing lessons per caps-ref before exit code = 1 (default: 8)",
    )
    parser.add_argument(
        "--difficulty",
        choices=["foundational", "developing", "on_level", "extending"],
        default="on_level",
        help="Lesson difficulty level (default: on_level)",
    )
    parser.add_argument(
        "--misconception-tags",
        nargs="*",
        metavar="TAG",
        default=[],
        help="Optional learner misconception tags for targeted remediation",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate lessons without writing to the database",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print per-attempt results",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        exit_code = asyncio.run(main(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(2)
    except Exception as exc:
        logger.exception("Fatal error: %s", exc)
        sys.exit(2)
