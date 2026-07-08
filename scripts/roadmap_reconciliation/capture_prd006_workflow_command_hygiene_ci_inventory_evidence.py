#!/usr/bin/env python3
"""Capture PRD-0.6 workflow command hygiene and CI inventory evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from scripts.production_readiness.audit_prd006_workflow_command_hygiene_ci_inventory import (
    PRD_ID,
    RECORD,
    REGISTER,
    WORKFLOW_INVENTORY,
    read_json,
    workflow_inventory,
)
from scripts.roadmap_reconciliation.verify_prd006_workflow_command_hygiene_ci_inventory import evaluate

EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-006-workflow-command-hygiene-ci-inventory")


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
    register["next_authorised_item"] = "PRD-0.7"
    for item in register.get("prd0_sequence", []):
        if item.get("prd_id") == PRD_ID:
            item["authorised"] = True
            item["status"] = "recorded"
    write_json(REGISTER, register)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd006-workflow-command-hygiene-ci-inventory", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd006_workflow_command_hygiene_ci_inventory:
        raise SystemExit("must pass --claim-prd006-workflow-command-hygiene-ci-inventory")
    before = evaluate(Path("."))
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    state = git_state(args.target_branch)
    now = datetime.now(timezone.utc).isoformat()
    inventory = workflow_inventory(Path("."), captured_at=now)
    write_json(WORKFLOW_INVENTORY, inventory)
    record = read_json(RECORD)
    record.update({
        "prd_id": PRD_ID,
        "stream_id": "PRD-PRODUCTION-READINESS",
        "status": "workflow_command_hygiene_ci_inventory_recorded",
        "workflow_command_hygiene_ci_inventory_recorded": True,
        "prd005_test_failure_collection_stabilisation_register_valid": before.get("prd005_test_failure_collection_stabilisation_register_valid") is True,
        "workflow_inventory_recorded": True,
        "ci_workflow_inventory_recorded": True,
        "workflow_count": inventory.get("workflow_count"),
        "pytest_workflow_count": inventory.get("pytest_workflow_count"),
        "direct_pytest_command_count": inventory.get("direct_pytest_command_count"),
        "direct_pytest_workflow_count": inventory.get("direct_pytest_workflow_count"),
        "module_pytest_command_count": inventory.get("module_pytest_command_count"),
        "module_pytest_workflow_count": inventory.get("module_pytest_workflow_count"),
        "requirements_dev_install_workflow_count": inventory.get("requirements_dev_install_workflow_count"),
        "pytest_workflow_missing_dev_install_count": inventory.get("pytest_workflow_missing_dev_install_count"),
        "direct_pytest_commands_resolved": inventory.get("direct_pytest_command_count") == 0,
        "canonical_pytest_command_recorded": True,
        "ci_dependency_install_inventory_recorded": True,
        "workflow_command_hygiene_policy_recorded": True,
        "openapi_generated_artifact_canonicalisation_deferred_to_prd007": True,
        "branch_release_naming_reconciliation_deferred_to_prd008": True,
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
        "next_authorised_item": "PRD-0.7",
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
    write_json(EVIDENCE_DIR / "workflow_command_hygiene_ci_inventory_snapshot.json", inventory)
    (EVIDENCE_DIR / "evidence_index.md").write_text(
        "# PRD-0.6 Workflow Command Hygiene and CI Inventory Evidence\n\n"
        f"- Captured at: {now}\n"
        f"- Evidence owner: {args.prd_owner}\n"
        f"- Target branch: {args.target_branch}\n"
        f"- Valid: {after.get('valid')}\n"
        f"- Authority valid: {after.get('authority_valid')}\n"
        f"- Workflows: {inventory.get('workflow_count')}\n"
        f"- Direct pytest commands remaining: {inventory.get('direct_pytest_command_count')}\n"
        f"- Module pytest commands: {inventory.get('module_pytest_command_count')}\n"
        f"- Pytest workflows missing requirements/dev.txt install: {inventory.get('pytest_workflow_missing_dev_install_count')}\n"
        "- OpenAPI/generated artifact canonicalisation deferred to PRD-0.7\n"
        "- Branch/release naming reconciliation deferred to PRD-0.8\n",
        encoding="utf-8",
    )
    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    if args.json:
        print(json.dumps(after, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.6 evidence valid: {after.get('valid')}")
    return 0 if after.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
