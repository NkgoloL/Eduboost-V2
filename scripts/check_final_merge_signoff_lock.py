#!/usr/bin/env python3
"""Validate final merge signoff lock."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_merge_signoff_lock.md"

REQUIRED_SNIPPETS = (
    "Final Merge Signoff Lock",
    "Cluster H release readiness check is green",
    "final project closeout attestation is present",
    "release owner execution guardrail is present",
    "Cluster H release evidence checksum index is present",
    "final release handoff package is present",
    "post-terminal audit readiness assertion is present",
    "beta release final index is present",
    "beta governance seal checklist is present",
    "final PR merge readiness contract is present",
    "branch sync and rebase checklist is complete",
    "Signoff ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "Reviewer",
    "Signoff Time UTC",
    "Merge Outcome",
    "Evidence Archive Location",
    "merge signoff must reference release candidate and commit SHA",
    "merge signoff must verify branch accepts non-force push",
    "merge signoff must verify generated artifacts are not unresolved",
    "merge signoff must verify Cluster H release readiness check is green",
    "merge signoff must preserve manual approval workflow references",
    "merge signoff must remain controlled staging/beta evidence",
    "merge signoff must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or replace manual approval",
    "make final-merge-signoff-lock-check",
)


@dataclass(frozen=True)
class FinalMergeSignoffLockResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalMergeSignoffLockResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalMergeSignoffLockResult(DOC.exists(), "lock present" if DOC.exists() else "lock missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalMergeSignoffLockResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final merge signoff lock check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
