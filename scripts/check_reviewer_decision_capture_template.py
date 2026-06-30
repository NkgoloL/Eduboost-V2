#!/usr/bin/env python3
"""Validate reviewer decision capture template."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "reviewer_decision_capture_template.md"

REQUIRED_SNIPPETS = (
    "Reviewer Decision Capture Template",
    "final closure manifest",
    "branch handoff proof record",
    "final acceptance memo",
    "release record closure ledger",
    "PR merge evidence summary",
    "final reviewer pack checklist",
    "merge-control evidence gate",
    "PR-ready final closure certificate",
    "final release evidence table of contents",
    "final evidence no-op execution assertion",
    "Reviewer Decision ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Reviewer",
    "Decision Time UTC",
    "approve merge / request changes / defer / reject",
    "Follow-Up Owner",
    "reviewer decision must reference release candidate and commit SHA",
    "reviewer decision must reference branch and PR number",
    "approve merge decision requires merge-control evidence gate review",
    "request changes decision must identify evidence gap and owner",
    "defer decision must identify reason and target milestone",
    "reject decision must identify blocking evidence failure",
    "reviewer decision must preserve no-op execution boundary",
    "reviewer decision must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make reviewer-decision-capture-template-check",
)


@dataclass(frozen=True)
class ReviewerDecisionCaptureTemplateResult:
    ok: bool
    detail: str


def run_checks() -> list[ReviewerDecisionCaptureTemplateResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [ReviewerDecisionCaptureTemplateResult(DOC.exists(), "template present" if DOC.exists() else "template missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ReviewerDecisionCaptureTemplateResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Reviewer decision capture template check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
