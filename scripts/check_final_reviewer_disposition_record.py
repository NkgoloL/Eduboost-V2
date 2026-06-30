#!/usr/bin/env python3
"""Validate final reviewer disposition record."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_reviewer_disposition_record.md"

REQUIRED_SNIPPETS = (
    "Final Reviewer Disposition Record",
    "reviewer decision capture template",
    "final closure manifest",
    "branch handoff proof record",
    "final acceptance memo",
    "release record closure ledger",
    "PR merge evidence summary",
    "merge-control evidence gate",
    "final reviewer pack checklist",
    "PR-ready final closure certificate",
    "final release evidence table of contents",
    "Disposition ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Reviewer",
    "Disposition Time UTC",
    "approve merge / request changes / defer / reject",
    "Evidence Gap",
    "Follow-Up Owner",
    "disposition must reference release candidate and commit SHA",
    "disposition must reference branch and PR number",
    "disposition must preserve reviewer decision capture template references",
    "disposition must preserve merge-control evidence gate references",
    "disposition must preserve branch handoff proof references",
    "disposition must preserve no-op execution boundary references",
    "disposition must preserve controlled staging/beta scope",
    "disposition must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make final-reviewer-disposition-record-check",
)


@dataclass(frozen=True)
class FinalReviewerDispositionRecordResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalReviewerDispositionRecordResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalReviewerDispositionRecordResult(DOC.exists(), "record present" if DOC.exists() else "record missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalReviewerDispositionRecordResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final reviewer disposition record check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
