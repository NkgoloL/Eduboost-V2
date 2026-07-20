#!/usr/bin/env python3
"""Capture PRD-1.1 CI inventory authority evidence."""
from __future__ import annotations

import argparse
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path

from scripts.production_readiness.apply_prd101_ci_inventory_authority import apply as apply_authority
from scripts.production_readiness.audit_prd101_ci_inventory_authority import (
    FALSE_KEYS,
    NO_CHANGE_KEYS,
    PRD_ID,
    PRD1_REGISTER,
    RECORD,
    REGISTER,
    SNAPSHOT,
    STREAM_ID,
    TRUE_KEYS,
    inventory_snapshot,
)
from scripts.roadmap_reconciliation.verify_prd101_ci_inventory_authority import evaluate

EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-101-ci-inventory-authority")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def update_prd1_register(now: str) -> dict:
    data = read_json(PRD1_REGISTER)
    data["last_recorded_item"] = PRD_ID
    data["next_authorised_item"] = "PRD-1.2"
    data["last_recorded_at"] = now
    data["status"] = "prd1_1_ci_inventory_recorded_prd1_2_authorised"
    data["ci_inventory_authority_recorded_at"] = now
    data["ci_inventory_authority_recorded"] = True
    for item in data.get("prd1_sequence", []):
        if item.get("prd_id") == "PRD-1.0":
            item["authorised"] = True
            item["status"] = "recorded"
        elif item.get("prd_id") == PRD_ID:
            item["authorised"] = True
            item["status"] = "recorded"
        elif item.get("prd_id") == "PRD-1.2":
            item["authorised"] = True
            item["status"] = "authorised"
        elif item.get("prd_id") not in {"PRD-1.0", PRD_ID, "PRD-1.2"}:
            item.setdefault("authorised", False)
            item.setdefault("status", "blocked")
    data.setdefault("authority_boundaries", {})
    for key in TRUE_KEYS:
        data["authority_boundaries"][key] = True
    for key in FALSE_KEYS:
        data["authority_boundaries"][key] = False
    data.setdefault("implementation_boundaries", {})
    for key in NO_CHANGE_KEYS:
        data["implementation_boundaries"][key] = False
    data["implementation_boundaries"]["ci_inventory_performed"] = True
    write_json(PRD1_REGISTER, data)
    return data


def update_production_register(now: str, prd1_register: dict) -> dict:
    register = read_json(REGISTER)
    register["last_recorded_item"] = PRD_ID
    register["last_recorded_at"] = now
    register["next_authorised_item"] = "PRD-1.2"
    register["status"] = "prd_1_1_ci_inventory_recorded_prd_1_2_authorised"
    register["prd1_next_authorised_item"] = "PRD-1.2"
    register["prd1_ci_inventory_authority_recorded"] = True
    register["prd1_ci_inventory_authority_recorded_at"] = now
    register["prd1_sequence"] = prd1_register.get("prd1_sequence", [])
    register.setdefault("current_truth", {})["prd1_ci_inventory_authority_recorded"] = True
    register["current_truth"]["prd1_next_authorised_item"] = "PRD-1.2"
    for item in register.get("production_readiness_sequence", []):
        if item.get("prd_id") == "PRD-1":
            item["authorised"] = True
            item["status"] = "in_progress"
        elif item.get("prd_id") != "PRD-1":
            item.setdefault("authorised", False)
            item.setdefault("status", "blocked")
    register.setdefault("authority_boundaries", {})
    for key in TRUE_KEYS:
        register["authority_boundaries"][key] = True
    register["authority_boundaries"]["prd1_implementation_authorised"] = False
    for key in FALSE_KEYS:
        register["authority_boundaries"][key] = False
    write_json(REGISTER, register)
    return register


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd101-ci-inventory-authority", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd101_ci_inventory_authority:
        raise SystemExit("must pass --claim-prd101-ci-inventory-authority")

    before = evaluate(Path("."))
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    now = datetime.now(timezone.utc).isoformat()
    state = git_state(args.target_branch)
    apply_authority(Path("."), write_files=True)
    snapshot = inventory_snapshot(Path("."), captured_at=now)
    write_json(SNAPSHOT, snapshot)
    prd1_register = update_prd1_register(now)
    production_register = update_production_register(now, prd1_register)
    snapshot = inventory_snapshot(Path("."), captured_at=now)
    write_json(SNAPSHOT, snapshot)

    record = read_json(RECORD)
    record.update({
        "prd_id": PRD_ID,
        "stream_id": STREAM_ID,
        "status": "prd1_1_ci_inventory_recorded_prd1_2_authorised",
        "prd100_ci_release_gate_stream_authority_valid": before.get("prd100_ci_release_gate_stream_authority_valid") is True,
        "ci_inventory_authority_recorded": True,
        "ci_inventory_evidence_recorded": True,
        "ci_inventory_recorded": True,
        "ci_inventory_performed": True,
        "next_authorised_item": "PRD-1.2",
        "prd1_2_authorised": True,
        "required_check_classification_performed": False,
        "workflow_canonicalisation_performed": False,
        "ci_workflow_changes_performed": False,
        "required_checks_enforced": False,
        "release_gate_enforced": False,
        "branch_protection_modified": False,
        "openapi_reconciliation_performed": False,
        "no_required_check_classification_performed": True,
        "no_workflow_canonicalisation_performed": True,
        "no_ci_workflow_changes_performed": True,
        "no_required_check_enforcement_performed": True,
        "no_release_gate_enforcement_performed": True,
        "no_branch_protection_change_performed": True,
        "no_openapi_reconciliation_performed": True,
        "no_prd2_implementation_performed": True,
        "inventory_summary": snapshot.get("summary", {}),
        "evidence_owner": args.prd_owner,
        "evidence_captured_at": now,
        "target_branch": args.target_branch,
        "clean_git_state_at_capture": state["status_short"] == "" if state.get("git_available") else None,
        "git_state": state,
    })
    for key in TRUE_KEYS:
        record[key] = True
    for key in FALSE_KEYS:
        record[key] = False
    for key in NO_CHANGE_KEYS:
        record[key] = False
    write_json(RECORD, record)

    after = evaluate(Path("."))
    record["verification"] = after
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", after)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "production_readiness_register_prd1_1_snapshot.json", production_register)
    write_json(EVIDENCE_DIR / "prd1_ci_release_gate_register_snapshot.json", prd1_register)
    write_json(EVIDENCE_DIR / "prd1_ci_inventory_authority_snapshot.json", snapshot)
    (EVIDENCE_DIR / "evidence_index.md").write_text(
        "# PRD-1.1 CI Inventory Authority Evidence\n\n"
        f"- Captured at: {now}\n"
        f"- Evidence owner: {args.prd_owner}\n"
        f"- Target branch: {args.target_branch}\n"
        f"- Valid: {after.get('valid')}\n"
        f"- Authority valid: {after.get('authority_valid')}\n"
        f"- PRD-1.0 valid: {after.get('prd100_ci_release_gate_stream_authority_valid')}\n"
        f"- Workflow count: {after.get('workflow_count')}\n"
        f"- master workflow references: {after.get('master_workflow_count')}\n"
        f"- main workflow references: {after.get('main_workflow_count')}\n"
        f"- release-branch workflow references: {after.get('release_branch_workflow_count')}\n"
        f"- release-event workflow references: {after.get('release_event_workflow_count')}\n"
        f"- deployment/promotion workflow references: {after.get('deployment_reference_workflow_count')}\n"
        f"- OpenAPI workflow references: {after.get('openapi_reference_workflow_count')}\n"
        f"- pytest workflow references: {after.get('pytest_reference_workflow_count')}\n"
        f"- Next authorised item: {after.get('register_next_authorised_item')}\n"
        "- Required-check classification performed by PRD-1.1: false\n"
        "- Workflow canonicalisation performed by PRD-1.1: false\n"
        "- CI workflow changes performed by PRD-1.1: false\n"
        "- Release gate enforcement performed by PRD-1.1: false\n"
        "- PRD-2 implementation performed by PRD-1.1: false\n"
        "- Production release/deployment/beta/billing/live learner traffic/new KG scope: false\n",
        encoding="utf-8",
    )

    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    if args.json:
        print(json.dumps(after, indent=2, sort_keys=True))
    else:
        print(f"PRD-1.1 evidence valid: {after.get('valid')}")
    return 0 if after.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
