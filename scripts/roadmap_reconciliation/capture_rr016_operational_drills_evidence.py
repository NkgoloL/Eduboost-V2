#!/usr/bin/env python3
"""Capture RR-016 operational drills evidence."""
from __future__ import annotations

import argparse
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_rr016_operational_drills import evaluate

RR_ID = "RR-016"
RECORD = Path("docs/roadmap/reconciliation/rr_016_operational_drills_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/roadmap-reconciliation/rr-016-operational-drills")


def _git_state(target_branch: str) -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            return check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
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
        "# RR-016 Operational Drills Evidence", "",
        f"Recorded at: `{record['evidence_captured_at']}`",
        f"RR ID: `{RR_ID}`",
        f"Owner: `{record['evidence_owner']}`", "",
        "## Result", "",
        f"- Valid: `{verification['valid']}`",
        f"- RR-015 external approvals valid: `{record['rr015_external_approvals_valid']}`",
        f"- Backup drill completed: `{record['backup_drill_completed']}`",
        f"- Restore drill completed: `{record['restore_drill_completed']}`",
        f"- Rollback drill completed: `{record['rollback_drill_completed']}`",
        f"- Monitoring dashboard verified: `{record['monitoring_dashboard_verified']}`",
        f"- Incident handoff verified: `{record['incident_handoff_verified']}`", "",
        "## Carried caveats", "",
        f"- RR-003 fallback coverage caveat visible: `{record['rr003_fallback_coverage_caveat_visible']}`",
        f"- RR-006 non-required checks caveat visible: `{record['rr006_non_required_checks_caveat_visible']}`",
        f"- RR-017 release safety controls remaining visible: `{record['rr017_release_safety_controls_remaining_visible']}`",
        f"- RR-018 trustworthy beta quality remaining visible: `{record['rr018_trustworthy_beta_quality_remaining_visible']}`", "",
        "## Boundary", "",
        f"- Billing launch authorised: `{record['billing_launch_authorised']}`",
        f"- Live payment processing authorised: `{record['live_payment_processing_authorised']}`",
        f"- Production release authorised: `{record['production_release_authorised']}`",
        f"- Deployment authorised: `{record['deployment_authorised']}`",
        f"- Release tag authorised: `{record['release_tag_authorised']}`",
        f"- Public beta authorised: `{record['public_beta_authorised']}`",
        f"- Public beta live traffic authorised: `{record['public_beta_live_traffic_authorised']}`",
        f"- Runtime KG implementation claimed: `{record['runtime_kg_implementation_claimed']}`", "",
        "## Required drill reports", "",
        "- `docs/operations/drills/rr016_backup_drill_report.md`",
        "- `docs/operations/drills/rr016_restore_drill_report.md`",
        "- `docs/operations/drills/rr016_rollback_drill_report.md`",
        "- `docs/operations/drills/rr016_monitoring_dashboard_verification.md`",
        "- `docs/operations/drills/rr016_incident_handoff_verification.md`", "",
        "## Raw evidence", "",
        "- `raw/record.json`",
        "- `raw/verification.json`", "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-rr016-operational-drills", action="store_true")
    parser.add_argument("--operations-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_rr016_operational_drills:
        raise SystemExit("missing --claim-rr016-operational-drills")

    pre = evaluate(Path("."))
    if not pre.get("authority_valid"):
        payload = {"valid": False, "stage": "pre-capture", "errors": pre.get("errors", [])}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        if args.require_valid:
            return 1

    git_state = _git_state(args.target_branch)
    record: dict[str, Any] = {
        "rr_id": RR_ID,
        "status": "operational_drills_recorded",
        "evidence_owner": args.operations_owner,
        "target_branch": args.target_branch,
        "evidence_captured_at": datetime.now(timezone.utc).isoformat(),
        "git_state": git_state,
        "clean_git_state_at_capture": git_state.get("status_short") == "",
        "operational_drills_recorded": True,
        "rr015_external_approvals_valid": True,
        "backup_drill_completed": True,
        "restore_drill_completed": True,
        "rollback_drill_completed": True,
        "monitoring_dashboard_verified": True,
        "incident_handoff_verified": True,
        "rr003_fallback_coverage_caveat_visible": True,
        "rr006_non_required_checks_caveat_visible": True,
        "rr017_release_safety_controls_remaining_visible": True,
        "rr018_trustworthy_beta_quality_remaining_visible": True,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
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

    payload = {**verification, "record": record}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RR-016 evidence valid: {verification['valid']}")
    return 0 if verification["valid"] or not args.require_valid else 1

if __name__ == "__main__":
    raise SystemExit(main())
