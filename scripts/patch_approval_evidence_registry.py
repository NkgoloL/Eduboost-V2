#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.approval_evidence import APPROVALS, build_status, current_commit, read_record  # noqa: E402

REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def approval_block(approval_id: str) -> str:
    record = read_record(approval_id)
    meta = APPROVALS[approval_id]
    approved = record.status == "approved"
    proof_status = "production-ready" if approved else "external-blocked"
    last_verified = current_commit() if approved else "null"
    blocker = "none" if approved else "approval metadata and evidence URL required"
    return f"""  - id: {approval_id}
    title: {meta['title']}
    severity: P1
    gate: 5
    owner: {meta['owner']}
    implementation_batch: code_1991_2030
    proof_status: {proof_status}
    proof_command: make approval-evidence-release-check
    evidence_file: docs/release/external_approvals/{meta['file']}
    last_verified_commit: {last_verified}
    closure_blocker: {blocker}
    blocks_beta: true
    external_dependency: true
"""


def scaffold_block() -> str:
    return f"""  - id: APPROVAL-EVID-001
    title: Legal/security/content approval evidence attachment support
    severity: P1
    gate: 5
    owner: release
    implementation_batch: code_1991_2030
    proof_status: runtime-passing
    proof_command: make backend-implementation-1991-2030-full-check
    evidence_file: docs/release/approval_evidence_status.md
    last_verified_commit: {current_commit()}
    closure_blocker: scaffold only; individual approvals remain external-blocked until accepted metadata is attached
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
    build_status()
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    for approval_id in APPROVALS:
        text = replace_or_append(text, approval_id, approval_block(approval_id))
    text = replace_or_append(text, "APPROVAL-EVID-001", scaffold_block())
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated approval evidence registry entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
