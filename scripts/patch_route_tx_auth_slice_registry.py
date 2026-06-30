#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.route_tx_auth_slice import write_report  # noqa: E402

REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def current_commit() -> str:
    import subprocess

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def auth_slice_block() -> str:
    report = write_report()
    proof_status = "runtime-passing" if report.local_status == "route-auth-delegation-passing" else "not-proven"
    return f"""  - id: ROUTE-TX-AUTH-001
    title: First production route transaction wiring slice for auth routes
    severity: P1
    gate: 4
    owner: backend
    implementation_batch: code_2071_2110
    proof_status: {proof_status}
    proof_command: make backend-implementation-2071-2110-full-check
    evidence_file: docs/release/auth_route_transaction_slice_report.md
    last_verified_commit: {current_commit() if proof_status == "runtime-passing" else "null"}
    closure_blocker: live DB rollback proof remains external-blocked for this slice
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
    text = replace_or_append(text, "ROUTE-TX-AUTH-001", auth_slice_block())
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated ROUTE-TX-AUTH-001 registry entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
