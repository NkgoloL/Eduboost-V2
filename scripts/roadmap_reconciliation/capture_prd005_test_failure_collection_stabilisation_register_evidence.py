#!/usr/bin/env python3
"""Capture PRD-0.5 test failure and collection stabilisation evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from scripts.production_readiness.audit_prd005_test_failure_collection_stabilisation_register import (
    RECORD,
    REGISTER,
    STABILISATION_REGISTER,
    PRD_ID,
    build_stabilisation_register,
    read_json,
)
from scripts.roadmap_reconciliation.verify_prd005_test_failure_collection_stabilisation_register import evaluate

EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-005-test-failure-collection-stabilisation-register")


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
    register["next_authorised_item"] = "PRD-0.6"
    for item in register.get("prd0_sequence", []):
        if item.get("prd_id") == PRD_ID:
            item["authorised"] = True
            item["status"] = "recorded"
    write_json(REGISTER, register)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd005-test-failure-collection-stabilisation-register", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd005_test_failure_collection_stabilisation_register:
        raise SystemExit("must pass --claim-prd005-test-failure-collection-stabilisation-register")
    before = evaluate(Path("."))
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    state = git_state(args.target_branch)
    now = datetime.now(timezone.utc).isoformat()
    stabilisation = build_stabilisation_register(Path("."), captured_at=now)
    write_json(STABILISATION_REGISTER, stabilisation)
    record = read_json(RECORD)
    record.update({
        "prd_id": PRD_ID,
        "stream_id": "PRD-PRODUCTION-READINESS",
        "status": "test_failure_collection_stabilisation_register_recorded",
        "test_failure_collection_stabilisation_register_recorded": True,
        "prd004_test_dependency_bootstrap_baseline_valid": before.get("prd004_test_dependency_bootstrap_baseline_valid") is True,
        "test_inventory_recorded": True,
        "collection_command_matrix_recorded": True,
        "failure_classification_schema_recorded": True,
        "triage_register_recorded": True,
        "test_file_count": stabilisation.get("test_inventory", {}).get("test_file_count"),
        "test_function_count": stabilisation.get("test_inventory", {}).get("test_function_count"),
        "python_parse_error_count": stabilisation.get("test_inventory", {}).get("python_parse_error_count"),
        "collection_command_count": len(stabilisation.get("collection_command_matrix", [])),
        "triage_item_count": len(stabilisation.get("triage_register", [])),
        "failure_classification_category_count": len(stabilisation.get("failure_classification_schema", [])),
        "no_test_deletions_authorised": True,
        "no_silent_xfail_authorised": True,
        "no_product_behavior_repairs_authorised": True,
        "workflow_hygiene_deferred_to_prd006": True,
        "openapi_generated_artifact_canonicalisation_deferred_to_prd007": True,
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
        "next_authorised_item": "PRD-0.6",
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
    write_json(EVIDENCE_DIR / "test_failure_collection_stabilisation_register_snapshot.json", stabilisation)
    (EVIDENCE_DIR / "evidence_index.md").write_text(
        "# PRD-0.5 Test Failure and Collection Stabilisation Register Evidence\n\n"
        f"- Captured at: {now}\n"
        f"- Evidence owner: {args.prd_owner}\n"
        f"- Target branch: {args.target_branch}\n"
        f"- Valid: {after.get('valid')}\n"
        f"- Authority valid: {after.get('authority_valid')}\n"
        f"- Test files: {record.get('test_file_count')}\n"
        f"- Test functions: {record.get('test_function_count')}\n"
        f"- Collection commands: {record.get('collection_command_count')}\n"
        f"- Triage items: {record.get('triage_item_count')}\n"
        "- No test deletion authorised: true\n"
        "- Workflow command hygiene deferred to PRD-0.6\n"
        "- OpenAPI/generated artifact canonicalisation deferred to PRD-0.7\n",
        encoding="utf-8",
    )
    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    if args.json:
        print(json.dumps(after, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.5 evidence valid: {after.get('valid')}")
    return 0 if after.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
