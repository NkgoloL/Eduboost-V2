#!/usr/bin/env python3
"""Validate archival lock assertion."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "archival_lock_assertion.md"

REQUIRED_SNIPPETS = (
    "Archival Lock Assertion",
    "final acceptance packet index is present",
    "release handoff freeze assertion is present",
    "post-closeout evidence access policy is present",
    "final release evidence ledger is present",
    "frozen scope variance register is present",
    "post-closeout maintenance boundary is present",
    "final evidence no-op execution assertion is present",
    "Cluster H release evidence checksum index is present",
    "final project closeout attestation is present",
    "release owner post-closeout decision record is present",
    "archival lock must reference release candidate and commit SHA",
    "archival lock must preserve final acceptance packet references",
    "archival lock must preserve handoff freeze references",
    "archival lock must preserve access policy references",
    "archival lock must preserve ledger and checksum references",
    "archival lock must preserve frozen scope variance references",
    "archival lock must remain controlled staging/beta evidence",
    "archival lock does not approve production launch",
    "archival lock does not execute deployment",
    "archival lock does not create release tags",
    "archival lock does not bypass manual approval",
    "archival lock does not rewrite source control history",
    "archival lock does not delete audit evidence",
    "does not approve production launch, execute deployment, create release tags, or replace manual approval",
    "make archival-lock-assertion-check",
)


@dataclass(frozen=True)
class ArchivalLockAssertionResult:
    ok: bool
    detail: str


def run_checks() -> list[ArchivalLockAssertionResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [ArchivalLockAssertionResult(DOC.exists(), "assertion present" if DOC.exists() else "assertion missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ArchivalLockAssertionResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Archival lock assertion check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
