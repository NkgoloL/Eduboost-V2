#!/usr/bin/env python3
"""Validate release audit trail index."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "release_audit_trail_index.md"

REQUIRED_SNIPPETS = (
    "Release Audit Trail Index",
    "Source and Branch State",
    "Release Evidence",
    "Governance Evidence",
    "Technical Closure Evidence",
    "Operational Evidence",
    "docs/operations/release_state_snapshot.md",
    "docs/operations/final_pr_merge_readiness_contract.md",
    "docs/operations/beta_release_evidence_bundle.md",
    "docs/operations/final_release_verification_bundle.md",
    "docs/operations/post_merge_release_handoff_checklist.md",
    "docs/operations/release_owner_accountability_matrix.md",
    "docs/operations/beta_release_decision_log.md",
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "docs/security/POPIA_CONSENT_GATE_CLOSURE.md",
    "docs/operations/beta_rollback_runbook.md",
    "docs/operations/release_candidate_tag_manifest.md",
    "does not replace workflow logs, approval records, deployment platform evidence, or incident records",
    "make release-audit-trail-index-check",
)


@dataclass(frozen=True)
class ReleaseAuditTrailIndexResult:
    ok: bool
    detail: str


def run_checks() -> list[ReleaseAuditTrailIndexResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        ReleaseAuditTrailIndexResult(DOC.exists(), "index present" if DOC.exists() else "index missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ReleaseAuditTrailIndexResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Release audit trail index check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
