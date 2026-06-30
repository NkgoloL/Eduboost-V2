#!/usr/bin/env python3
from __future__ import annotations
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.auth_route_logout_delegate import write_status  # noqa: E402
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
    status = write_status()
    proof = "runtime-passing" if status.status == "auth-route-logout-delegation-passing" else "not-proven"
    blocker = "; ".join(status.blockers) or "none"
    block = f"""  - id: AUTH-ROUTE-LOGOUT-DELEGATE-001
    title: Auth logout and revoke-all route delegation to service
    severity: P1
    gate: 3
    owner: backend
    implementation_batch: code_2551_2590
    proof_status: {proof}
    proof_command: make backend-implementation-2551-2590-full-check
    evidence_file: docs/release/auth_route_logout_delegate_status.md
    last_verified_commit: {current_commit() if proof == "runtime-passing" else "null"}
    closure_blocker: {blocker}
    blocks_beta: false
    external_dependency: false
"""
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    REGISTRY.write_text(replace_or_append(text, "AUTH-ROUTE-LOGOUT-DELEGATE-001", block), encoding="utf-8")
    print("Updated AUTH-ROUTE-LOGOUT-DELEGATE-001 registry entry")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
