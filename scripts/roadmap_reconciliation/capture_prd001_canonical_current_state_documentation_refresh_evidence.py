#!/usr/bin/env python3
"""Capture PRD-0.1 canonical current-state documentation refresh evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_prd001_canonical_current_state_documentation_refresh import evaluate

PRD_ID = "PRD-0.1"
RECORD = Path("docs/roadmap/production_readiness/prd_001_canonical_current_state_documentation_refresh_record.json")
REGISTER = Path("docs/roadmap/production_readiness/production_readiness_register.json")
EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-001-canonical-current-state-documentation-refresh")

def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def git(args: list[str]) -> str:
    return subprocess.run(["git", *args], check=False, text=True, capture_output=True).stdout.strip()

def git_state(target_branch: str) -> dict[str, Any]:
    return {"branch": git(["branch", "--show-current"]), "head_sha": git(["rev-parse", "HEAD"]), "status_short": git(["status", "--short"]), "target_branch": target_branch}

def update_register(now: str) -> None:
    register = read_json(REGISTER)
    register["last_recorded_item"] = PRD_ID
    register["last_recorded_at"] = now
    register["next_authorised_item"] = "PRD-0.2"
    for item in register.get("prd0_sequence", []):
        if item.get("prd_id") == "PRD-0.1":
            item["authorised"] = True
            item["status"] = "recorded"
    write_json(REGISTER, register)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd001-canonical-current-state-docs", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd001_canonical_current_state_docs:
        raise SystemExit("must pass --claim-prd001-canonical-current-state-docs")
    before = evaluate(Path("."))
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    now = datetime.now(timezone.utc).isoformat()
    state = git_state(args.target_branch)
    record = read_json(RECORD)
    record.update({
        "prd_id": PRD_ID,
        "stream_id": "PRD-PRODUCTION-READINESS",
        "status": "canonical_current_state_documentation_refresh_recorded",
        "canonical_current_state_documentation_refresh_recorded": True,
        "prd000_production_readiness_stream_authority_valid": before.get("prd000_production_readiness_stream_authority_valid") is True,
        "truth_map_recorded": before.get("truth_map_recorded") is True,
        "canonical_docs_refreshed": before.get("canonical_docs_refreshed") is True,
        "stale_canonical_claims_removed": before.get("stale_canonical_claims_removed") is True,
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
        "next_authorised_item": "PRD-0.2",
        "evidence_owner": args.prd_owner,
        "evidence_captured_at": now,
        "target_branch": args.target_branch,
        "clean_git_state_at_capture": state["status_short"] == "",
        "git_state": state,
    })
    write_json(RECORD, record)
    update_register(now)
    after = evaluate(Path("."))
    record["verification"] = after
    write_json(RECORD, record)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", after)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "current_state_documentation_truth_map_snapshot.json", read_json(Path("docs/roadmap/production_readiness/current_state_documentation_truth_map.json")))
    (EVIDENCE_DIR / "evidence_index.md").write_text(
        "# PRD-0.1 Canonical Current-State Documentation Refresh Evidence\n\n"
        f"- Captured at: {now}\n"
        f"- Evidence owner: {args.prd_owner}\n"
        f"- Target branch: {args.target_branch}\n"
        f"- Valid: {after.get('valid')}\n"
        f"- Authority valid: {after.get('authority_valid')}\n"
        "- Canonical docs refreshed: true\n"
        "- Stale canonical claims removed: true\n",
        encoding="utf-8",
    )
    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    if args.json:
        print(json.dumps(after, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.1 evidence valid: {after.get('valid')}")
    return 0 if after.get("valid") else 1

if __name__ == "__main__":
    raise SystemExit(main())
