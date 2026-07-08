#!/usr/bin/env python3
"""Capture PRD-0.7 OpenAPI/generated artifact canonicalisation evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from scripts.production_readiness.apply_prd007_openapi_generated_artifact_canonicalisation import canonicalise
from scripts.production_readiness.audit_prd007_openapi_generated_artifact_canonicalisation import (
    GENERATED_ARTIFACT_INVENTORY,
    PRD_ID,
    RECORD,
    REGISTER,
    generated_artifact_inventory,
    read_json,
)
from scripts.roadmap_reconciliation.verify_prd007_openapi_generated_artifact_canonicalisation import evaluate

EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-007-openapi-generated-artifact-canonicalisation")


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
    register["next_authorised_item"] = "PRD-0.8"
    for item in register.get("prd0_sequence", []):
        if item.get("prd_id") == PRD_ID:
            item["authorised"] = True
            item["status"] = "recorded"
    write_json(REGISTER, register)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd007-openapi-generated-artifact-canonicalisation", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd007_openapi_generated_artifact_canonicalisation:
        raise SystemExit("must pass --claim-prd007-openapi-generated-artifact-canonicalisation")
    before = evaluate(Path("."))
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    state = git_state(args.target_branch)
    now = datetime.now(timezone.utc).isoformat()
    canonicalise(Path("."), write=True)
    inventory = generated_artifact_inventory(Path("."), captured_at=now)
    write_json(GENERATED_ARTIFACT_INVENTORY, inventory)
    record = read_json(RECORD)
    record.update({
        "prd_id": PRD_ID,
        "stream_id": "PRD-PRODUCTION-READINESS",
        "status": "openapi_generated_artifact_canonicalisation_recorded",
        "openapi_generated_artifact_canonicalisation_recorded": True,
        "prd006_workflow_command_hygiene_ci_inventory_valid": before.get("prd006_workflow_command_hygiene_ci_inventory_valid") is True,
        "canonical_openapi_path": inventory.get("canonical_openapi_path"),
        "root_openapi_json_path": inventory.get("root_openapi_json_path"),
        "root_openapi_yaml_path": inventory.get("root_openapi_yaml_path"),
        "canonical_openapi_sha256": inventory.get("canonical_openapi_sha256"),
        "root_openapi_json_sha256": inventory.get("root_openapi_json_sha256"),
        "root_openapi_yaml_sha256": inventory.get("root_openapi_yaml_sha256"),
        "generated_artifact_inventory_recorded": True,
        "generated_artifact_count": inventory.get("generated_artifact_count"),
        "historical_openapi_snapshot_count": inventory.get("historical_openapi_snapshot_count"),
        "root_json_matches_canonical": inventory.get("root_json_matches_canonical") is True,
        "root_yaml_schema_matches_canonical": inventory.get("root_yaml_schema_matches_canonical") is True,
        "openapi_path_count": inventory.get("openapi_path_count"),
        "openapi_operation_count": inventory.get("openapi_operation_count"),
        "openapi_mirrors_canonicalised": inventory.get("root_json_matches_canonical") is True and inventory.get("root_yaml_schema_matches_canonical") is True,
        "canonical_openapi_source_of_truth_recorded": True,
        "root_openapi_json_mirror_recorded": True,
        "root_openapi_yaml_mirror_recorded": True,
        "historical_openapi_snapshots_retained": True,
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
        "next_authorised_item": "PRD-0.8",
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
    write_json(EVIDENCE_DIR / "generated_artifact_canonicalisation_inventory_snapshot.json", inventory)
    (EVIDENCE_DIR / "evidence_index.md").write_text(
        "# PRD-0.7 OpenAPI and Generated Artifact Canonicalisation Evidence\n\n"
        f"- Captured at: {now}\n"
        f"- Evidence owner: {args.prd_owner}\n"
        f"- Target branch: {args.target_branch}\n"
        f"- Valid: {after.get('valid')}\n"
        f"- Authority valid: {after.get('authority_valid')}\n"
        f"- Canonical OpenAPI path: {inventory.get('canonical_openapi_path')}\n"
        f"- Root JSON mirror matches canonical: {inventory.get('root_json_matches_canonical')}\n"
        f"- Root YAML mirror schema matches canonical: {inventory.get('root_yaml_schema_matches_canonical')}\n"
        f"- OpenAPI paths: {inventory.get('openapi_path_count')}\n"
        f"- OpenAPI operations: {inventory.get('openapi_operation_count')}\n"
        f"- Generated artifacts inventoried: {inventory.get('generated_artifact_count')}\n"
        f"- Historical OpenAPI snapshots retained: {inventory.get('historical_openapi_snapshot_count')}\n"
        "- Branch/release naming reconciliation deferred to PRD-0.8\n",
        encoding="utf-8",
    )
    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    if args.json:
        print(json.dumps(after, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.7 evidence valid: {after.get('valid')}")
    return 0 if after.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
