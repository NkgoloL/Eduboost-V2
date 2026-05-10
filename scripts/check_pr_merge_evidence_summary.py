#!/usr/bin/env python3
"""Validate PR merge evidence summary."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "pr_merge_evidence_summary.md"

REQUIRED_SNIPPETS = (
    "PR Merge Evidence Summary",
    "final release readiness rollup",
    "evidence freeze confirmation record",
    "final reviewer pack checklist",
    "merge-control evidence gate",
    "PR-ready final closure certificate",
    "final release evidence table of contents",
    "final acceptance packet index",
    "final evidence no-op execution assertion",
    "release evidence retention finalization",
    "post-closeout evidence access policy",
    "Summary ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Merge Evidence Outcome",
    "Reviewer",
    "Reviewed At UTC",
    "Follow-Up Owner",
    "summary must reference release candidate and commit SHA",
    "summary must reference branch and PR number",
    "summary must preserve merge-control evidence gate references",
    "summary must preserve PR-ready final closure certificate references",
    "summary must preserve final evidence no-op execution assertion",
    "summary must preserve evidence freeze confirmation record",
    "summary must preserve controlled staging/beta scope",
    "summary must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make pr-merge-evidence-summary-check",
)


@dataclass(frozen=True)
class PrMergeEvidenceSummaryResult:
    ok: bool
    detail: str


def run_checks() -> list[PrMergeEvidenceSummaryResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [PrMergeEvidenceSummaryResult(DOC.exists(), "summary present" if DOC.exists() else "summary missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            PrMergeEvidenceSummaryResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("PR merge evidence summary check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
