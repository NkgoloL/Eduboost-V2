#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"

CI_BLOCK = """  - id: CI-001
    title: Authoritative CI on release repo and branch
    severity: P1
    gate: 2
    owner: release
    implementation_batch: code_1671_1710
    proof_status: external-blocked
    proof_command: attach passing GitHub Actions run URL and run make ci-authority-release-check
    evidence_file: docs/release/ci_evidence.md
    last_verified_commit: null
    closure_blocker: GitHub Actions run URL required for codex/production_readiness
    blocks_beta: true
    external_dependency: true
"""


def replace_or_append_ci_block(text: str) -> str:
    if "findings:" not in text:
        text = "findings:\n"

    marker = "  - id: CI-001"
    index = text.find(marker)
    if index < 0:
        return text.rstrip() + "\n" + CI_BLOCK

    next_index = text.find("\n  - id:", index + 1)
    if next_index < 0:
        return text[:index] + CI_BLOCK
    return text[:index] + CI_BLOCK + text[next_index + 1 :]


def main() -> int:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    original = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    updated = replace_or_append_ci_block(original)
    REGISTRY.write_text(updated, encoding="utf-8")
    print("Updated CI-001 evidence registry entry as external-blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
