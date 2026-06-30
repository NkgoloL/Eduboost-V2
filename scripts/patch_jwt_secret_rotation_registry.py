#!/usr/bin/env python3
from __future__ import annotations
import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.jwt_secret_rotation_evidence import ACCEPTED_STATUS, write_status  # noqa: E402
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"

def replace_or_append(text: str, item_id: str, block: str) -> str:
    if "findings:" not in text: text = "findings:\n"
    marker = f"  - id: {item_id}"
    start = text.find(marker)
    if start < 0: return text.rstrip() + "\n" + block
    end = text.find("\n  - id:", start + 1)
    return text[:start] + block if end < 0 else text[:start] + block + text[end + 1:]

def main() -> int:
    s = write_status(); accepted = s.status == ACCEPTED_STATUS
    proof = "runtime-passing" if accepted else "not-proven"
    blocker = "none" if accepted else "JWT secret provisioning and rotation evidence required"
    ready = "true" if accepted else "false"; blocks = "false" if accepted else "true"
    common = f"""    proof_status: {proof}
    proof_command: make jwt-secret-rotation-release-check
    evidence_file: docs/release/jwt_secret_rotation_evidence_status.md
    evidence_url: {s.github_run.run_url if accepted else "null"}
    workflow_name: {s.github_run.workflow_name if accepted else "null"}
    run_id: {s.github_run.run_id if accepted else "null"}
    evidence_environment: {s.evidence_environment if accepted else "null"}
    algorithm: {s.algorithm}
    access_fingerprint: {s.access_current.fingerprint if accepted else "null"}
    refresh_fingerprint: {s.refresh_current.fingerprint if accepted else "null"}
    access_rotated: {str(s.access_rotated).lower()}
    refresh_rotated: {str(s.refresh_rotated).lower()}
    last_verified_commit: {s.current_commit if accepted else "null"}
    verified_by: {s.verified_by if accepted else "null"}
    date_verified: {s.date_verified if accepted else "null"}
    closure_blocker: {blocker}
    release_ready: {ready}
    blocks_beta: {blocks}
    external_dependency: true
"""
    jwt = f"""  - id: JWT-001
    title: JWT secret provisioning and rotation evidence
    severity: P0
    gate: 6
    owner: backend
    implementation_batch: code_3351_3390
{common}"""
    repair = f"""  - id: JWT-001R
    title: JWT secret rotation evidence repair
    severity: P0
    gate: 6
    owner: backend
    implementation_batch: code_3351_3390
{common}"""
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    REGISTRY.write_text(replace_or_append(replace_or_append(text, "JWT-001", jwt), "JWT-001R", repair), encoding="utf-8")
    print("Updated JWT-001 and JWT-001R registry entries")
    if os.getenv("JWT_EVIDENCE_ACCEPT") == "1" and not accepted:
        print("JWT secret rotation evidence is not accepted; blockers:")
        for b in s.blockers: print(f"- {b}")
        return 1
    return 0
if __name__ == "__main__": raise SystemExit(main())
