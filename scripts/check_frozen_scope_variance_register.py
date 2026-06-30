#!/usr/bin/env python3
"""Validate frozen scope variance register."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "frozen_scope_variance_register.md"

REQUIRED_SNIPPETS = (
    "Frozen Scope Variance Register",
    "Variance ID",
    "Release Candidate",
    "Commit SHA",
    "Source Document",
    "typo / link / evidence-reference / owner-update / blocker",
    "Requested By",
    "Reviewed By",
    "accepted / rejected / deferred",
    "Recorded At UTC",
    "variance must reference release candidate and commit SHA",
    "variance must identify source document and evidence reference",
    "typo variance may be accepted without reopening Cluster H scope",
    "link variance may be accepted when target evidence already exists",
    "evidence-reference variance must preserve audit traceability",
    "owner-update variance must preserve release-owner accountability",
    "blocker variance must stop merge signoff until resolved",
    "accepted variance must be listed in final release evidence ledger",
    "docs/operations/final_release_evidence_ledger.md",
    "docs/operations/final_merge_signoff_lock.md",
    "docs/operations/final_project_closeout_attestation.md",
    "docs/operations/release_owner_post_closeout_decision_record.md",
    "docs/operations/final_evidence_noop_execution_assertion.md",
    "does not approve production launch, execute deployment, create release tags, or reopen closed release scope automatically",
    "make frozen-scope-variance-register-check",
)


@dataclass(frozen=True)
class FrozenScopeVarianceRegisterResult:
    ok: bool
    detail: str


def run_checks() -> list[FrozenScopeVarianceRegisterResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FrozenScopeVarianceRegisterResult(DOC.exists(), "register present" if DOC.exists() else "register missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FrozenScopeVarianceRegisterResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Frozen scope variance register check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
