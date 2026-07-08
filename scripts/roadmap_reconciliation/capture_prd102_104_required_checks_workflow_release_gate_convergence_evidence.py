#!/usr/bin/env python3
"""Capture PRD-1.2-1.4 required-check, workflow, and release-gate convergence evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from scripts.production_readiness.apply_prd102_104_required_checks_workflow_release_gate_convergence import (
    CONFIG,
    FALSE_BOUNDARIES,
    PRD_ID,
    RECORD,
    STREAM_ID,
    TRUE_BOUNDARIES,
    apply as apply_authority,
)
from scripts.roadmap_reconciliation.verify_prd102_104_required_checks_workflow_release_gate_convergence import evaluate

ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD1_REGISTER = ROOT / "prd1_ci_release_gate_register.json"
EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-102-104-required-checks-workflow-release-gate-convergence")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_state(target_branch: str) -> dict:
    def run(args: list[str]) -> str | None:
        try:
            return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
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
    data["last_recorded_item"] = "PRD-1.4"
    data["next_authorised_item"] = "PRD-1.5"
    data["last_recorded_at"] = now
    data["status"] = "prd1_2_1_4_required_checks_workflow_release_gate_recorded_prd1_5_authorised"
    data["required_check_classification_recorded"] = True
    data["workflow_canonicalisation_recorded"] = True
    data["release_gate_definition_recorded"] = True
    data["required_checks_workflow_release_gate_recorded_at"] = now
    for item in data.get("prd1_sequence", []):
        if item.get("prd_id") in {"PRD-1.0", "PRD-1.1", "PRD-1.2", "PRD-1.3", "PRD-1.4"}:
            item["authorised"] = True
            item["status"] = "recorded"
        elif item.get("prd_id") == "PRD-1.5":
            item["authorised"] = True
            item["status"] = "authorised"
        else:
            item.setdefault("authorised", False)
            item.setdefault("status", "blocked")
    data.setdefault("implementation_boundaries", {})
    data["implementation_boundaries"].update({
        "required_check_classification_performed": True,
        "workflow_canonicalisation_performed": True,
        "ci_workflow_changes_performed": True,
        "openapi_reconciliation_performed": True,
        "required_checks_enforced": False,
        "release_gate_enforced": False,
        "branch_protection_modified": False,
    })
    data.setdefault("authority_boundaries", {})
    for key in TRUE_BOUNDARIES:
        data["authority_boundaries"][key] = True
    for key in FALSE_BOUNDARIES:
        data["authority_boundaries"][key] = False
    write_json(PRD1_REGISTER, data)
    return data


def update_production_register(now: str, prd1_register: dict) -> dict:
    register = read_json(REGISTER)
    register["last_recorded_item"] = "PRD-1.4"
    register["last_recorded_at"] = now
    register["next_authorised_item"] = "PRD-1.5"
    register["status"] = "prd_1_2_1_4_required_checks_workflow_release_gate_recorded_prd_1_5_authorised"
    register["prd1_next_authorised_item"] = "PRD-1.5"
    register["prd1_required_checks_workflow_release_gate_recorded"] = True
    register["prd1_required_checks_workflow_release_gate_recorded_at"] = now
    register["prd1_sequence"] = prd1_register.get("prd1_sequence", [])
    register.setdefault("current_truth", {})["prd1_required_checks_workflow_release_gate_recorded"] = True
    register["current_truth"]["prd1_next_authorised_item"] = "PRD-1.5"
    register.setdefault("authority_boundaries", {})
    for key in TRUE_BOUNDARIES:
        register["authority_boundaries"][key] = True
    register["authority_boundaries"]["prd1_implementation_authorised"] = False
    for key in FALSE_BOUNDARIES:
        register["authority_boundaries"][key] = False
    write_json(REGISTER, register)
    return register


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd102-104-required-checks-workflow-release-gate-convergence", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd102_104_required_checks_workflow_release_gate_convergence:
        raise SystemExit("must pass --claim-prd102-104-required-checks-workflow-release-gate-convergence")

    before = evaluate(Path("."))
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    now = datetime.now(timezone.utc).isoformat()
    state = git_state(args.target_branch)
    config = apply_authority(Path("."), write_files=True)
    prd1_register = update_prd1_register(now)
    production_register = update_production_register(now, prd1_register)

    record = read_json(RECORD)
    record.update({
        "schema_version": "prd1-required-checks-workflow-release-gate-convergence-record/v1",
        "prd_id": PRD_ID,
        "merged_prd_slices": ["PRD-1.2", "PRD-1.3", "PRD-1.4"],
        "stream_id": STREAM_ID,
        "status": "prd1_2_1_4_recorded_prd1_5_authorised",
        "required_checks_workflow_release_gate_evidence_recorded": True,
        "required_check_classification_performed": True,
        "workflow_canonicalisation_performed": True,
        "ci_workflow_changes_performed": True,
        "openapi_reconciliation_performed": True,
        "required_checks_enforced": False,
        "release_gate_enforced": False,
        "branch_protection_modified": False,
        "prd1_5_authorised": True,
        "next_authorised_item": "PRD-1.5",
        "evidence_owner": args.prd_owner,
        "evidence_captured_at": now,
        "target_branch": args.target_branch,
        "clean_git_state_at_capture": state["status_short"] == "" if state.get("git_available") else None,
        "git_state": state,
        "config_summary": {
            "required_check_count": len(config.get("required_check_classification", {}).get("required_checks", [])),
            "python_m_pytest_workflow_count": config.get("workflow_canonicalisation", {}).get("workflow_summary_after_canonicalisation", {}).get("python_m_pytest_workflow_count"),
            "python3_m_pytest_workflow_count": config.get("workflow_canonicalisation", {}).get("workflow_summary_after_canonicalisation", {}).get("python3_m_pytest_workflow_count"),
            "openapi_root_and_docs_match": config.get("openapi_reconciliation", {}).get("root_and_docs_openapi_match"),
        },
    })
    for key in TRUE_BOUNDARIES:
        record[key] = True
    for key in FALSE_BOUNDARIES:
        record[key] = False
    write_json(RECORD, record)

    after = evaluate(Path("."))
    record["verification"] = after
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", after)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "production_readiness_register_prd1_2_1_4_snapshot.json", production_register)
    write_json(EVIDENCE_DIR / "prd1_ci_release_gate_register_snapshot.json", prd1_register)
    write_json(EVIDENCE_DIR / "required_checks_workflow_release_gate_config_snapshot.json", read_json(CONFIG))
    (EVIDENCE_DIR / "evidence_index.md").write_text(
        "# PRD-1.2-1.4 Required Checks, Workflow Canonicalisation, and Release Gate Evidence\n\n"
        f"- Captured at: {now}\n"
        f"- Evidence owner: {args.prd_owner}\n"
        f"- Target branch: {args.target_branch}\n"
        f"- Valid: {after.get('valid')}\n"
        f"- Authority valid: {after.get('authority_valid')}\n"
        "- Required-check classification performed: true\n"
        "- Workflow canonicalisation performed: true\n"
        "- CI workflow command changes performed: true\n"
        "- OpenAPI reconciliation performed: true\n"
        "- Required checks enforced: false\n"
        "- Release gate enforced: false\n"
        "- Branch protection modified: false\n"
        f"- Deprecated workflow pytest command count: {after.get('python_m_pytest_workflow_count')}\n"
        f"- Next authorised item: {after.get('register_next_authorised_item')}\n"
        "- Production release/deployment/beta/billing/live learner traffic/PRD-2 implementation: false\n",
        encoding="utf-8",
    )

    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    if args.json:
        print(json.dumps(after, indent=2, sort_keys=True))
    else:
        print(f"PRD-1.2-1.4 evidence valid: {after.get('valid')}")
    return 0 if after.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
