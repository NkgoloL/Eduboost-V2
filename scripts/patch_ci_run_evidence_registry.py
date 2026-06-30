#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ci_run_evidence import build_status, current_commit  # noqa: E402

REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def ci_block() -> str:
    status = build_status()
    accepted = status.status == "ci-evidence-accepted"
    proof_status = "integration-passing" if accepted else "external-blocked"
    last_verified = current_commit() if accepted else "null"
    blocker = "none" if accepted else "valid GitHub Actions run URL and passing result metadata required"
    return f"""  - id: CI-001
    title: Authoritative CI on release repo and branch
    severity: P1
    gate: 2
    owner: release
    implementation_batch: code_1951_1990
    proof_status: {proof_status}
    proof_command: make ci-run-evidence-release-check
    evidence_file: docs/release/ci_evidence.md
    last_verified_commit: {last_verified}
    closure_blocker: {blocker}
    blocks_beta: true
    external_dependency: true
"""


def scaffold_block() -> str:
    return f"""  - id: CI-RUN-001
    title: CI evidence attachment and verification support
    severity: P1
    gate: 2
    owner: release
    implementation_batch: code_1951_1990
    proof_status: runtime-passing
    proof_command: make backend-implementation-1951-1990-full-check
    evidence_file: docs/release/ci_run_evidence_status.md
    last_verified_commit: {current_commit()}
    closure_blocker: scaffold only; CI-001 remains external-blocked until accepted CI evidence is attached
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
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    text = replace_or_append(text, "CI-001", ci_block())
    text = replace_or_append(text, "CI-RUN-001", scaffold_block())
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated CI-001 and CI-RUN-001 registry entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
