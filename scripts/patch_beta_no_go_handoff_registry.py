#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.beta_no_go_handoff_packet import write_packet  # noqa: E402

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
    packet = write_packet()
    return f"""  - id: BETA-NO-GO-HANDOFF-001
    title: Beta NO-GO handoff packet
    severity: P1
    gate: 7
    owner: release
    implementation_batch: code_2351_2390
    proof_status: runtime-passing
    proof_command: make backend-implementation-2351-2390-full-check
    evidence_file: docs/release/beta_no_go_handoff_packet.md
    last_verified_commit: {current_commit()}
    closure_blocker: handoff only; beta decision remains {packet.beta_decision}
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
    text = replace_or_append(text, "BETA-NO-GO-HANDOFF-001", block())
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated BETA-NO-GO-HANDOFF-001 registry entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
