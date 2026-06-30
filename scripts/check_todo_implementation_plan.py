#!/usr/bin/env python3
"""Validate that the TODO implementation plan covers outstanding tasks."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TODO = REPO_ROOT / "TODO.md"
PLAN = REPO_ROOT / "docs" / "operations" / "todo_implementation_plan.md"

NS_ID_RE = re.compile(r"NS-\d{2}")


@dataclass(frozen=True)
class PlanCheckResult:
    ok: bool
    detail: str


def _todo_rows() -> list[str]:
    return [
        line
        for line in TODO.read_text(encoding="utf-8").splitlines()
        if line.startswith("| NS-")
    ]


def outstanding_todo_ids() -> list[str]:
    ids: list[str] = []
    for row in _todo_rows():
        if "| [x] |" in row:
            continue
        match = NS_ID_RE.search(row)
        if match:
            ids.append(match.group(0))
    return sorted(set(ids), key=lambda item: int(item.split("-")[1]))


def plan_ids() -> set[str]:
    text = PLAN.read_text(encoding="utf-8") if PLAN.exists() else ""
    return set(NS_ID_RE.findall(text))


def run_checks() -> list[PlanCheckResult]:
    results = [
        PlanCheckResult(
            TODO.exists(),
            "TODO.md present" if TODO.exists() else "TODO.md missing",
        ),
        PlanCheckResult(
            PLAN.exists(),
            "implementation plan present" if PLAN.exists() else "implementation plan missing",
        ),
    ]

    if not TODO.exists() or not PLAN.exists():
        return results

    plan_text = PLAN.read_text(encoding="utf-8")
    outstanding = outstanding_todo_ids()
    covered = plan_ids()
    missing = [todo_id for todo_id in outstanding if todo_id not in covered]

    results.append(
        PlanCheckResult(
            bool(outstanding),
            f"found {len(outstanding)} outstanding TODO IDs"
            if outstanding
            else "no outstanding TODO IDs found",
        )
    )
    results.append(
        PlanCheckResult(
            not missing,
            "all outstanding TODO IDs are covered"
            if not missing
            else f"missing TODO IDs: {', '.join(missing)}",
        )
    )
    results.append(
        PlanCheckResult(
            "EduBoost remains not public-beta-ready" in plan_text,
            "no-go posture preserved"
            if "EduBoost remains not public-beta-ready" in plan_text
            else "missing no-go posture",
        )
    )
    return results


def main() -> int:
    results = run_checks()
    print("TODO implementation plan check")
    print("Scope: plan coverage only; not task completion evidence")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
