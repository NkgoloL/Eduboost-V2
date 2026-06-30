#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.route_tx_impl_plan import current_commit, write_plan  # noqa: E402

REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def block() -> str:
    plan = write_plan()
    return f"""  - id: ROUTE-TX-IMPL-001
    title: Production transaction route wiring implementation plan
    severity: P1
    gate: 4
    owner: backend
    implementation_batch: code_2031_2070
    proof_status: runtime-passing
    proof_command: make backend-implementation-2031-2070-full-check
    evidence_file: docs/release/route_transaction_implementation_plan.md
    last_verified_commit: {current_commit()}
    closure_blocker: plan only; {plan.action_count} route transaction wiring actions remain until implemented and proven
    blocks_beta: false
    external_dependency: false
"""


def tx_route_block() -> str:
    plan = write_plan()
    return f"""  - id: TX-ROUTE-001
    title: Production route transaction wiring inventory
    severity: P1
    gate: 4
    owner: backend
    implementation_batch: code_2031_2070
    proof_status: runtime-passing
    proof_command: make tx-route-impl-plan-check
    evidence_file: docs/release/route_transaction_implementation_plan.md
    last_verified_commit: {current_commit()}
    closure_blocker: {plan.action_count} production mutation route transaction wiring actions remain pending
    blocks_beta: false
    external_dependency: false
"""


def replace_or_append(text: str, item_id: str, item_block: str) -> str:
    if "findings:" not in text:
        text = "findings:\n"
    marker = f"  - id: {item_id}"
    index = text.find(marker)
    if index < 0:
        return text.rstrip() + "\n" + item_block

    next_index = text.find("\n  - id:", index + 1)
    if next_index < 0:
        return text[:index] + item_block
    return text[:index] + item_block + text[next_index + 1 :]


def main() -> int:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    text = replace_or_append(text, "TX-ROUTE-001", tx_route_block())
    text = replace_or_append(text, "ROUTE-TX-IMPL-001", block())
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated ROUTE-TX-IMPL-001 registry entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
