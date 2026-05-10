#!/usr/bin/env python3
"""
scripts/ci_lesson_bank_check.py

L5-04 + L5-05 — EduBoost SA Phase 5

CI assertion script that performs two jobs:

  Job A (L5-04) — Lesson bank threshold check:
    Asserts that each of the three launch caps_refs has ≥8 approved lessons
    in the database.  Fails CI with exit code 1 if any ref is below threshold.

  Job B (L5-05) — Approved lesson integrity check:
    Runs all 8 validator rules on every approved lesson. Fails CI if any
    previously-approved lesson now fails schema or validation.

Usage:
  # Run both jobs (default, used in CI after lesson generation):
  python scripts/ci_lesson_bank_check.py

  # Run only the threshold check:
  python scripts/ci_lesson_bank_check.py --job threshold

  # Run only the integrity check:
  python scripts/ci_lesson_bank_check.py --job validate

  # Dry run (print report without exit codes):
  python scripts/ci_lesson_bank_check.py --dry-run

Exit codes:
  0  All checks passed.
  1  One or more checks failed (CI blocking).
  2  Configuration / database error.
"""

from __future__ import annotations

import argparse
import os
import sys
import json
import logging
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Logging setup — GitHub Actions compatible (::error:: annotations)
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)
log = logging.getLogger("ci_lesson_bank_check")

IN_CI = bool(os.environ.get("CI"))


def _ci_error(message: str) -> None:
    """Emit a GitHub Actions error annotation if running in CI."""
    if IN_CI:
        print(f"::error::{message}", flush=True)
    log.error(message)


def _ci_warning(message: str) -> None:
    if IN_CI:
        print(f"::warning::{message}", flush=True)
    log.warning(message)


def _ci_notice(message: str) -> None:
    if IN_CI:
        print(f"::notice::{message}", flush=True)
    log.info(message)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LAUNCH_CAPS_REFS: list[str] = ["4.M.1.1", "4.M.1.2", "4.M.1.3"]
MINIMUM_APPROVED_LESSONS: int = int(os.environ.get("MIN_APPROVED_LESSONS", "8"))


# ---------------------------------------------------------------------------
# Domain imports — lazy to allow the script to emit a clear error if the
# app package is not importable (e.g. wrong working directory in CI).
# ---------------------------------------------------------------------------

def _import_app_dependencies() -> tuple[Any, Any]:
    try:
        from app.modules.lessons.lesson_validator import LessonValidator
        from app.modules.lessons.caps_topic_map_service import CapsTopicMapService
        return LessonValidator, CapsTopicMapService
    except ImportError as exc:
        log.error(
            "Cannot import app modules.  Ensure you are running from the repo "
            "root with the virtualenv activated: %s",
            exc,
        )
        sys.exit(2)


def _import_db() -> Any:
    try:
        from app.repositories.lesson_repository import LessonRepository
        return LessonRepository
    except ImportError as exc:
        log.error("Cannot import LessonRepository: %s", exc)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class ThresholdResult:
    caps_ref: str
    approved_count: int
    threshold: int

    @property
    def passed(self) -> bool:
        return self.approved_count >= self.threshold


@dataclass
class IntegrityViolation:
    lesson_id: str
    caps_ref: str
    failed_rules: list[str]


@dataclass
class IntegrityResult:
    total_checked: int
    violations: list[IntegrityViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


# ---------------------------------------------------------------------------
# Job A: Threshold check (L5-04)
# ---------------------------------------------------------------------------

def run_threshold_check(repo: Any, dry_run: bool = False) -> list[ThresholdResult]:
    """
    Query the lesson repository for approved lesson counts per caps_ref.
    Returns one ThresholdResult per launch caps_ref.
    """
    results: list[ThresholdResult] = []
    for caps_ref in LAUNCH_CAPS_REFS:
        count = repo.count_approved_by_caps_ref(caps_ref)
        result = ThresholdResult(
            caps_ref=caps_ref,
            approved_count=count,
            threshold=MINIMUM_APPROVED_LESSONS,
        )
        results.append(result)

        if result.passed:
            _ci_notice(
                f"[THRESHOLD ✓] {caps_ref}: {count}/{MINIMUM_APPROVED_LESSONS} approved lessons"
            )
        else:
            _ci_error(
                f"[THRESHOLD ✗] {caps_ref}: only {count}/{MINIMUM_APPROVED_LESSONS} approved lessons "
                f"(need {MINIMUM_APPROVED_LESSONS - count} more)"
            )

    return results


# ---------------------------------------------------------------------------
# Job B: Approved lesson integrity (L5-05)
# ---------------------------------------------------------------------------

def run_integrity_check(
    repo: Any,
    validator_cls: Any,
    caps_map_service_cls: Any,
    dry_run: bool = False,
) -> IntegrityResult:
    """
    Run all validator rules on every approved lesson in the database.
    Returns an IntegrityResult listing any violations.
    """
    caps_svc = caps_map_service_cls()
    validator = validator_cls(caps_topic_map_service=caps_svc)

    approved_lessons: list[dict[str, Any]] = repo.list_approved_lessons()
    total = len(approved_lessons)
    violations: list[IntegrityViolation] = []

    log.info("Running integrity check on %d approved lessons …", total)

    for lesson in approved_lessons:
        lesson_id = str(lesson.get("lesson_id", "unknown"))
        caps_ref = str(lesson.get("caps_ref", "unknown"))

        result = validator.validate(lesson)
        if not result.is_valid:
            violation = IntegrityViolation(
                lesson_id=lesson_id,
                caps_ref=caps_ref,
                failed_rules=result.failed_rules,
            )
            violations.append(violation)
            _ci_error(
                f"[INTEGRITY ✗] lesson_id={lesson_id} caps_ref={caps_ref} "
                f"failed rules: {', '.join(result.failed_rules)}"
            )
        else:
            log.debug("  ✓ lesson_id=%s caps_ref=%s", lesson_id, caps_ref)

    if not violations:
        _ci_notice(
            f"[INTEGRITY ✓] All {total} approved lessons passed validation."
        )

    return IntegrityResult(total_checked=total, violations=violations)


# ---------------------------------------------------------------------------
# Report printer
# ---------------------------------------------------------------------------

def print_summary(
    threshold_results: list[ThresholdResult] | None,
    integrity_result: IntegrityResult | None,
) -> None:
    print("\n" + "=" * 60)
    print("  EduBoost SA — CI Lesson Bank Check Report")
    print("=" * 60)

    if threshold_results is not None:
        print("\nA. LESSON BANK THRESHOLD (L5-04)")
        print(f"   Minimum required: {MINIMUM_APPROVED_LESSONS} approved lessons per caps_ref")
        all_passed = all(r.passed for r in threshold_results)
        for r in threshold_results:
            status = "✓" if r.passed else "✗"
            print(f"   [{status}] {r.caps_ref}: {r.approved_count}/{r.threshold}")
        if not all_passed:
            failing = [r.caps_ref for r in threshold_results if not r.passed]
            print(f"\n   ❌ FAILED: {', '.join(failing)} below threshold")
        else:
            print("\n   ✅ All caps_refs meet the minimum lesson threshold")

    if integrity_result is not None:
        print("\nB. APPROVED LESSON INTEGRITY (L5-05)")
        print(f"   Lessons checked: {integrity_result.total_checked}")
        if integrity_result.violations:
            print(f"   Violations: {len(integrity_result.violations)}")
            for v in integrity_result.violations:
                print(f"     ✗ lesson_id={v.lesson_id} caps_ref={v.caps_ref}")
                print(f"       Failed rules: {', '.join(v.failed_rules)}")
            print("\n   ❌ FAILED: regression detected in approved lesson bank")
        else:
            print(f"\n   ✅ All {integrity_result.total_checked} approved lessons passed")

    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="EduBoost CI Lesson Bank Check")
    parser.add_argument(
        "--job",
        choices=["threshold", "validate", "both"],
        default="both",
        help="Which check to run (default: both)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print report without exiting with error codes",
    )
    parser.add_argument(
        "--output-json",
        metavar="FILE",
        help="Write JSON report to FILE (for CI artifact upload)",
    )
    args = parser.parse_args()

    LessonValidator, CapsTopicMapService = _import_app_dependencies()
    LessonRepository = _import_db()

    repo = LessonRepository()
    threshold_results: list[ThresholdResult] | None = None
    integrity_result: IntegrityResult | None = None

    if args.job in ("threshold", "both"):
        threshold_results = run_threshold_check(repo, dry_run=args.dry_run)

    if args.job in ("validate", "both"):
        integrity_result = run_integrity_check(
            repo,
            LessonValidator,
            CapsTopicMapService,
            dry_run=args.dry_run,
        )

    print_summary(threshold_results, integrity_result)

    # JSON report for CI artifact upload
    if args.output_json:
        report: dict[str, Any] = {}
        if threshold_results is not None:
            report["threshold"] = [
                {
                    "caps_ref": r.caps_ref,
                    "approved_count": r.approved_count,
                    "threshold": r.threshold,
                    "passed": r.passed,
                }
                for r in threshold_results
            ]
        if integrity_result is not None:
            report["integrity"] = {
                "total_checked": integrity_result.total_checked,
                "violations": [
                    {
                        "lesson_id": v.lesson_id,
                        "caps_ref": v.caps_ref,
                        "failed_rules": v.failed_rules,
                    }
                    for v in integrity_result.violations
                ],
                "passed": integrity_result.passed,
            }
        Path(args.output_json).write_text(json.dumps(report, indent=2))
        log.info("Report written to %s", args.output_json)

    if args.dry_run:
        return 0

    # Determine exit code
    threshold_ok = (
        threshold_results is None or all(r.passed for r in threshold_results)
    )
    integrity_ok = integrity_result is None or integrity_result.passed

    if threshold_ok and integrity_ok:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
