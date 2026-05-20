#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.route_tx_diagnostics_slice import write_gap_plan, write_report  # noqa: E402

REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def current_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def diagnostics_slice_block() -> str:
    report = write_report()
    gap_plan = write_gap_plan()
    proof_status = "runtime-passing" if report.local_status == "route-diagnostics-delegation-passing" else "not-proven"
    blocker = (
        "live DB rollback proof remains external-blocked for this slice"
        if proof_status == "runtime-passing"
        else f"diagnostics route source delegation not proven; {gap_plan.action_count} gap actions remain"
    )
    return f"""  - id: ROUTE-TX-DIAG-001
    title: Diagnostics route transaction slice
    severity: P1
    gate: 4
    owner: backend
    implementation_batch: code_2151_2190
    proof_status: {proof_status}
    proof_command: make backend-implementation-2151-2190-full-check
    evidence_file: docs/release/diagnostics_route_transaction_slice_report.md
    last_verified_commit: {current_commit() if proof_status == "runtime-passing" else "null"}
    closure_blocker: {blocker}
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
    text = replace_or_append(text, "ROUTE-TX-DIAG-001", diagnostics_slice_block())
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated ROUTE-TX-DIAG-001 registry entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
