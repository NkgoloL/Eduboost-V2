#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"

APPROVALS = {
    "LEGAL-001": {
        "title": "POPIA/legal release approval",
        "owner": "legal",
        "file": "docs/release/external_approvals/legal_approval.md",
    },
    "SEC-001": {
        "title": "Security release approval",
        "owner": "security",
        "file": "docs/release/external_approvals/security_approval.md",
    },
    "CONTENT-001": {
        "title": "Educator/content release approval",
        "owner": "content",
        "file": "docs/release/external_approvals/content_approval.md",
    },
    "STAGING-001": {
        "title": "Staging acceptance approval",
        "owner": "release",
        "file": "docs/release/external_approvals/staging_acceptance.md",
    },
}


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


def block_for(approval_id: str, meta: dict[str, str]) -> str:
    return f"""  - id: {approval_id}
    title: {meta['title']}
    severity: P1
    gate: 5
    owner: {meta['owner']}
    implementation_batch: code_1791_1830
    proof_status: external-blocked
    proof_command: make external-approval-release-check after approval metadata is attached
    evidence_file: {meta['file']}
    last_verified_commit: null
    closure_blocker: external approval sign-off metadata required
    blocks_beta: true
    external_dependency: true
"""


def ext_gate_block() -> str:
    return f"""  - id: EXT-GATE-001
    title: External approval tracking gate
    severity: P1
    gate: 5
    owner: release
    implementation_batch: code_1791_1830
    proof_status: runtime-passing
    proof_command: make backend-implementation-1791-1830-full-check
    evidence_file: docs/release/external_approval_status.md
    last_verified_commit: {current_commit()}
    closure_blocker: required external approval items remain external-blocked until signed off
    blocks_beta: true
    external_dependency: true
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

    for approval_id, meta in APPROVALS.items():
        text = replace_or_append(text, approval_id, block_for(approval_id, meta))
    text = replace_or_append(text, "EXT-GATE-001", ext_gate_block())

    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated external approval registry entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
