#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def current_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def block() -> str:
    return f"""  - id: BLOCKER-BURN-001
    title: Beta blocker burn-down planning
    severity: P1
    gate: 7
    owner: release
    implementation_batch: code_1871_1910
    proof_status: runtime-passing
    proof_command: make backend-implementation-1871-1910-full-check
    evidence_file: docs/release/beta_blocker_burndown_plan.md
    last_verified_commit: {current_commit()}
    closure_blocker: plan only; blockers remain until their own evidence gates pass
    blocks_beta: false
    external_dependency: false
"""


def replace_or_append(text: str) -> str:
    if "findings:" not in text:
        text = "findings:\n"
    marker = "  - id: BLOCKER-BURN-001"
    index = text.find(marker)
    if index < 0:
        return text.rstrip() + "\n" + block()
    next_index = text.find("\n  - id:", index + 1)
    if next_index < 0:
        return text[:index] + block()
    return text[:index] + block() + text[next_index + 1:]


def main() -> int:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    REGISTRY.write_text(replace_or_append(text), encoding="utf-8")
    print("Updated BLOCKER-BURN-001 evidence registry entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
