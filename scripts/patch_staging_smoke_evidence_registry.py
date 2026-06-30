#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.staging_smoke_evidence_acceptance import ACCEPTED_STATUS, write_status  # noqa: E402

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
    closure_blocker = "none" if accepted else "real staging smoke evidence and GitHub Actions run URL required"
    blocks_beta = "false" if accepted else "true"
    release_ready = "true" if accepted else "false"

    return f"""  - id: {item_id}
    title: {title}
    severity: P0
    gate: 8
    owner: release
    implementation_batch: code_2911_2950
    proof_status: {proof_status}
    proof_command: make backend-implementation-2911-2950-full-check
    evidence_file: docs/release/staging_smoke_evidence_status.md
    evidence_url: {status.run_url if accepted else "null"}
    workflow_name: {status.workflow_name if accepted else "null"}
    run_id: {status.run_id if accepted else "null"}
    staging_base_url: {status.staging_base_url if accepted else "null"}
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
        print("Staging smoke evidence is not accepted; registry will not be patched as closed")
        for blocker in status.blockers:
            print(f"- {blocker}")
        return 1

    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"

    text = _replace_or_append(
        text,
        "STAGING-001",
        _block("STAGING-001", "Accepted staging smoke evidence", status),
    )
    text = _replace_or_append(
        text,
        "STAGING-001R",
        _block("STAGING-001R", "Staging smoke evidence acceptance repair", status),
    )

    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated STAGING-001 and STAGING-001R registry entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
