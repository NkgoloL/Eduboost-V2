#!/usr/bin/env python3
"""Validate beta release final index."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_release_final_index.md"

REQUIRED_SNIPPETS = (
    "Beta Release Final Index",
    "Core Release Evidence",
    "Governance Evidence",
    "Operational Evidence",
    "Outcome Evidence",
    "Closure Evidence",
    "docs/operations/beta_release_readiness_contract.md",
    "docs/operations/final_release_verification_bundle.md",
    "docs/operations/beta_governance_seal_checklist.md",
    "docs/operations/final_beta_operator_packet_index.md",
    "docs/operations/beta_release_freeze_window_contract.md",
    "docs/operations/beta_feedback_intake_contract.md",
    "docs/operations/beta_known_issues_register.md",
    "docs/operations/beta_acceptance_exit_criteria.md",
    "docs/operations/beta_outcome_report_template.md",
    "docs/operations/post_beta_evidence_archive_manifest.md",
    "docs/operations/final_cluster_h_closeout_rollup.md",
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "docs/operations/cluster_h_terminal_closure_assertion.md",
    "docs/operations/release_audit_trail_index.md",
    "final index must reference release candidate and commit SHA",
    "final index must preserve governance, operational, outcome, and closure evidence",
    "final index must remain controlled staging/beta evidence",
    "final index must not be treated as unrestricted production authorization",
    "does not approve production launch, execute deployment, create release tags, or replace workflow logs",
    "make beta-release-final-index-check",
)


@dataclass(frozen=True)
class BetaReleaseFinalIndexResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaReleaseFinalIndexResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [BetaReleaseFinalIndexResult(DOC.exists(), "index present" if DOC.exists() else "index missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(BetaReleaseFinalIndexResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))
    return results


def main() -> int:
    results = run_checks()
    print("Beta release final index check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
