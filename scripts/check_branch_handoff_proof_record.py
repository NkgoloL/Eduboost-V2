#!/usr/bin/env python3
"""Validate branch handoff proof record."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "branch_handoff_proof_record.md"

REQUIRED_SNIPPETS = (
    "Branch Handoff Proof Record",
    "final closure manifest",
    "final acceptance memo",
    "release record closure ledger",
    "PR merge evidence summary",
    "merge-control evidence gate",
    "final merge signoff lock",
    "branch sync and rebase checklist",
    "final PR merge readiness contract",
    "generated artifact hygiene contract",
    "PR-ready final closure certificate",
    "Handoff Proof ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "Remote Branch",
    "PR Number",
    "Handoff Owner",
    "Verified At UTC",
    "Handoff Outcome",
    "branch handoff proof must reference release candidate and commit SHA",
    "branch handoff proof must reference branch and PR number",
    "branch handoff proof must preserve non-force-push branch discipline",
    "branch handoff proof must verify generated artifact conflicts are resolved",
    "branch handoff proof must preserve final PR merge readiness references",
    "branch handoff proof must preserve merge-control evidence gate references",
    "branch handoff proof must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make branch-handoff-proof-record-check",
)


@dataclass(frozen=True)
class BranchHandoffProofRecordResult:
    ok: bool
    detail: str


def run_checks() -> list[BranchHandoffProofRecordResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [BranchHandoffProofRecordResult(DOC.exists(), "record present" if DOC.exists() else "record missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BranchHandoffProofRecordResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Branch handoff proof record check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
