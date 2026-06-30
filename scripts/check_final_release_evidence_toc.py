#!/usr/bin/env python3
"""Validate final release evidence table of contents."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_release_evidence_toc.md"

REQUIRED_SNIPPETS = (
    "Final Release Evidence Table of Contents",
    "docs/operations/final_acceptance_packet_index.md",
    "docs/operations/pr_ready_final_closure_certificate.md",
    "docs/operations/archival_lock_assertion.md",
    "docs/operations/release_handoff_freeze_assertion.md",
    "docs/operations/final_release_evidence_ledger.md",
    "docs/operations/frozen_scope_variance_register.md",
    "docs/operations/post_closeout_maintenance_boundary.md",
    "docs/operations/post_closeout_evidence_access_policy.md",
    "docs/operations/final_evidence_noop_execution_assertion.md",
    "docs/operations/cluster_h_release_evidence_checksum_index.md",
    "docs/operations/final_project_closeout_attestation.md",
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "reviewer must verify release candidate and commit SHA consistency",
    "reviewer must verify final acceptance packet references",
    "reviewer must verify PR-ready final closure certificate references",
    "reviewer must verify archival lock references",
    "reviewer must verify no-op execution boundary",
    "reviewer must verify post-closeout evidence access policy",
    "reviewer must verify controlled staging/beta scope",
    "reviewer must verify no unrestricted production launch authorization",
    "does not approve production launch, execute deployment, create release tags, or replace manual approval",
    "make final-release-evidence-toc-check",
)


@dataclass(frozen=True)
class FinalReleaseEvidenceTocResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalReleaseEvidenceTocResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalReleaseEvidenceTocResult(DOC.exists(), "toc present" if DOC.exists() else "toc missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalReleaseEvidenceTocResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final release evidence table of contents check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
