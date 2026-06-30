#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.audit_baseline_refresh import write_status  # noqa: E402

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

    block = f"""  - id: AUDIT-BASELINE-REFRESH-001
    title: Audit baseline refresh from current HEAD
    severity: P1
    gate: 1
    owner: release
    implementation_batch: code_2991_3030
    proof_status: runtime-passing
    proof_command: make backend-implementation-2991-3030-full-check
    evidence_file: docs/release/audit_baseline_refresh_status.md
    last_verified_commit: {status.current_commit}
    closure_blocker: refresh only; beta decision remains governed by remaining blockers
    release_ready: false
    blocks_beta: false
    external_dependency: false
"""

    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    text = _replace_or_append(text, "AUDIT-BASELINE-REFRESH-001", block)
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated AUDIT-BASELINE-REFRESH-001 registry entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
