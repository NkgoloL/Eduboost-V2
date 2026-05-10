#!/usr/bin/env python3
"""Validate parent vertical journey evidence contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "frontend" / "parent_vertical_journey_contract.md"
INVENTORY = REPO_ROOT / "docs" / "frontend" / "frontend_route_inventory.md"

DOC_SNIPPETS = (
    "Parent Vertical Journey Contract",
    "parent signs in",
    "parent opens parent dashboard",
    "parent selects linked learner",
    "parent views learner progress/mastery",
    "parent views consent status and trust dashboard",
    "parent can grant or revoke consent",
    "parent can request learner data export",
    "parent can start data-rights request",
    "authorization denial",
    "does not expose unrelated learner data",
    "make parent-vertical-journey-contract-check",
)

INVENTORY_SNIPPETS = (
    "Frontend Route Inventory",
    "parent dashboard and learner progress",
    "consent and trust surfaces",
)


@dataclass(frozen=True)
class ParentJourneyResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ParentJourneyResult]:
    results: list[ParentJourneyResult] = []
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    inventory_text = INVENTORY.read_text(encoding="utf-8") if INVENTORY.exists() else ""

    results.append(
        ParentJourneyResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "contract present" if DOC.exists() else "contract missing")
    )

    for snippet in DOC_SNIPPETS:
        results.append(
            ParentJourneyResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    results.append(
        ParentJourneyResult(
            str(INVENTORY.relative_to(REPO_ROOT)),
            INVENTORY.exists(),
            "route inventory present" if INVENTORY.exists() else "route inventory missing",
        )
    )

    for snippet in INVENTORY_SNIPPETS:
        results.append(
            ParentJourneyResult(
                str(INVENTORY.relative_to(REPO_ROOT)),
                snippet in inventory_text,
                f"contains {snippet!r}" if snippet in inventory_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Parent vertical journey contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
