#!/usr/bin/env python3
"""Capture RR-001 Atlas phase status reconciliation evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_rr001_atlas_phase_status_reconciliation import verify

ROOT = Path(__file__).resolve().parents[2]
RECON_DIR = ROOT / "docs" / "roadmap" / "reconciliation"
RECORD = RECON_DIR / "rr_001_atlas_phase_status_record.json"
EVIDENCE_DIR = ROOT / "docs" / "release-evidence" / "roadmap-reconciliation" / "rr-001-atlas-phase-status-reconciliation"
RAW_DIR = EVIDENCE_DIR / "raw"

SNAPSHOT_FILES = [
    "docs/roadmap/PHASE_STATUS_REGISTER.md",
    "docs/roadmap/reconciliation/roadmap_reconciliation_record.json",
    "docs/roadmap/reconciliation/outstanding_work_register.md",
    "docs/roadmap/reconciliation/phase_18_to_21_governance_classification.md",
    "docs/roadmap/reconciliation/rr_001_atlas_phase_status_reconciliation.md",
    "docs/roadmap/reconciliation/rr_001_atlas_phase_status_matrix.json",
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_state() -> dict[str, str]:
    def run(*cmd: str) -> str:
        return subprocess.check_output(cmd, cwd=ROOT, text=True).strip()
    return {
        "branch": run("git", "branch", "--show-current"),
        "head_sha": run("git", "rev-parse", "HEAD"),
        "status_short": run("git", "status", "--short"),
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def capture(owner: str, target_branch: str, require_valid: bool) -> dict[str, Any]:
    verification = verify()
    if require_valid and not verification["valid"]:
        return {
            "valid": False,
            "errors": verification["errors"],
            "warnings": verification.get("warnings", []),
            "status": "rr001_atlas_phase_status_reconciliation_invalid",
        }

    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    git_state = _git_state()

    if EVIDENCE_DIR.exists():
        shutil.rmtree(EVIDENCE_DIR)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    snapshots: list[dict[str, str]] = []
    for rel in SNAPSHOT_FILES:
        src = ROOT / rel
        dst = RAW_DIR / rel.replace("/", "__")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        snapshots.append({"path": rel, "sha256": _sha256(src)})

    _write_json(RAW_DIR / "verification.json", verification)
    _write_json(RAW_DIR / "git_state.json", git_state)

    result = {
        "version": 1,
        "rr_id": "RR-001",
        "status": "rr001_atlas_phase_status_reconciled",
        "captured_at": captured_at,
        "target_branch": target_branch,
        "reconciliation_owner": owner,
        "roadmap_reconciliation_claimed": True,
        "rr001_atlas_phase_status_reconciliation_claimed": True,
        "atlas_phase_register_reconciled": True,
        "old_phase_register_superseded": True,
        "phase_18_to_21_auxiliary_governance": True,
        "next_work_must_cite_rr_id": True,
        "new_unreconciled_work_authorised": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "verification": verification,
        "git_state": git_state,
        "snapshots": snapshots,
        "evidence_dir": str(EVIDENCE_DIR.relative_to(ROOT)),
        "valid": verification["valid"],
        "errors": verification["errors"],
        "warnings": verification.get("warnings", []),
    }

    _write_json(RAW_DIR / "rr001_capture_result.json", result)
    _write_json(RECORD, {k: v for k, v in result.items() if k not in {"verification", "snapshots"}})

    index = EVIDENCE_DIR / "evidence_index.md"
    lines = [
        "# RR-001 Atlas Phase Status Reconciliation Evidence",
        "",
        f"Captured at: `{captured_at}`",
        f"Owner: `{owner}`",
        f"Target branch: `{target_branch}`",
        f"HEAD: `{git_state['head_sha']}`",
        "",
        "## Result",
        "",
        f"- valid: `{verification['valid']}`",
        "- production release authorised: `false`",
        "- public beta authorised: `false`",
        "- runtime KG implementation claimed: `false`",
        "",
        "## Snapshots",
        "",
    ]
    for item in snapshots:
        lines.append(f"- `{item['path']}` — `{item['sha256']}`")
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (EVIDENCE_DIR / "evidence_index.sha256").write_text(_sha256(index) + "  evidence_index.md\n", encoding="utf-8")

    sha_lines = []
    for path in sorted(EVIDENCE_DIR.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            sha_lines.append(f"{_sha256(path)}  {path.relative_to(EVIDENCE_DIR)}")
    (EVIDENCE_DIR / "SHA256SUMS.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-rr001-reconciliation", action="store_true")
    parser.add_argument("--reconciliation-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.claim_rr001_reconciliation:
        result = {"valid": False, "errors": ["--claim-rr001-reconciliation is required"]}
    else:
        result = capture(args.reconciliation_owner, args.target_branch, args.require_valid)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid" if result.get("valid") else "invalid")
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
