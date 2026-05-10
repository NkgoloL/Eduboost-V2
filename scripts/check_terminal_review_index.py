#!/usr/bin/env python3
"""Validate terminal review index."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "terminal_review_index.md"

REQUIRED_SNIPPETS = (
    "Terminal Review Index",
    "final release operator brief",
    "terminal evidence seal",
    "final PR handoff summary",
    "final reviewer disposition record",
    "reviewer decision capture template",
    "final closure manifest",
    "branch handoff proof record",
    "final acceptance memo",
    "release record closure ledger",
    "final release evidence table of contents",
    "docs/operations/final_release_operator_brief.md",
    "docs/operations/terminal_evidence_seal.md",
    "docs/operations/final_pr_handoff_summary.md",
    "docs/operations/final_reviewer_disposition_record.md",
    "docs/operations/reviewer_decision_capture_template.md",
    "docs/operations/final_closure_manifest.md",
    "docs/operations/branch_handoff_proof_record.md",
    "docs/operations/final_acceptance_memo.md",
    "docs/operations/release_record_closure_ledger.md",
    "docs/operations/final_release_evidence_toc.md",
    "terminal review index must reference release candidate and commit SHA",
    "terminal review index must preserve branch and PR number references",
    "terminal review index must preserve terminal evidence seal references",
    "terminal review index must preserve final release operator brief references",
    "terminal review index must preserve no-op execution boundary references",
    "terminal review index must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make terminal-review-index-check",
)


@dataclass(frozen=True)
class TerminalReviewIndexResult:
    ok: bool
    detail: str


def run_checks() -> list[TerminalReviewIndexResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [TerminalReviewIndexResult(DOC.exists(), "index present" if DOC.exists() else "index missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            TerminalReviewIndexResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Terminal review index check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
