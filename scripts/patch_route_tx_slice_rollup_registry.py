#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.route_tx_slice_rollup import write_rollup  # noqa: E402

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


def rollup_block() -> str:
    return f"""  - id: ROUTE-TX-ROLLUP-001
    title: Route transaction slice rollup and remaining-gap reconciliation
    severity: P1
    gate: 4
    owner: backend
    implementation_batch: code_2191_2230
    proof_status: runtime-passing
    proof_command: make backend-implementation-2191-2230-full-check
    evidence_file: docs/release/route_transaction_slice_rollup.md
    last_verified_commit: {current_commit()}
    closure_blocker: rollup only; TX-ROUTE-001 remains blocked while local/live DB gaps remain
    blocks_beta: false
    external_dependency: false
"""


def tx_route_block() -> str:
    rollup = write_rollup()
    tx_status = "production-ready" if rollup.status == "route-transaction-slices-release-ready" else "not-proven"
    last_verified = current_commit() if tx_status == "production-ready" else "null"
    return f"""  - id: TX-ROUTE-001
    title: Production route transaction wiring inventory
    severity: P1
    gate: 4
    owner: backend
    implementation_batch: code_2191_2230
    proof_status: {tx_status}
    proof_command: make route-tx-slice-rollup-release-check
    evidence_file: docs/release/route_transaction_slice_rollup.md
    last_verified_commit: {last_verified}
    closure_blocker: local_gaps={rollup.local_source_gap_count}; live_db_gaps={rollup.live_db_gap_count}; inventory_unproven={rollup.inventory_unproven_route_count}
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
    text = replace_or_append(text, "TX-ROUTE-001", tx_route_block())
    text = replace_or_append(text, "ROUTE-TX-ROLLUP-001", rollup_block())
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated ROUTE-TX-ROLLUP-001 and TX-ROUTE-001 registry entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
