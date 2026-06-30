#!/usr/bin/env python3
"""Validate post-closeout maintenance boundary."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "post_closeout_maintenance_boundary.md"

REQUIRED_SNIPPETS = (
    "Post-Closeout Maintenance Boundary",
    "fix broken documentation links",
    "correct typographical errors",
    "update evidence references to existing artifacts",
    "add owner clarification without changing accountability",
    "add variance record to frozen scope variance register",
    "add checksum record to Cluster H release evidence checksum index",
    "add audit note to final release evidence ledger",
    "approve production launch",
    "execute deployment",
    "create release tags",
    "change release candidate identity without new decision record",
    "remove unresolved blocker evidence",
    "bypass manual approval workflow",
    "rewrite release owner decision outcome",
    "delete audit evidence",
    "maintenance must reference release candidate and commit SHA",
    "maintenance must preserve final release evidence ledger",
    "maintenance must preserve frozen scope variance register",
    "maintenance must preserve final evidence no-op execution assertion",
    "maintenance must preserve release owner post-closeout decision record",
    "maintenance must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or alter release outcome",
    "make post-closeout-maintenance-boundary-check",
)


@dataclass(frozen=True)
class PostCloseoutMaintenanceBoundaryResult:
    ok: bool
    detail: str


def run_checks() -> list[PostCloseoutMaintenanceBoundaryResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [PostCloseoutMaintenanceBoundaryResult(DOC.exists(), "boundary present" if DOC.exists() else "boundary missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            PostCloseoutMaintenanceBoundaryResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Post-closeout maintenance boundary check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
