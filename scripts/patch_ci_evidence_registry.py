#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ci_evidence_acceptance import ACCEPTED_STATUS, write_status  # noqa: E402

REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def _replace_or_append(text: str, item_id: str, block: str) -> str:
    if "findings:" not in text:
        text = "findings:\n"

    marker = f"  - id: {item_id}"
    start = text.find(marker)
    if start < 0:
        return text.rstrip() + "\n" + block

    end = text.find("\n  - id:", start + 1)
    if end < 0:
        return text[:start] + block

    return text[:start] + block + text[end + 1 :]


def _block(item_id: str, title: str, status) -> str:
    accepted = status.status == ACCEPTED_STATUS
    proof_status = "integration-passing" if accepted else "external-blocked"
    closure_blocker = "none" if accepted else "valid GitHub Actions run URL and passing result metadata required"
    blocks_beta = "false" if accepted else "true"
    release_ready = "true" if accepted else "false"
    severity = "P0" if item_id == "CI-001" else "P1"

    return f"""  - id: {item_id}
    title: {title}
    severity: {severity}
    gate: 7
    owner: release
    implementation_batch: code_2871_2910
    proof_status: {proof_status}
    proof_command: make backend-implementation-2871-2910-full-check
    evidence_file: docs/release/ci_evidence_status.md
    evidence_url: {status.run_url if accepted else "null"}
    workflow_name: {status.workflow_name if accepted else "null"}
    run_id: {status.run_id if accepted else "null"}
    last_verified_commit: {status.current_commit if accepted else "null"}
    verified_by: {status.verified_by if accepted else "null"}
    date_verified: {status.date_verified if accepted else "null"}
    closure_blocker: {closure_blocker}
    release_ready: {release_ready}
    blocks_beta: {blocks_beta}
    external_dependency: true
"""


def main() -> int:
    status = write_status()
    if status.status != ACCEPTED_STATUS:
        print("CI evidence is not accepted; registry will not be patched as closed")
        for blocker in status.blockers:
            print(f"- {blocker}")
        return 1

    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"

    text = _replace_or_append(
        text,
        "CI-001",
        _block("CI-001", "Accepted GitHub Actions CI evidence", status),
    )
    text = _replace_or_append(
        text,
        "EVID-001",
        _block("EVID-001", "Accepted evidence registry CI authority", status),
    )
    text = _replace_or_append(
        text,
        "CI-001R",
        _block("CI-001R", "CI evidence acceptance repair", status),
    )
    text = _replace_or_append(
        text,
        "EVID-001R",
        _block("EVID-001R", "Evidence registry CI authority repair", status),
    )

    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated CI-001, EVID-001, CI-001R, and EVID-001R registry entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
