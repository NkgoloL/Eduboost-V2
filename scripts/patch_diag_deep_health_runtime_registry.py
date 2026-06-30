#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.diag_deep_health_runtime_evidence import ACCEPTED_STATUS, write_status  # noqa: E402

REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"

def _replace_or_append(text: str, item_id: str, block: str) -> str:
    if "findings:" not in text:
        text = "findings:\n"
    marker = f"  - id: {item_id}"
    start = text.find(marker)
    if start < 0:
        return text.rstrip() + "\n" + block
    end = text.find("\n  - id:", start + 1)
    return text[:start] + block if end < 0 else text[:start] + block + text[end + 1:]

def _block(item_id: str, title: str, status) -> str:
    accepted = status.status == ACCEPTED_STATUS
    proof_status = "runtime-passing" if accepted else "runtime-blocked"
    closure_blocker = "none" if accepted else "full HTTP plus production DB diagnostic session proof still required"
    release_ready = "true" if accepted else "false"
    blocks_beta = "false" if accepted else "true"
    return f"""  - id: {item_id}
    title: {title}
    severity: P0
    gate: 5
    owner: backend
    implementation_batch: code_2951_2990
    proof_status: {proof_status}
    proof_command: make diag-deep-health-runtime-release-check
    evidence_file: docs/release/diag_deep_health_runtime_status.md
    evidence_url: {status.github_run.run_url if accepted else "null"}
    workflow_name: {status.github_run.workflow_name if accepted else "null"}
    run_id: {status.github_run.run_id if accepted else "null"}
    deep_health_url: {status.deep_health_url if accepted else "null"}
    last_verified_commit: {status.current_commit if accepted else "null"}
    verified_by: {status.verified_by if accepted else "null"}
    date_verified: {status.date_verified if accepted else "null"}
    closure_blocker: {closure_blocker}
    release_ready: {release_ready}
    blocks_beta: {blocks_beta}
    external_dependency: true
"""

def main() -> int:
    status = write_status(run_http=True)
    if status.status != ACCEPTED_STATUS:
        print("DIAG deep-health runtime evidence is not accepted; registry will not be patched as closed")
        for blocker in status.blockers:
            print(f"- {blocker}")
        return 1
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    text = _replace_or_append(text, "DIAG-001", _block("DIAG-001", "Diagnostic deep-health full HTTP and DB runtime proof", status))
    text = _replace_or_append(text, "DIAG-001R", _block("DIAG-001R", "Diagnostic deep-health runtime evidence repair", status))
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated DIAG-001 and DIAG-001R registry entries")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
