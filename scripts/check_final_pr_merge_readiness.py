#!/usr/bin/env python3
"""Validate final PR merge readiness contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_pr_merge_readiness_contract.md"

REQUIRED_SNIPPETS = (
    "Final PR Merge Readiness Contract",
    "generated artifact hygiene check passes",
    "branch sync and rebase checklist passes",
    "beta evidence consistency check passes",
    "release state snapshot check passes",
    "final release verification check passes",
    "Cluster H release readiness check passes",
    "Cluster H closure check passes",
    "PR body contains verification, release boundary, rollback, evidence index, and known follow-ups",
    "no unresolved merge conflicts remain",
    "no generated `coverage.xml` conflict remains",
    "remote branch accepts non-force push",
    "docs/operations/release_state_snapshot.md",
    "docs/operations/beta_evidence_consistency_guard.md",
    "docs/operations/final_release_verification_bundle.md",
    "docs/operations/beta_release_pr_body.md",
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "does not itself execute deployment, approval, tagging, or production launch",
    "make final-pr-merge-readiness-check",
)


@dataclass(frozen=True)
class FinalPRMergeReadinessResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalPRMergeReadinessResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        FinalPRMergeReadinessResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalPRMergeReadinessResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Final PR merge readiness check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
