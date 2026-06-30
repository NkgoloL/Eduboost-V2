#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_staging_smoke_workflow_config import write_status  # noqa: E402

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
    status = write_status()
    if status.status != "staging-smoke-workflow-configured":
        print("Staging smoke workflow is not configured; registry not patched")
        for blocker in status.blockers:
            print(f"- {blocker}")
        return 1

    block = f"""  - id: STAGING-SMOKE-WORKFLOW-001
    title: Staging smoke evidence workflow configuration
    severity: P1
    gate: 8
    owner: release
    implementation_batch: code_2911_2950
    proof_status: config-passing
    proof_command: make backend-implementation-2911-2950-workflow-check
    evidence_file: docs/release/staging_smoke_workflow_status.md
    last_verified_commit: {status.current_commit}
    closure_blocker: workflow only; STAGING-001 remains external-blocked until real staging evidence is attached
    release_ready: false
    blocks_beta: false
    external_dependency: false
"""

    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    text = _replace_or_append(text, "STAGING-SMOKE-WORKFLOW-001", block)
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated STAGING-SMOKE-WORKFLOW-001 registry entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
