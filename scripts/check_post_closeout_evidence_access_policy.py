#!/usr/bin/env python3
"""Validate post-closeout evidence access policy."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "post_closeout_evidence_access_policy.md"

REQUIRED_SNIPPETS = (
    "Post-Closeout Evidence Access Policy",
    "access is limited to release, audit, compliance, and maintenance purposes",
    "evidence references must preserve release candidate and commit SHA",
    "evidence access must avoid unnecessary learner personal information",
    "evidence sharing must preserve controlled staging/beta scope",
    "post-freeze changes must reference frozen scope variance register",
    "maintenance edits must reference post-closeout maintenance boundary",
    "evidence access must preserve no-op execution boundary",
    "evidence access must not imply production launch authorization",
    "docs/operations/final_acceptance_packet_index.md",
    "docs/operations/release_handoff_freeze_assertion.md",
    "docs/operations/final_release_evidence_ledger.md",
    "docs/operations/frozen_scope_variance_register.md",
    "docs/operations/post_closeout_maintenance_boundary.md",
    "docs/operations/final_evidence_noop_execution_assertion.md",
    "docs/operations/cluster_h_release_evidence_checksum_index.md",
    "use evidence access as deployment approval",
    "use evidence access to create release tags",
    "use evidence access to bypass manual approval",
    "use evidence access to collect live learner data",
    "use evidence access to alter release-owner decision",
    "use evidence access to delete audit evidence",
    "use evidence access to rewrite source control history",
    "does not approve production launch, execute deployment, create release tags, or bypass manual approval",
    "make post-closeout-evidence-access-policy-check",
)


@dataclass(frozen=True)
class PostCloseoutEvidenceAccessPolicyResult:
    ok: bool
    detail: str


def run_checks() -> list[PostCloseoutEvidenceAccessPolicyResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [PostCloseoutEvidenceAccessPolicyResult(DOC.exists(), "policy present" if DOC.exists() else "policy missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            PostCloseoutEvidenceAccessPolicyResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Post-closeout evidence access policy check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
