#!/usr/bin/env python3
"""Validate final Cluster H closeout rollup."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_cluster_h_closeout_rollup.md"

REQUIRED_FILES = (
    "docs/operations/final_cluster_h_closeout_rollup.md",
    "docs/operations/release_audit_trail_index.md",
    "docs/operations/beta_release_closure_attestation.md",
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "docs/operations/project_release_closure_index.md",
    "docs/operations/final_pr_merge_readiness_contract.md",
    "docs/operations/beta_release_decision_log.md",
    "docs/operations/release_owner_accountability_matrix.md",
    "docs/operations/post_merge_release_handoff_checklist.md",
    "docs/operations/final_release_verification_bundle.md",
    "docs/operations/release_state_snapshot.md",
)

REQUIRED_SNIPPETS = (
    "Final Cluster H Closeout Rollup",
    "release readiness baseline evidence",
    "operational release controls",
    "bundle approval and closure evidence",
    "final project closure evidence",
    "release hygiene and PR closeout evidence",
    "execution PR verification evidence",
    "state consistency merge readiness evidence",
    "post-merge governance handoff evidence",
    "release audit trail evidence",
    "beta release closure attestation evidence",
    "make release-audit-trail-index-check",
    "make beta-release-closure-attestation-check",
    "make cluster-h-final-closeout-rollup-check",
    "does not perform deployment, manual approval, tag creation, production migration, or post-deploy browser execution",
)


@dataclass(frozen=True)
class ClusterHFinalCloseoutRollupResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ClusterHFinalCloseoutRollupResult]:
    results: list[ClusterHFinalCloseoutRollupResult] = []
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            ClusterHFinalCloseoutRollupResult(
                "file",
                rel_path,
                path.exists(),
                "present" if path.exists() else "missing",
            )
        )

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ClusterHFinalCloseoutRollupResult(
                "content",
                str(DOC.relative_to(REPO_ROOT)),
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Cluster H final closeout rollup check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
