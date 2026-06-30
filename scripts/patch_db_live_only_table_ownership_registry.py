#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.db_live_only_table_ownership import write_status  # noqa: E402

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
    accepted = status.status == "db-live-only-table-ownership-accepted"

    proof_status = "policy-accepted" if accepted else "not-proven"
    closure_blocker = "none" if accepted else "live-only table ownership policy incomplete"
    release_ready = "true" if accepted else "false"

    block = f"""  - id: DB-OWNERSHIP-001R
    title: Live-only POPIA/DSR table ownership classification
    severity: P1
    gate: 2
    owner: backend
    implementation_batch: code_3111_3150
    proof_status: {proof_status}
    proof_command: make backend-implementation-3111-3150-full-check
    evidence_file: docs/release/db_live_only_table_ownership_status.md
    policy_file: docs/architecture/db_live_only_table_ownership.yml
    accepted_records: {status.accepted_count}/{status.required_count}
    last_verified_commit: {status.current_commit if accepted else "null"}
    closure_blocker: {closure_blocker}
    release_ready: {release_ready}
    blocks_beta: false
    external_dependency: false
"""

    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    text = _replace_or_append(text, "DB-OWNERSHIP-001R", block)
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated DB-OWNERSHIP-001R registry entry")

    if not accepted:
        print("DB live-only table ownership is not accepted; blockers:")
        for blocker in status.blockers:
            print(f"- {blocker}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
