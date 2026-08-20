#!/usr/bin/env python3
"""Capture PRD-0.3 documentation housekeeping ratchet refresh evidence."""
from __future__ import annotations

import argparse
import json
from scripts._subprocess import run
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_prd003_documentation_housekeeping_ratchet_refresh import evaluate

PRD_ID = "PRD-0.3"
RECORD = Path("docs/roadmap/production_readiness/prd_003_documentation_housekeeping_ratchet_refresh_record.json")
REGISTER = Path("docs/roadmap/production_readiness/production_readiness_register.json")
INVENTORY_JSON = Path("docs/generated/documentation_inventory.json")
FINDINGS_CSV = Path("docs/generated/documentation_findings.csv")
RATCHET_BASELINE = Path("docs/documentation/housekeeping_ratchet_baseline.json")
EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-003-documentation-housekeeping-ratchet-refresh")
BASELINE_NOTE = "PRD-0.3 baseline captured after post-closure documentation authority refresh."


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git(args: list[str]) -> str:
    return run(["git", *args], check=False, text=True, capture_output=True).stdout.strip()


def git_state(target_branch: str) -> dict[str, Any]:
    return {
        "branch": git(["branch", "--show-current"]),
        "head_sha": git(["rev-parse", "HEAD"]),
        "status_short": git(["status", "--short"]),
        "target_branch": target_branch,
    }


def run_checked(cmd: list[str]) -> None:
    completed = run(cmd, check=False, text=True, capture_output=True)
    if completed.returncode != 0:
        detail = completed.stdout + completed.stderr
        raise SystemExit(f"command failed ({completed.returncode}): {' '.join(cmd)}\n{detail}")


def update_register(now: str) -> None:
    register = read_json(REGISTER)
    register["last_recorded_item"] = PRD_ID
    register["last_recorded_at"] = now
    register["next_authorised_item"] = "PRD-0.4"
    for item in register.get("prd0_sequence", []):
        if item.get("prd_id") == PRD_ID:
            item["authorised"] = True
            item["status"] = "recorded"
    write_json(REGISTER, register)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd003-doc-housekeeping-ratchet-refresh", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd003_doc_housekeeping_ratchet_refresh:
        raise SystemExit("must pass --claim-prd003-doc-housekeeping-ratchet-refresh")

    before = evaluate(Path("."))
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    state = git_state(args.target_branch)
    now = datetime.now(timezone.utc).isoformat()

    run_checked([sys.executable, "scripts/maintenance/check_doc_inventory_reproducible.py", "--root", ".", "--update"])
    run_checked([sys.executable, "scripts/maintenance/update_doc_housekeeping_baseline.py", "--root", ".", "--note", BASELINE_NOTE])
    run_checked([sys.executable, "scripts/maintenance/check_doc_housekeeping_ratchet.py", "--root", "."])

    inventory = read_json(INVENTORY_JSON)
    inventory_summary = inventory.get("summary", {})
    baseline = read_json(RATCHET_BASELINE)

    record = read_json(RECORD)
    record.update({
        "prd_id": PRD_ID,
        "stream_id": "PRD-PRODUCTION-READINESS",
        "status": "documentation_housekeeping_ratchet_refresh_recorded",
        "documentation_housekeeping_ratchet_refresh_recorded": True,
        "prd002_historical_report_stale_source_quarantine_valid": before.get("prd002_historical_report_stale_source_quarantine_valid") is True,
        "documentation_inventory_regenerated": True,
        "documentation_findings_regenerated": FINDINGS_CSV.exists(),
        "housekeeping_ratchet_baseline_refreshed": True,
        "documentation_housekeeping_ratchet_check_passed": True,
        "documentation_inventory_summary_recorded": True,
        "inventory_summary": inventory_summary,
        "housekeeping_ratchet_baseline_summary": {
            "schema_version": baseline.get("schema_version"),
            "baseline_source": baseline.get("baseline_source"),
            "note": baseline.get("note"),
            "max_summary": baseline.get("max_summary", {}),
            "min_summary": baseline.get("min_summary", {}),
            "max_findings_by_type": baseline.get("max_findings_by_type", {}),
            "strict_zero_new_finding_types": baseline.get("strict_zero_new_finding_types"),
        },
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
        "next_authorised_item": "PRD-0.4",
        "evidence_owner": args.prd_owner,
        "evidence_captured_at": now,
        "target_branch": args.target_branch,
        "clean_git_state_at_capture": state["status_short"] == "",
        "git_state": state,
    })
    update_register(now)
    write_json(RECORD, record)
    after = evaluate(Path("."))
    record["verification"] = after
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", after)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "documentation_inventory_summary_snapshot.json", inventory_summary)
    write_json(EVIDENCE_DIR / "housekeeping_ratchet_baseline_snapshot.json", baseline)
    (EVIDENCE_DIR / "evidence_index.md").write_text(
        "# PRD-0.3 Documentation Housekeeping Ratchet Refresh Evidence\n\n"
        f"- Captured at: {now}\n"
        f"- Evidence owner: {args.prd_owner}\n"
        f"- Target branch: {args.target_branch}\n"
        f"- Valid: {after.get('valid')}\n"
        f"- Authority valid: {after.get('authority_valid')}\n"
        f"- Markdown files: {inventory_summary.get('markdown_files')}\n"
        f"- Finding count: {inventory_summary.get('finding_count')}\n"
        "- Documentation inventory regenerated: true\n"
        "- Documentation findings regenerated: true\n"
        "- Housekeeping ratchet baseline refreshed: true\n"
        "- Documentation housekeeping ratchet check passed: true\n",
        encoding="utf-8",
    )

    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    if args.json:
        print(json.dumps(after, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.3 evidence valid: {after.get('valid')}")
    return 0 if after.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
