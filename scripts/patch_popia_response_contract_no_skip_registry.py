#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.popia_response_contract_no_skips import write_status  # noqa: E402

REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
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
    status = write_status(run_tests=True)
    accepted = status.status == "popia-response-contract-no-skip-passing"
    proof = "integration-passing" if accepted else "not-proven"
    blocker = "none" if accepted else "; ".join(status.blockers[:6])
    blocks_beta = "false" if accepted else "true"
    commit = current_commit() if accepted else "null"

    popia_block = f"""  - id: POPIA-001
    title: POPIA lifecycle HTTP response-contract proof
    severity: P1
    gate: 3
    owner: backend
    implementation_batch: code_2831_2870R
    proof_status: {proof}
    proof_command: make backend-implementation-2831-2870R-full-check
    evidence_file: docs/release/popia_response_contract_no_skip_status.md
    last_verified_commit: {commit}
    closure_blocker: {blocker}
    blocks_beta: {blocks_beta}
    external_dependency: false
"""

    repair_block = f"""  - id: POPIA-001R
    title: POPIA no-skip response-contract proof repair
    severity: P1
    gate: 3
    owner: backend
    implementation_batch: code_2831_2870R
    proof_status: {proof}
    proof_command: make backend-implementation-2831-2870R-full-check
    evidence_file: docs/release/popia_response_contract_no_skip_status.md
    last_verified_commit: {commit}
    closure_blocker: {blocker}
    blocks_beta: false
    external_dependency: false
"""

    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    text = replace_or_append(text, "POPIA-001", popia_block)
    text = replace_or_append(text, "POPIA-001R", repair_block)
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated POPIA-001 and POPIA-001R registry entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
