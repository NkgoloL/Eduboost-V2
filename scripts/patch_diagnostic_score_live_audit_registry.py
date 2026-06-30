#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.diagnostic_score_live_audit import ACCEPTED_STATUS, write_status  # noqa: E402

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


def main() -> int:
    apply_seed = os.getenv("DIAG_SCORE_APPLY_SEED") == "1" or os.getenv("DIAG_SCORE_ALLOW_BRIDGE_SEED") == "1"
    status = write_status(apply_seed=apply_seed)
    accepted = status.status == ACCEPTED_STATUS

    proof_status = "runtime-passing" if accepted else "not-proven"
    closure_blocker = "none" if accepted else "live diagnostic scoring seed/audit proof required"
    release_ready = "true" if accepted else "false"
    blocks_beta = "false" if accepted else "true"

    block = f"""  - id: DIAG-SCORE-001
    title: Diagnostic scoring live DB and item-bank audit
    severity: P0
    gate: 5
    owner: backend
    implementation_batch: code_3191_3230
    proof_status: {proof_status}
    proof_command: make diagnostic-score-live-audit-release-check
    evidence_file: docs/release/diagnostic_score_live_audit_status.md
    evidence_url: {status.github_run.run_url if accepted else "null"}
    workflow_name: {status.github_run.workflow_name if accepted else "null"}
    run_id: {status.github_run.run_id if accepted else "null"}
    diagnostic_items_count: {status.diagnostic_items_count}
    irt_items_count: {status.irt_items_count}
    seed_inserted_rows: {status.seed_inserted_rows}
    last_verified_commit: {status.current_commit if accepted else "null"}
    verified_by: {status.verified_by if accepted else "null"}
    date_verified: {status.date_verified if accepted else "null"}
    closure_blocker: {closure_blocker}
    release_ready: {release_ready}
    blocks_beta: {blocks_beta}
    external_dependency: true
"""

    repair = f"""  - id: DIAG-SCORE-001R
    title: Diagnostic scoring live audit repair
    severity: P0
    gate: 5
    owner: backend
    implementation_batch: code_3191_3230
    proof_status: {proof_status}
    proof_command: make diagnostic-score-live-audit-release-check
    evidence_file: docs/release/diagnostic_score_live_audit_status.md
    evidence_url: {status.github_run.run_url if accepted else "null"}
    run_id: {status.github_run.run_id if accepted else "null"}
    diagnostic_items_count: {status.diagnostic_items_count}
    irt_items_count: {status.irt_items_count}
    last_verified_commit: {status.current_commit if accepted else "null"}
    closure_blocker: {closure_blocker}
    release_ready: {release_ready}
    blocks_beta: {blocks_beta}
    external_dependency: true
"""

    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    text = _replace_or_append(text, "DIAG-SCORE-001", block)
    text = _replace_or_append(text, "DIAG-SCORE-001R", repair)
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated DIAG-SCORE-001 and DIAG-SCORE-001R registry entries")

    if not accepted:
        print("Diagnostic score live audit is not accepted; blockers:")
        for blocker in status.blockers:
            print(f"- {blocker}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
