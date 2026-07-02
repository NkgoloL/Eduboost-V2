#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_rr002_privacy_popia_completion import verify

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/roadmap/reconciliation/rr_002_privacy_popia_completion_record.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/roadmap-reconciliation/rr-002-privacy-popia-completion"
RAW_DIR = EVIDENCE_DIR / "raw"
CHECKSUM_FILES = [
    "app/services/popia_erasure_safety.py",
    "app/services/popia_service.py",
    "app/api_v2_routers/learners.py",
    "app/api_v2_routers/parents.py",
    "docs/roadmap/reconciliation/outstanding_work_register.md",
    "docs/roadmap/reconciliation/rr_002_privacy_popia_completion.md",
    "docs/roadmap/reconciliation/rr_002_privacy_popia_completion_record.json",
]


def _run_git(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"unavailable: {exc}"


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def capture(owner: str, target_branch: str, claim: bool) -> dict[str, Any]:
    verification = verify()
    status_short = _run_git(["status", "--short"])
    git_state = {
        "branch": _run_git(["branch", "--show-current"]),
        "head_sha": _run_git(["rev-parse", "HEAD"]),
        "target_branch": target_branch,
        "status_short": status_short,
    }
    recorded = bool(claim and verification["valid"])
    record = {
        "rr_id": "RR-002",
        "status": "privacy_popia_completion_recorded" if recorded else "authority_installed_evidence_pending",
        "privacy_popia_completion_recorded": recorded,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "privacy_owner": owner,
        "target_branch": target_branch,
        "legal_hold_checks_before_erasure": recorded,
        "export_offered_before_erasure": recorded,
        "deletion_flow_persisted": recorded,
        "repository_backed_authorization_enforced": recorded,
        "audit_immutability_preserved": recorded,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "verification": verification,
        "git_state": git_state,
        "clean_git_state_at_capture": status_short == "",
    }
    _write(RECORD, record)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    _write(RAW_DIR / "rr002_privacy_popia_completion_result.json", record)
    _write(RAW_DIR / "git_state.json", git_state)
    _write(RAW_DIR / "verification.json", verification)

    lines: list[str] = []
    for rel in CHECKSUM_FILES:
        path = ROOT / rel
        if path.exists():
            lines.append(f"{_sha(path)}  {rel}")
    (EVIDENCE_DIR / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    index = "\n".join([
        "# RR-002 Privacy / POPIA Completion Evidence",
        "",
        f"Recorded: {recorded}",
        f"Owner: {owner}",
        f"Target branch: {target_branch}",
        "",
        "## Boundary",
        "",
        "This evidence records RR-002 privacy/POPIA completion only. It does not authorise production release, deployment, public beta, release tagging, or runtime KG implementation.",
        "",
        "## Files",
        "",
        *[f"- `{line.split('  ', 1)[1]}`" for line in lines],
        "",
    ])
    (EVIDENCE_DIR / "evidence_index.md").write_text(index, encoding="utf-8")
    (EVIDENCE_DIR / "evidence_index.sha256").write_text(_sha(EVIDENCE_DIR / "evidence_index.md") + "  evidence_index.md\n", encoding="utf-8")

    return {
        "valid": recorded and verification["valid"],
        "rr_id": "RR-002",
        "privacy_popia_completion_recorded": recorded,
        "verification_valid": verification["valid"],
        "clean_git_state_at_capture": status_short == "",
        "production_release_authorised": False,
        "deployment_authorised": False,
        "public_beta_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "evidence_dir": str(EVIDENCE_DIR.relative_to(ROOT)),
        "errors": verification["errors"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-rr002-privacy-popia-completion", action="store_true")
    parser.add_argument("--privacy-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = capture(args.privacy_owner, args.target_branch, args.claim_rr002_privacy_popia_completion)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid" if result["valid"] else "invalid")
    if args.require_valid and not result["valid"]:
        return 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
