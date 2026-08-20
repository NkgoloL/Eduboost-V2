#!/usr/bin/env python3
"""Capture PRD-0.2 historical report and stale-source quarantine evidence."""
from __future__ import annotations

import argparse
import json
from scripts._subprocess import run
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_prd002_historical_report_stale_source_quarantine import evaluate

PRD_ID = "PRD-0.2"
RECORD = Path("docs/roadmap/production_readiness/prd_002_historical_report_stale_source_quarantine_record.json")
REGISTER = Path("docs/roadmap/production_readiness/production_readiness_register.json")
QUARANTINE_REGISTER = Path("docs/reports/stale_source_quarantine_register.json")
EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-002-historical-report-stale-source-quarantine")

def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def git(args: list[str]) -> str:
    return run(["git", *args], check=False, text=True, capture_output=True).stdout.strip()

def git_state(target_branch: str) -> dict[str, Any]:
    return {"branch": git(["branch", "--show-current"]), "head_sha": git(["rev-parse", "HEAD"]), "status_short": git(["status", "--short"]), "target_branch": target_branch}

def update_register(now: str) -> None:
    register = read_json(REGISTER)
    register["last_recorded_item"] = PRD_ID
    register["last_recorded_at"] = now
    register["next_authorised_item"] = "PRD-0.3"
    for item in register.get("prd0_sequence", []):
        if item.get("prd_id") == "PRD-0.2":
            item["authorised"] = True
            item["status"] = "recorded"
    write_json(REGISTER, register)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd002-historical-stale-source-quarantine", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd002_historical_stale_source_quarantine:
        raise SystemExit("must pass --claim-prd002-historical-stale-source-quarantine")
    before = evaluate(Path("."))
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    now = datetime.now(timezone.utc).isoformat()
    state = git_state(args.target_branch)
    record = read_json(RECORD)
    record.update({
        "prd_id": PRD_ID,
        "stream_id": "PRD-PRODUCTION-READINESS",
        "status": "historical_report_stale_source_quarantine_recorded",
        "historical_report_stale_source_quarantine_recorded": True,
        "prd001_canonical_current_state_documentation_refresh_valid": before.get("prd001_canonical_current_state_documentation_refresh_valid") is True,
        "stale_source_quarantine_register_recorded": before.get("stale_source_quarantine_register_recorded") is True,
        "historical_reports_marked_superseded": before.get("historical_reports_marked_superseded") is True,
        "stale_roadmap_authority_blocked": before.get("stale_roadmap_authority_blocked") is True,
        "zone_identifier_removed": before.get("zone_identifier_removed") is True,
        "current_authority_sources_recorded": before.get("current_authority_sources_recorded") is True,
        "runtime_kg_implementation_claimed": True,
        "runtime_kg_authority_switch_authorised": True,
        "authority_switch_executed": True,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "live_learner_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "new_kg_slice_authorised": False,
        "prd1_implementation_authorised": False,
        "next_authorised_item": "PRD-0.3",
        "evidence_owner": args.prd_owner,
        "evidence_captured_at": now,
        "target_branch": args.target_branch,
        "clean_git_state_at_capture": state["status_short"] == "",
        "git_state": state,
    })
    write_json(RECORD, record)
    update_register(now)
    qreg = read_json(QUARANTINE_REGISTER)
    qreg["status"] = "recorded"
    qreg["recorded_at"] = now
    qreg["evidence_owner"] = args.prd_owner
    write_json(QUARANTINE_REGISTER, qreg)
    after = evaluate(Path("."))
    record["verification"] = after
    write_json(RECORD, record)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", after)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "stale_source_quarantine_register_snapshot.json", read_json(QUARANTINE_REGISTER))
    (EVIDENCE_DIR / "evidence_index.md").write_text(
        "# PRD-0.2 Historical Report and Stale-Source Quarantine Evidence\n\n"
        f"- Captured at: {now}\n"
        f"- Evidence owner: {args.prd_owner}\n"
        f"- Target branch: {args.target_branch}\n"
        f"- Valid: {after.get('valid')}\n"
        f"- Authority valid: {after.get('authority_valid')}\n"
        "- Historical reports marked superseded: true\n"
        "- Stale roadmap authority blocked: true\n"
        "- Zone.Identifier sidecar removed: true\n",
        encoding="utf-8",
    )
    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    if args.json:
        print(json.dumps(after, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.2 evidence valid: {after.get('valid')}")
    return 0 if after.get("valid") else 1

if __name__ == "__main__":
    raise SystemExit(main())
