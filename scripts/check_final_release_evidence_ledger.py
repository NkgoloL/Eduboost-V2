#!/usr/bin/env python3
"""Validate final release evidence ledger."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_release_evidence_ledger.md"

REQUIRED_SNIPPETS = (
    "Final Release Evidence Ledger",
    "release identity",
    "release readiness",
    "release governance",
    "terminal closure",
    "post-terminal audit readiness",
    "release-owner handoff",
    "release-owner decision",
    "merge signoff",
    "no-op execution boundary",
    "archive completeness",
    "checksum index",
    "final project closeout",
    "docs/operations/release_state_snapshot.md",
    "docs/operations/cluster_h_terminal_closure_assertion.md",
    "docs/operations/beta_release_final_index.md",
    "docs/operations/beta_governance_seal_checklist.md",
    "docs/operations/final_release_handoff_package.md",
    "docs/operations/release_owner_post_closeout_decision_record.md",
    "docs/operations/final_merge_signoff_lock.md",
    "docs/operations/final_evidence_noop_execution_assertion.md",
    "docs/operations/evidence_archive_completeness_guard.md",
    "docs/operations/cluster_h_release_evidence_checksum_index.md",
    "docs/operations/final_project_closeout_attestation.md",
    "docs/operations/post_terminal_audit_readiness_assertion.md",
    "ledger must reference release candidate and commit SHA",
    "ledger must preserve controlled staging/beta scope",
    "ledger must preserve release-owner decision references",
    "ledger must preserve manual approval workflow references",
    "ledger must preserve no-op execution boundary references",
    "ledger must preserve archive and checksum references",
    "ledger must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or replace manual approval",
    "make final-release-evidence-ledger-check",
)


@dataclass(frozen=True)
class FinalReleaseEvidenceLedgerResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalReleaseEvidenceLedgerResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalReleaseEvidenceLedgerResult(DOC.exists(), "ledger present" if DOC.exists() else "ledger missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalReleaseEvidenceLedgerResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final release evidence ledger check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
