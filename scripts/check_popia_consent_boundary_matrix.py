#!/usr/bin/env python3
"""Validate explicit POPIA consent-boundary decisions."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.generate_popia_consent_boundary_matrix import collect_rows


@dataclass(frozen=True)
class CheckResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[CheckResult]:
    results: list[CheckResult] = []
    rows = collect_rows()

    active = [row for row in rows if row.decision == "active_consent_required"]
    rights = [row for row in rows if row.decision == "rights_exercise_not_active_consent_blocked"]
    catalog = [row for row in rows if row.decision == "authenticated_catalog_boundary"]

    results.append(CheckResult("active_consent_required_count", bool(active), f"{len(active)} active routes"))
    results.append(CheckResult("rights_exercise_count", bool(rights), f"{len(rights)} rights routes"))
    results.append(CheckResult("catalog_boundary_count", bool(catalog), f"{len(catalog)} catalog routes"))

    for row in active:
        results.append(
            CheckResult(
                f"{row.router}::{row.function}",
                row.marker in {"require_active_consent_for_current_user", "require_active_consent"},
                f"active marker {row.marker}",
            )
        )

    for row in rights:
        results.append(
            CheckResult(
                f"{row.router}::{row.function}",
                row.marker == "rights_exercise",
                f"rights marker {row.marker}",
            )
        )

    expected = {
        ("lessons.py", "generate_lesson"),
        ("diagnostics.py", "submit_diagnostic"),
        ("study_plans.py", "generate_study_plan"),
        ("parents.py", "get_learner_progress"),
        ("popia.py", "create_export_request"),
        ("assessments.py", "submit_attempt"),
        ("onboarding.py", "submit_onboarding"),
    }
    present = {(row.router, row.function) for row in active}
    for key in sorted(expected):
        results.append(CheckResult(f"{key[0]}::{key[1]}", key in present, "expected active-consent route"))

    return results


def main() -> int:
    results = run_checks()
    print("POPIA consent-boundary matrix check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
