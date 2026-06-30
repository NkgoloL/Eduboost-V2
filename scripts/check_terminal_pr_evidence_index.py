#!/usr/bin/env python3
"""Validate terminal PR evidence index."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "terminal_pr_evidence_index.md"

REQUIRED_SNIPPETS = (
    "Terminal PR Evidence Index",
    "sealed reviewer closeout packet",
    "final audit handoff register",
    "final release operator brief",
    "terminal review index",
    "sealed evidence access handoff",
    "terminal evidence seal",
    "final PR handoff summary",
    "final reviewer disposition record",
    "final closure manifest",
    "branch handoff proof record",
    "docs/operations/sealed_reviewer_closeout_packet.md",
    "docs/operations/final_audit_handoff_register.md",
    "docs/operations/final_release_operator_brief.md",
    "docs/operations/terminal_review_index.md",
    "docs/operations/sealed_evidence_access_handoff.md",
    "docs/operations/terminal_evidence_seal.md",
    "docs/operations/final_pr_handoff_summary.md",
    "docs/operations/final_reviewer_disposition_record.md",
    "docs/operations/final_closure_manifest.md",
    "docs/operations/branch_handoff_proof_record.md",
    "terminal PR index must reference release candidate and commit SHA",
    "terminal PR index must reference branch and PR number",
    "terminal PR index must preserve sealed reviewer closeout packet references",
    "terminal PR index must preserve final audit handoff register references",
    "terminal PR index must preserve terminal evidence seal references",
    "terminal PR index must preserve no-op execution boundary references",
    "terminal PR index must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make terminal-pr-evidence-index-check",
)


@dataclass(frozen=True)
class TerminalPrEvidenceIndexResult:
    ok: bool
    detail: str


def run_checks() -> list[TerminalPrEvidenceIndexResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [TerminalPrEvidenceIndexResult(DOC.exists(), "index present" if DOC.exists() else "index missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            TerminalPrEvidenceIndexResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Terminal PR evidence index check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
