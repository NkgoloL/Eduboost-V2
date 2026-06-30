#!/usr/bin/env python3
"""Validate final reviewer pack checklist."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_reviewer_pack_checklist.md"

REQUIRED_SNIPPETS = (
    "Final Reviewer Pack Checklist",
    "final release evidence table of contents",
    "final acceptance packet index",
    "PR-ready final closure certificate",
    "archival lock assertion",
    "release handoff freeze assertion",
    "post-closeout evidence access policy",
    "final release evidence ledger",
    "final evidence no-op execution assertion",
    "final merge signoff lock",
    "release owner post-closeout decision record",
    "reviewer verifies release candidate and commit SHA consistency",
    "reviewer verifies controlled staging/beta scope is preserved",
    "reviewer verifies no unrestricted production launch authorization exists",
    "reviewer verifies no-op execution boundary is present",
    "reviewer verifies manual approval workflow references are preserved",
    "reviewer verifies branch and PR references are present",
    "reviewer verifies frozen scope variance register is present",
    "reviewer verifies post-closeout maintenance boundary is present",
    "reviewer verifies evidence access policy is present",
    "reviewer verifies archival lock assertion is present",
    "ready for merge review",
    "request evidence correction",
    "defer merge review",
    "reject merge review",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make final-reviewer-pack-checklist-check",
)


@dataclass(frozen=True)
class FinalReviewerPackChecklistResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalReviewerPackChecklistResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalReviewerPackChecklistResult(DOC.exists(), "checklist present" if DOC.exists() else "checklist missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalReviewerPackChecklistResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final reviewer pack checklist check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
