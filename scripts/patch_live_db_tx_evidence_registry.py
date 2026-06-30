#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.live_db_tx_evidence import SLICES, build_status, current_commit, read_record  # noqa: E402

REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def slice_block(slice_name: str) -> str:
    record = read_record(slice_name)
    meta = SLICES[slice_name]
    accepted = record.status == "live-db-proof-accepted"
    proof_status = "integration-passing" if accepted else "external-blocked"
    last_verified = current_commit() if accepted else "null"
    blocker = "none" if accepted else "live DB rollback evidence metadata required"
    return f"""  - id: {meta['item']}
    title: {meta['title']}
    severity: P1
    gate: 4
    owner: backend
    implementation_batch: code_2231_2270
    proof_status: {proof_status}
    proof_command: {meta['release_check']}
    evidence_file: {meta['evidence_file']}
    last_verified_commit: {last_verified}
    closure_blocker: {blocker}
    blocks_beta: false
    external_dependency: false
"""


def scaffold_block() -> str:
    status = build_status()
    return f"""  - id: LIVE-DB-TX-EVID-001
    title: Live database transaction evidence attachment support
    severity: P1
    gate: 4
    owner: backend
    implementation_batch: code_2231_2270
    proof_status: runtime-passing
    proof_command: make backend-implementation-2231-2270-full-check
    evidence_file: docs/release/live_db_transaction_evidence_status.md
    last_verified_commit: {current_commit()}
    closure_blocker: scaffold only; live DB evidence aggregate status is {status.status}
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
    for slice_name, meta in SLICES.items():
        text = replace_or_append(text, meta["item"], slice_block(slice_name))
    text = replace_or_append(text, "LIVE-DB-TX-EVID-001", scaffold_block())
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated live DB transaction evidence registry entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
