#!/usr/bin/env python3
"""Validate evidence freeze confirmation record."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "evidence_freeze_confirmation_record.md"

REQUIRED_SNIPPETS = (
    "Evidence Freeze Confirmation Record",
    "release handoff freeze assertion",
    "archival lock assertion",
    "final release readiness rollup",
    "final release evidence table of contents",
    "release evidence retention finalization",
    "merge-control evidence gate",
    "final reviewer pack checklist",
    "final acceptance packet index",
    "final release evidence ledger",
    "post-closeout evidence access policy",
    "Confirmation ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Confirmed By",
    "Confirmed At UTC",
    "Freeze Outcome",
    "Evidence Archive Location",
    "confirmation must reference release candidate and commit SHA",
    "confirmation must reference branch and PR number",
    "confirmation must preserve release handoff freeze assertion",
    "confirmation must preserve archival lock assertion",
    "confirmation must preserve final release readiness rollup",
    "confirmation must preserve post-closeout evidence access policy",
    "confirmation must route post-freeze changes through frozen scope variance register",
    "confirmation must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make evidence-freeze-confirmation-record-check",
)


@dataclass(frozen=True)
class EvidenceFreezeConfirmationRecordResult:
    ok: bool
    detail: str


def run_checks() -> list[EvidenceFreezeConfirmationRecordResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [EvidenceFreezeConfirmationRecordResult(DOC.exists(), "record present" if DOC.exists() else "record missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            EvidenceFreezeConfirmationRecordResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Evidence freeze confirmation record check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
