#!/usr/bin/env python3
"""Validate final PR handoff summary."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_pr_handoff_summary.md"

REQUIRED_SNIPPETS = (
    "Final PR Handoff Summary",
    "terminal evidence seal",
    "final reviewer disposition record",
    "final closure manifest",
    "branch handoff proof record",
    "final acceptance memo",
    "release record closure ledger",
    "post-merge evidence continuity note",
    "PR merge evidence summary",
    "final release evidence table of contents",
    "merge-control evidence gate",
    "Summary ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Handoff Owner",
    "Receiving Owner",
    "Summary Time UTC",
    "Handoff Outcome",
    "summary must reference release candidate and commit SHA",
    "summary must reference branch and PR number",
    "summary must preserve terminal evidence seal references",
    "summary must preserve final reviewer disposition record references",
    "summary must preserve branch handoff proof references",
    "summary must preserve merge-control evidence gate references",
    "summary must preserve no-op execution boundary references",
    "summary must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make final-pr-handoff-summary-check",
)


@dataclass(frozen=True)
class FinalPrHandoffSummaryResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalPrHandoffSummaryResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalPrHandoffSummaryResult(DOC.exists(), "summary present" if DOC.exists() else "summary missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalPrHandoffSummaryResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final PR handoff summary check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
