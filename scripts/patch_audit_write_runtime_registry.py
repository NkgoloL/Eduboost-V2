#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.audit_write_runtime_evidence import ACCEPTED_STATUS, write_status  # noqa: E402

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
    run_flow = os.getenv("AUDIT_WRITE_RUN_FLOW") == "1" or os.getenv("AUDIT_WRITE_ACCEPT") == "1"
    status = write_status(run_flow=run_flow)
    accepted = status.status == ACCEPTED_STATUS
    proof_status = "runtime-passing" if accepted else "not-proven"
    closure_blocker = "none" if accepted else "real audit_events write proof required"
    release_ready = "true" if accepted else "false"
    blocks_beta = "false" if accepted else "true"

    block = f"""  - id: AUDIT-WRITE-001
    title: Runtime audit_events write proof
    severity: P0
    gate: 6
    owner: backend
    implementation_batch: code_3271_3310
    proof_status: {proof_status}
    proof_command: make audit-write-runtime-release-check
    evidence_file: docs/release/audit_write_runtime_evidence_status.md
    evidence_url: {status.github_run.run_url if accepted else "null"}
    workflow_name: {status.github_run.workflow_name if accepted else "null"}
    run_id: {status.github_run.run_id if accepted else "null"}
    audit_events_count_before: {status.audit_events_count_before}
    audit_events_count_after: {status.audit_events_count_after}
    audit_events_delta: {status.audit_events_delta}
    audit_trace_id: {status.audit_trace_id}
    last_verified_commit: {status.current_commit if accepted else "null"}
    verified_by: {status.verified_by if accepted else "null"}
    date_verified: {status.date_verified if accepted else "null"}
    closure_blocker: {closure_blocker}
    release_ready: {release_ready}
    blocks_beta: {blocks_beta}
    external_dependency: true
"""
    repair = f"""  - id: AUDIT-WRITE-001R
    title: Runtime audit_events write evidence repair
    severity: P0
    gate: 6
    owner: backend
    implementation_batch: code_3271_3310
    proof_status: {proof_status}
    proof_command: make audit-write-runtime-release-check
    evidence_file: docs/release/audit_write_runtime_evidence_status.md
    evidence_url: {status.github_run.run_url if accepted else "null"}
    run_id: {status.github_run.run_id if accepted else "null"}
    audit_events_delta: {status.audit_events_delta}
    last_verified_commit: {status.current_commit if accepted else "null"}
    closure_blocker: {closure_blocker}
    release_ready: {release_ready}
    blocks_beta: {blocks_beta}
    external_dependency: true
"""
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    text = _replace_or_append(text, "AUDIT-WRITE-001", block)
    text = _replace_or_append(text, "AUDIT-WRITE-001R", repair)
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated AUDIT-WRITE-001 and AUDIT-WRITE-001R registry entries")

    if os.getenv("AUDIT_WRITE_ACCEPT") == "1" and not accepted:
        print("Audit write runtime evidence is not accepted; blockers:")
        for blocker in status.blockers:
            print(f"- {blocker}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
