#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.prod_frontend_runtime import write_status  # noqa: E402

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


def block() -> str:
    status = write_status()
    proof_status = (
        "integration-passing"
        if status.status == "runtime-evidence-accepted"
        else "runtime-passing"
        if status.status in {"runtime-preflight-passing", "runtime-preflight-static-passing-compose-tool-unavailable"}
        else "not-proven"
    )
    return f"""  - id: DEPLOY-FE-RUNTIME-001
    title: Production frontend runtime proof guardrails
    severity: P1
    gate: 5
    owner: platform
    implementation_batch: code_2471_2510
    proof_status: {proof_status}
    proof_command: make backend-implementation-2471-2510-full-check
    evidence_file: docs/release/production_frontend_runtime_status.md
    last_verified_commit: {current_commit() if proof_status != "not-proven" else "null"}
    closure_blocker: local preflight only unless runtime evidence is accepted
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
    text = replace_or_append(text, "DEPLOY-FE-RUNTIME-001", block())
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated DEPLOY-FE-RUNTIME-001 registry entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
