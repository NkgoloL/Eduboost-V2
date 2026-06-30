#!/usr/bin/env python3
"""Validate release record closure ledger."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "release_record_closure_ledger.md"

REQUIRED_SNIPPETS = (
    "Release Record Closure Ledger",
    "final acceptance memo",
    "final release readiness rollup",
    "evidence freeze confirmation record",
    "PR merge evidence summary",
    "final release evidence table of contents",
    "release evidence retention finalization",
    "archival lock assertion",
    "final acceptance packet index",
    "final release evidence ledger",
    "post-closeout evidence access policy",
    "Record ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Closure Owner",
    "Closure Time UTC",
    "Closure Outcome",
    "Evidence Archive Location",
    "closure ledger must reference release candidate and commit SHA",
    "closure ledger must reference branch and PR number",
    "closure ledger must preserve final acceptance memo references",
    "closure ledger must preserve evidence freeze confirmation record references",
    "closure ledger must preserve release evidence retention finalization references",
    "closure ledger must preserve archival lock assertion references",
    "closure ledger must remain controlled staging/beta evidence",
    "closure ledger must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make release-record-closure-ledger-check",
)


@dataclass(frozen=True)
class ReleaseRecordClosureLedgerResult:
    ok: bool
    detail: str


def run_checks() -> list[ReleaseRecordClosureLedgerResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [ReleaseRecordClosureLedgerResult(DOC.exists(), "ledger present" if DOC.exists() else "ledger missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ReleaseRecordClosureLedgerResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Release record closure ledger check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
