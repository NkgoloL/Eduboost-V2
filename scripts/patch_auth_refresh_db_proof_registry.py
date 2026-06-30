#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.auth_refresh_db_proof import write_status  # noqa: E402

REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def current_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def replace_or_append(text: str, item_id: str, block: str) -> str:
    if "findings:" not in text:
        text = "findings:\n"
    marker = f"  - id: {item_id}"
    index = text.find(marker)
    if index < 0:
        return text.rstrip() + "\n" + block
    next_index = text.find("\n  - id:", index + 1)
    return text[:index] + block if next_index < 0 else text[:index] + block + text[next_index + 1:]


def main() -> int:
    status = write_status(run_pytest=False)
    proof = "integration-passing" if status.status == "auth-refresh-db-proof-accepted" else "external-blocked"
    blocker = "; ".join(status.blockers[:6]) or "none"
    block = f"""  - id: AUTH-REFRESH-DB-PROOF-001
    title: Auth refresh-token DB persistence and revocation proof
    severity: P1
    gate: 3
    owner: backend
    implementation_batch: code_2671_2710
    proof_status: {proof}
    proof_command: make auth-refresh-db-proof-release-check
    evidence_file: docs/release/auth_refresh_db_proof_status.md
    last_verified_commit: {current_commit() if proof == "integration-passing" else "null"}
    closure_blocker: {blocker}
    blocks_beta: true
    external_dependency: true
"""
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    REGISTRY.write_text(replace_or_append(text, "AUTH-REFRESH-DB-PROOF-001", block), encoding="utf-8")
    print("Updated AUTH-REFRESH-DB-PROOF-001 registry entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
