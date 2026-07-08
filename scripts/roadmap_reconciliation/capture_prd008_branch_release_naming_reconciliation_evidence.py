#!/usr/bin/env python3
"""Capture PRD-0.8 branch/release naming reconciliation evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from scripts.production_readiness.apply_prd008_branch_release_naming_reconciliation import apply as apply_reconciliation
from scripts.production_readiness.audit_prd008_branch_release_naming_reconciliation import (
    INVENTORY,
    PRD_ID,
    RECORD,
    REGISTER,
    branch_release_inventory,
    read_json,
)
from scripts.roadmap_reconciliation.verify_prd008_branch_release_naming_reconciliation import evaluate

EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-008-branch-release-naming-reconciliation")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_state(target_branch: str) -> dict:
    def run(args: list[str]) -> str:
        return subprocess.check_output(args, text=True).strip()
    return {
        "branch": run(["git", "branch", "--show-current"]),
        "head_sha": run(["git", "rev-parse", "HEAD"]),
        "status_short": subprocess.check_output(["git", "status", "--short"], text=True),
        "target_branch": target_branch,
    }


def update_register(now: str) -> None:
    register = read_json(REGISTER)
    register["last_recorded_item"] = PRD_ID
    register["last_recorded_at"] = now
    register["next_authorised_item"] = "PRD-0.9"
    for item in register.get("prd0_sequence", []):
        if item.get("prd_id") == PRD_ID:
            item["authorised"] = True
            item["status"] = "recorded"
    write_json(REGISTER, register)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd008-branch-release-naming-reconciliation", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd008_branch_release_naming_reconciliation:
        raise SystemExit("must pass --claim-prd008-branch-release-naming-reconciliation")
    before = evaluate(Path("."))
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    state = git_state(args.target_branch)
    now = datetime.now(timezone.utc).isoformat()
    apply_reconciliation(Path("."), write=True)
    inventory = branch_release_inventory(Path("."), captured_at=now)
    write_json(INVENTORY, inventory)
    record = read_json(RECORD)
    record.update({
        "prd_id": PRD_ID,
        "stream_id": "PRD-PRODUCTION-READINESS",
        "status": "branch_release_naming_reconciliation_recorded",
        "branch_release_naming_reconciliation_recorded": True,
        "prd007_openapi_generated_artifact_canonicalisation_valid": before.get("prd007_openapi_generated_artifact_canonicalisation_valid") is True,
        "canonical_trunk_branch_recorded": True,
        "canonical_trunk_branch": inventory.get("canonical_trunk_branch"),
        "legacy_main_alias_policy_recorded": True,
        "legacy_main_alias_policy": inventory.get("legacy_main_alias_policy"),
        "release_branch_pattern_recorded": True,
        "release_branch_pattern": inventory.get("release_branch_pattern"),
        "prd_authority_branch_pattern_recorded": True,
        "prd_authority_branch_pattern": inventory.get("prd_authority_branch_pattern"),
        "prd_evidence_branch_pattern_recorded": True,
        "prd_evidence_branch_pattern": inventory.get("prd_evidence_branch_pattern"),
        "branching_policy_document_refreshed": inventory.get("branching_policy_document_refreshed") is True,
        "branch_release_inventory_recorded": True,
        "workflow_count": inventory.get("workflow_count"),
        "master_workflow_count": inventory.get("workflow_branch_reference_summary", {}).get("master_workflow_count"),
        "main_workflow_count": inventory.get("workflow_branch_reference_summary", {}).get("main_workflow_count"),
        "release_branch_workflow_count": inventory.get("workflow_branch_reference_summary", {}).get("release_branch_workflow_count"),
        "release_event_workflow_count": inventory.get("release_event_workflow_count"),
        "deployment_reference_workflow_count": inventory.get("deployment_reference_workflow_count"),
        "release_tag_boundary_recorded": True,
        "production_release_boundary_recorded": True,
        "deployment_boundary_recorded": True,
        "no_release_authority_granted": True,
        "repository_hygiene_deferred_to_prd009": True,
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
        "next_authorised_item": "PRD-0.9",
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
    write_json(EVIDENCE_DIR / "branch_release_naming_reconciliation_inventory_snapshot.json", inventory)
    (EVIDENCE_DIR / "evidence_index.md").write_text(
        "# PRD-0.8 Branch/Release Naming Reconciliation Evidence\n\n"
        f"- Captured at: {now}\n"
        f"- Evidence owner: {args.prd_owner}\n"
        f"- Target branch: {args.target_branch}\n"
        f"- Valid: {after.get('valid')}\n"
        f"- Authority valid: {after.get('authority_valid')}\n"
        f"- Canonical trunk branch: {inventory.get('canonical_trunk_branch')}\n"
        f"- Legacy main alias policy: {inventory.get('legacy_main_alias_policy')}\n"
        f"- Release branch pattern: {inventory.get('release_branch_pattern')}\n"
        f"- Workflow count: {inventory.get('workflow_count')}\n"
        f"- Workflows referencing master: {inventory.get('workflow_branch_reference_summary', {}).get('master_workflow_count')}\n"
        f"- Workflows referencing main: {inventory.get('workflow_branch_reference_summary', {}).get('main_workflow_count')}\n"
        f"- Workflows referencing release branches: {inventory.get('workflow_branch_reference_summary', {}).get('release_branch_workflow_count')}\n"
        f"- Release-event workflows: {inventory.get('release_event_workflow_count')}\n"
        f"- Deployment-reference workflows: {inventory.get('deployment_reference_workflow_count')}\n"
        "- Repository hygiene deferred to PRD-0.9\n",
        encoding="utf-8",
    )
    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    if args.json:
        print(json.dumps(after, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.8 evidence valid: {after.get('valid')}")
    return 0 if after.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
