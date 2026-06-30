#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.diagnostic_item_bank_canonicality import write_status  # noqa: E402

REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def _replace_or_append(text: str, item_id: str, block: str) -> str:
    if "findings:" not in text:
        text = "findings:\n"

    marker = f"  - id: {item_id}"
    start = text.find(marker)
    if start < 0:
        return text.rstrip() + "\n" + block

    end = text.find("\n  - id:", start + 1)
    if end < 0:
        return text[:start] + block

    return text[:start] + block + text[end + 1 :]


def _diag_score_guard_block(status) -> str:
    return f"""  - id: DIAG-SCORE-001
    title: Diagnostic scoring live DB and item-bank audit
    severity: P0
    gate: 5
    owner: backend
    implementation_batch: pending
    proof_status: not-proven
    proof_command: pending DIAG-SCORE-001R live scoring audit
    evidence_file: docs/release/diagnostic_item_bank_canonicality_status.md
    canonical_table: {status.canonical_table}
    supporting_table: {status.supporting_table}
    last_verified_commit: null
    closure_blocker: diagnostic_items is runtime-required and must be seeded or runtime references removed before scoring audit can close
    release_ready: false
    blocks_beta: true
    external_dependency: true
"""


def main() -> int:
    status = write_status()
    accepted = status.status == "diagnostic-item-bank-policy-accepted"

    proof_status = "policy-accepted" if accepted else "not-proven"
    closure_blocker = "none" if accepted else "diagnostic item-bank policy incomplete"
    release_ready = "true" if accepted else "false"

    block = f"""  - id: DIAG-ITEMS-001R
    title: Diagnostic item-bank runtime-required policy
    severity: P1
    gate: 5
    owner: backend
    implementation_batch: code_3151_3190
    proof_status: {proof_status}
    proof_command: make backend-implementation-3151-3190-full-check
    evidence_file: docs/release/diagnostic_item_bank_canonicality_status.md
    policy_file: docs/architecture/diagnostic_item_bank_canonicality.yml
    decision: {status.decision}
    canonical_table: {status.canonical_table}
    supporting_table: {status.supporting_table}
    unresolved_blocker: {status.unresolved_blocker}
    last_verified_commit: {status.current_commit if accepted else "null"}
    closure_blocker: {closure_blocker}
    release_ready: {release_ready}
    blocks_beta: false
    external_dependency: false
"""

    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    text = _replace_or_append(text, "DIAG-ITEMS-001R", block)
    text = _replace_or_append(text, "DIAG-SCORE-001", _diag_score_guard_block(status))
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated DIAG-ITEMS-001R and preserved DIAG-SCORE-001 blocker")

    if not accepted:
        print("Diagnostic item-bank policy is not accepted; blockers:")
        for blocker in status.blockers:
            print(f"- {blocker}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
