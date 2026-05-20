#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.popia_route_tx_gap_plan import write_plan  # noqa: E402

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


def popia_block() -> str:
    plan = write_plan()
    proven = plan.source_local_status == "route-popia-delegation-passing" and plan.action_count == 0
    proof_status = "runtime-passing" if proven else "not-proven"
    commit = current_commit() if proven else "null"
    blocker = (
        "live DB rollback proof remains external-blocked for this slice"
        if proven
        else f"POPIA route source delegation not proven; {plan.action_count} gap actions remain"
    )
    return f"""  - id: ROUTE-TX-POPIA-001
    title: POPIA route transaction slice
    severity: P1
    gate: 4
    owner: backend
    implementation_batch: code_2111_2150R
    proof_status: {proof_status}
    proof_command: make popia-route-tx-no-false-closure-check
    evidence_file: docs/release/popia_route_transaction_gap_plan.md
    last_verified_commit: {commit}
    closure_blocker: {blocker}
    blocks_beta: false
    external_dependency: false
"""


def repair_block() -> str:
    return f"""  - id: ROUTE-TX-POPIA-001R
    title: POPIA route transaction no-false-closure repair
    severity: P1
    gate: 4
    owner: backend
    implementation_batch: code_2111_2150R
    proof_status: runtime-passing
    proof_command: make backend-implementation-2111-2150R-full-check
    evidence_file: docs/release/popia_route_transaction_gap_plan.md
    last_verified_commit: {current_commit()}
    closure_blocker: repair only; implementation gaps remain until source local status passes
    blocks_beta: false
    external_dependency: false
"""


def replace_or_append(text: str, item_id: str, block: str) -> str:
    if "findings:" not in text:
        text = "findings:\n"
    marker = f"  - id: {item_id}"
    index = text.find(marker)
    if index < 0:
        return text.rstrip() + "\n" + block
    next_index = text.find("\n  - id:", index + 1)
    if next_index < 0:
        return text[:index] + block
    return text[:index] + block + text[next_index + 1 :]


def main() -> int:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    text = replace_or_append(text, "ROUTE-TX-POPIA-001", popia_block())
    text = replace_or_append(text, "ROUTE-TX-POPIA-001R", repair_block())
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated POPIA route transaction not-proven registry entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
