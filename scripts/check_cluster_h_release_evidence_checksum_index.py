#!/usr/bin/env python3
"""Validate Cluster H release evidence checksum index."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "cluster_h_release_evidence_checksum_index.md"

REQUIRED_SNIPPETS = (
    "Cluster H Release Evidence Checksum Index",
    "docs/operations/cluster_h_terminal_closure_assertion.md",
    "docs/operations/beta_release_final_index.md",
    "docs/operations/beta_governance_seal_checklist.md",
    "docs/operations/final_release_handoff_package.md",
    "docs/operations/evidence_archive_completeness_guard.md",
    "docs/operations/post_terminal_audit_readiness_assertion.md",
    "docs/operations/final_project_closeout_attestation.md",
    "docs/operations/post_beta_evidence_archive_manifest.md",
    "docs/operations/beta_outcome_report_template.md",
    "docs/operations/beta_retrospective_action_register.md",
    "docs/operations/release_owner_execution_guardrail.md",
    "docs/operations/release_audit_trail_index.md",
    "Evidence Path",
    "Release Candidate",
    "Commit SHA",
    "Hash Algorithm",
    "sha256",
    "Hash Value",
    "Recorded By",
    "Recorded At UTC",
    "checksum index must reference release candidate and commit SHA",
    "checksum index must use sha256 as the canonical hash algorithm",
    "checksum index must preserve terminal closure evidence references",
    "checksum index must preserve handoff and archive evidence references",
    "checksum index must not include unnecessary learner personal information",
    "checksum index must remain audit evidence only",
    "does not compute hashes automatically, approve production launch, execute deployment, or create release tags",
    "make cluster-h-release-evidence-checksum-index-check",
)


@dataclass(frozen=True)
class ClusterHReleaseEvidenceChecksumIndexResult:
    ok: bool
    detail: str


def run_checks() -> list[ClusterHReleaseEvidenceChecksumIndexResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [ClusterHReleaseEvidenceChecksumIndexResult(DOC.exists(), "index present" if DOC.exists() else "index missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ClusterHReleaseEvidenceChecksumIndexResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Cluster H release evidence checksum index check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
