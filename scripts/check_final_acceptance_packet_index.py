#!/usr/bin/env python3
"""Validate final acceptance packet index."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_acceptance_packet_index.md"

REQUIRED_SNIPPETS = (
    "Final Acceptance Packet Index",
    "release identity evidence",
    "readiness evidence",
    "governance evidence",
    "terminal closure evidence",
    "post-terminal audit evidence",
    "handoff evidence",
    "release-owner decision evidence",
    "merge signoff evidence",
    "no-op execution evidence",
    "ledger and variance evidence",
    "maintenance boundary evidence",
    "checksum evidence",
    "docs/operations/release_state_snapshot.md",
    "docs/operations/cluster_h_terminal_closure_assertion.md",
    "docs/operations/final_release_evidence_ledger.md",
    "docs/operations/frozen_scope_variance_register.md",
    "docs/operations/post_closeout_maintenance_boundary.md",
    "docs/operations/final_merge_signoff_lock.md",
    "docs/operations/release_owner_post_closeout_decision_record.md",
    "docs/operations/final_evidence_noop_execution_assertion.md",
    "docs/operations/final_project_closeout_attestation.md",
    "docs/operations/cluster_h_release_evidence_checksum_index.md",
    "acceptance packet must reference release candidate and commit SHA",
    "acceptance packet must preserve controlled staging/beta scope",
    "acceptance packet must preserve release-owner decision evidence",
    "acceptance packet must preserve no-op execution evidence",
    "acceptance packet must preserve frozen scope variance evidence",
    "acceptance packet must preserve maintenance boundary evidence",
    "acceptance packet must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or replace manual approval",
    "make final-acceptance-packet-index-check",
)


@dataclass(frozen=True)
class FinalAcceptancePacketIndexResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalAcceptancePacketIndexResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalAcceptancePacketIndexResult(DOC.exists(), "index present" if DOC.exists() else "index missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalAcceptancePacketIndexResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final acceptance packet index check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
