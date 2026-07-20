#!/usr/bin/env python3
"""Capture PRD-0.9 repository hygiene and generated/local artifact audit evidence."""
from __future__ import annotations

import argparse
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path

from scripts.production_readiness.apply_prd009_repository_hygiene_generated_local_artifact_audit import apply as apply_hygiene_policy
from scripts.production_readiness.audit_prd009_repository_hygiene_generated_local_artifact_audit import (
    INVENTORY,
    PRD_ID,
    RECORD,
    REGISTER,
    read_json,
    repository_hygiene_inventory,
    write_json,
)
from scripts.roadmap_reconciliation.verify_prd009_repository_hygiene_generated_local_artifact_audit import evaluate

EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-009-repository-hygiene-generated-local-artifact-audit")


def git_state(target_branch: str) -> dict:
    def run(args: list[str]) -> str | None:
        try:
            return check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    status = run(["git", "status", "--short"])
    return {
        "branch": run(["git", "branch", "--show-current"]),
        "head_sha": run(["git", "rev-parse", "HEAD"]),
        "status_short": status,
        "target_branch": target_branch,
        "git_available": status is not None,
    }


def update_register(now: str) -> None:
    register = read_json(REGISTER)
    register["last_recorded_item"] = PRD_ID
    register["last_recorded_at"] = now
    register["next_authorised_item"] = "PRD-0.10"
    for item in register.get("prd0_sequence", []):
        if item.get("prd_id") == PRD_ID:
            item["authorised"] = True
            item["status"] = "recorded"
    write_json(REGISTER, register)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd009-repository-hygiene-generated-local-artifact-audit", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd009_repository_hygiene_generated_local_artifact_audit:
        raise SystemExit("must pass --claim-prd009-repository-hygiene-generated-local-artifact-audit")

    before = evaluate(Path("."))
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    state = git_state(args.target_branch)
    now = datetime.now(timezone.utc).isoformat()
    apply_hygiene_policy(Path("."), write=True)
    inventory = repository_hygiene_inventory(Path("."), captured_at=now)
    write_json(INVENTORY, inventory)

    summary = inventory.get("summary", {})
    record = read_json(RECORD)
    record.update({
        "prd_id": PRD_ID,
        "stream_id": "PRD-PRODUCTION-READINESS",
        "status": "repository_hygiene_generated_local_artifact_audit_recorded",
        "repository_hygiene_generated_local_artifact_audit_recorded": True,
        "prd008_branch_release_naming_reconciliation_valid": before.get("prd008_branch_release_naming_reconciliation_valid") is True,
        "repository_hygiene_policy_document_refreshed": inventory.get("repository_hygiene_policy_document_refreshed") is True,
        "generated_local_artifact_inventory_recorded": True,
        "suspicious_top_level_entries_inventory_required": True,
        "cleanup_recommendation_recorded": True,
        "configured_generated_local_path_count": summary.get("configured_generated_local_path_count"),
        "present_generated_local_path_count": summary.get("present_generated_local_path_count"),
        "ignored_present_generated_local_path_count": summary.get("ignored_present_generated_local_path_count"),
        "unignored_present_generated_local_path_count": summary.get("unignored_present_generated_local_path_count"),
        "suspicious_top_level_entry_count": summary.get("suspicious_top_level_entry_count"),
        "terminal_output_artifact_count": summary.get("terminal_output_artifact_count"),
        "coverage_artifact_present": summary.get("coverage_artifact_present"),
        "egg_info_present": summary.get("egg_info_present"),
        "local_backup_path_count": summary.get("local_backup_path_count"),
        "total_generated_local_bytes_estimate": summary.get("total_generated_local_bytes_estimate"),
        "generated_local_cleanup_authorised": False,
        "file_deletion_authorised": False,
        "artifact_deletion_authorised": False,
        "repository_history_rewrite_authorised": False,
        "no_cleanup_performed": True,
        "no_file_deletion_performed": True,
        "prd0_closure_deferred_to_prd010": True,
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
        "next_authorised_item": "PRD-0.10",
        "evidence_owner": args.prd_owner,
        "evidence_captured_at": now,
        "target_branch": args.target_branch,
        "clean_git_state_at_capture": state["status_short"] == "" if state.get("git_available") else None,
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
    write_json(EVIDENCE_DIR / "repository_hygiene_generated_local_artifact_audit_snapshot.json", inventory)
    (EVIDENCE_DIR / "evidence_index.md").write_text(
        "# PRD-0.9 Repository Hygiene and Generated/Local Artifact Audit Evidence\n\n"
        f"- Captured at: {now}\n"
        f"- Evidence owner: {args.prd_owner}\n"
        f"- Target branch: {args.target_branch}\n"
        f"- Valid: {after.get('valid')}\n"
        f"- Authority valid: {after.get('authority_valid')}\n"
        f"- Configured generated/local paths: {summary.get('configured_generated_local_path_count')}\n"
        f"- Present generated/local paths: {summary.get('present_generated_local_path_count')}\n"
        f"- Ignored present generated/local paths: {summary.get('ignored_present_generated_local_path_count')}\n"
        f"- Unignored present generated/local paths: {summary.get('unignored_present_generated_local_path_count')}\n"
        f"- Suspicious top-level entries: {summary.get('suspicious_top_level_entry_count')}\n"
        f"- Terminal-output artifact candidates: {summary.get('terminal_output_artifact_count')}\n"
        "- Cleanup/deletion/history rewrite authority: false\n"
        "- PRD-0 closure deferred to PRD-0.10\n",
        encoding="utf-8",
    )

    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    if args.json:
        print(json.dumps(after, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.9 evidence valid: {after.get('valid')}")
    return 0 if after.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
