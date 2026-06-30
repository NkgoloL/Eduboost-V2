#!/usr/bin/env python3
"""Validate final beta operator packet index."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_beta_operator_packet_index.md"

REQUIRED_SNIPPETS = (
    "Final Beta Operator Packet Index",
    "Required Execution Documents",
    "Required Approval Documents",
    "Required Recovery Documents",
    "Required Identity Documents",
    "docs/operations/beta_release_execution_plan.md",
    "docs/operations/final_release_verification_bundle.md",
    "docs/operations/post_merge_release_handoff_checklist.md",
    "docs/operations/beta_release_freeze_window_contract.md",
    "docs/operations/release_change_control_exception_log.md",
    "docs/operations/beta_signoff_manifest.md",
    "docs/operations/beta_release_closure_attestation.md",
    "docs/operations/beta_release_decision_log.md",
    "docs/operations/release_owner_accountability_matrix.md",
    "docs/operations/beta_rollback_runbook.md",
    "docs/operations/post_deploy_staging_smoke_checklist.md",
    "docs/operations/release_audit_trail_index.md",
    "docs/operations/release_candidate_tag_manifest.md",
    "docs/operations/release_state_snapshot.md",
    "docs/operations/beta_release_evidence_bundle.md",
    "must not execute deployment, create a release tag, or run post-deploy actions",
    "packet is complete and manual approval is recorded",
    "make final-beta-operator-packet-check",
)


@dataclass(frozen=True)
class FinalBetaOperatorPacketResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalBetaOperatorPacketResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        FinalBetaOperatorPacketResult(DOC.exists(), "operator packet present" if DOC.exists() else "operator packet missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalBetaOperatorPacketResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final beta operator packet check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
