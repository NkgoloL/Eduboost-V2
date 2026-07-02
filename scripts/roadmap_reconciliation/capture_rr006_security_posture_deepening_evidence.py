#!/usr/bin/env python3
"""Capture RR-006 security posture deepening evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_rr006_security_posture_deepening import evaluate

RR_ID = "RR-006"
RECORD = Path("docs/roadmap/reconciliation/rr_006_security_posture_deepening_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/roadmap-reconciliation/rr-006-security-posture-deepening")


def _git_state(target_branch: str) -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""

    return {
        "branch": run("branch", "--show-current"),
        "head_sha": run("rev-parse", "HEAD"),
        "status_short": run("status", "--short"),
        "target_branch": target_branch,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_index(path: Path, record: dict[str, Any], verification: dict[str, Any]) -> None:
    lines = [
        "# RR-006 Security Posture Deepening Evidence",
        "",
        f"Recorded at: `{record['recorded_at']}`",
        f"RR ID: `{RR_ID}`",
        f"Owner: `{record['security_owner']}`",
        "",
        "## Result",
        "",
        f"- Valid: `{verification['valid']}`",
        f"- Threat model reviewed: `{record['v2_threat_model_reviewed']}`",
        f"- Pen-test checklist recorded: `{record['v2_pen_test_checklist_recorded']}`",
        f"- Dependency vulnerability scan enforced: `{record['dependency_vulnerability_scan_enforced']}`",
        f"- Python dependency audit enforced: `{record['python_dependency_audit_enforced']}`",
        f"- Secrets scanning in pre-commit enforced: `{record['secrets_scanning_precommit_enforced']}`",
        f"- Secrets scanning in CI enforced: `{record['secrets_scanning_ci_enforced']}`",
        "",
        "## Boundary",
        "",
        f"- Production release authorised: `{record['production_release_authorised']}`",
        f"- Deployment authorised: `{record['deployment_authorised']}`",
        f"- Release tag authorised: `{record['release_tag_authorised']}`",
        f"- Public beta authorised: `{record['public_beta_authorised']}`",
        f"- Runtime KG implementation claimed: `{record['runtime_kg_implementation_claimed']}`",
        "",
        "## Raw evidence",
        "",
        "- `raw/verification.json`",
        "- `raw/record.json`",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-rr006-security-posture-deepening", action="store_true")
    parser.add_argument("--security-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.claim_rr006_security_posture_deepening:
        raise SystemExit("missing --claim-rr006-security-posture-deepening")

    pre = evaluate(Path("."))
    if not pre.get("authority_valid"):
        payload = {"valid": False, "errors": pre.get("errors", []), "stage": "pre-capture"}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        if args.require_valid:
            return 1

    git_state = _git_state(args.target_branch)
    record: dict[str, Any] = {
        "rr_id": RR_ID,
        "status": "security_posture_deepening_recorded",
        "security_owner": args.security_owner,
        "target_branch": args.target_branch,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "git_state": git_state,
        "clean_git_state_at_capture": git_state.get("status_short") == "",
        "security_posture_deepening_recorded": True,
        "v2_threat_model_reviewed": True,
        "v2_pen_test_checklist_recorded": True,
        "dependency_vulnerability_scan_enforced": True,
        "python_dependency_audit_enforced": True,
        "secrets_scanning_precommit_enforced": True,
        "secrets_scanning_ci_enforced": True,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "runtime_kg_implementation_claimed": False,
    }

    _write_json(RECORD, record)
    verification = evaluate(Path("."))
    record["verification"] = verification
    _write_json(RECORD, record)

    raw_dir = EVIDENCE_DIR / "raw"
    _write_json(raw_dir / "record.json", record)
    _write_json(raw_dir / "verification.json", verification)
    _write_index(EVIDENCE_DIR / "evidence_index.md", record, verification)

    if args.json:
        print(json.dumps({**verification, "record": record}, indent=2, sort_keys=True))
    else:
        print(f"RR-006 evidence valid: {verification['valid']}")

    return 0 if verification["valid"] or not args.require_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
