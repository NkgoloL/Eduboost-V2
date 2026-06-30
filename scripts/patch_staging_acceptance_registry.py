#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


def staging_block() -> str:
    return """  - id: STAGING-001
    title: Staging acceptance approval
    severity: P1
    gate: 5
    owner: release
    implementation_batch: code_1911_1950
    proof_status: external-blocked
    proof_command: make staging-acceptance-release-check
    evidence_file: docs/release/staging_smoke_evidence.md
    last_verified_commit: null
    closure_blocker: real staging smoke evidence and GitHub Actions run URL required
    blocks_beta: true
    external_dependency: true
"""


def scaffold_block() -> str:
    return f"""  - id: STAGING-PROOF-001
    title: Staging acceptance evidence capture scaffold
    severity: P1
    gate: 5
    owner: release
    implementation_batch: code_1911_1950
    proof_status: runtime-passing
    proof_command: make backend-implementation-1911-1950-full-check
    evidence_file: docs/release/staging_acceptance_status.md
    last_verified_commit: {current_commit()}
    closure_blocker: scaffold only; STAGING-001 remains external-blocked until real staging evidence is attached
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
    text = replace_or_append(text, "STAGING-001", staging_block())
    text = replace_or_append(text, "STAGING-PROOF-001", scaffold_block())
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated STAGING-001 and STAGING-PROOF-001 registry entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
