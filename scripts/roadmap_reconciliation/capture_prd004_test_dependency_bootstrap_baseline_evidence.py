#!/usr/bin/env python3
"""Capture PRD-0.4 test/dependency bootstrap baseline evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from scripts.production_readiness.audit_prd004_test_dependency_bootstrap_baseline import build_baseline
from scripts.roadmap_reconciliation.verify_prd004_test_dependency_bootstrap_baseline import evaluate

PRD_ID = "PRD-0.4"
RECORD = Path("docs/roadmap/production_readiness/prd_004_test_dependency_bootstrap_baseline_record.json")
REGISTER = Path("docs/roadmap/production_readiness/production_readiness_register.json")
BASELINE = Path("docs/roadmap/production_readiness/test_dependency_bootstrap_baseline.json")
EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-004-test-dependency-bootstrap-baseline")

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
    register["next_authorised_item"] = "PRD-0.5"
    for item in register.get("prd0_sequence", []):
        if item.get("prd_id") == PRD_ID:
            item["authorised"] = True
            item["status"] = "recorded"
    write_json(REGISTER, register)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd004-test-dependency-bootstrap-baseline", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd004_test_dependency_bootstrap_baseline:
        raise SystemExit("must pass --claim-prd004-test-dependency-bootstrap-baseline")
    before = evaluate(Path("."))
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    state = git_state(args.target_branch)
    now = datetime.now(timezone.utc).isoformat()
    baseline = build_baseline(Path("."), captured_at=now)
    write_json(BASELINE, baseline)
    record = read_json(RECORD)
    record.update({"prd_id": PRD_ID, "stream_id": "PRD-PRODUCTION-READINESS", "status": "test_dependency_bootstrap_baseline_recorded", "test_dependency_bootstrap_baseline_recorded": True, "prd003_documentation_housekeeping_ratchet_refresh_valid": before.get("prd003_documentation_housekeeping_ratchet_refresh_valid") is True, "dependency_manifest_recorded": True, "bootstrap_command_contract_recorded": True, "python_test_dependency_contract_recorded": True, "frontend_test_dependency_contract_recorded": True, "ci_dependency_install_contract_recorded": True, "deferred_failure_triage_boundary_recorded": True, "baseline_schema_version": baseline.get("schema_version"), "requirements_file_count": len(baseline.get("python_backend", {}).get("requirement_files", [])), "pytest_declared": baseline.get("python_backend", {}).get("dependency_markers", {}).get("pytest_declared") is True, "pytest_cov_declared": baseline.get("python_backend", {}).get("dependency_markers", {}).get("pytest_cov_declared") is True, "frontend_vitest_declared": baseline.get("frontend", {}).get("dependency_markers", {}).get("vitest_declared") is True, "workflow_count": baseline.get("workflow_inventory", {}).get("workflow_count"), "direct_pytest_workflow_count": baseline.get("workflow_inventory", {}).get("direct_pytest_workflow_count"), "module_pytest_workflow_count": baseline.get("workflow_inventory", {}).get("module_pytest_workflow_count"), "runtime_kg_implementation_claimed": True, "runtime_kg_authority_switch_authorised": True, "authority_switch_executed": True, "production_release_authorised": False, "deployment_authorised": False, "release_tag_authorised": False, "public_beta_authorised": False, "public_beta_live_traffic_authorised": False, "live_learner_traffic_authorised": False, "billing_launch_authorised": False, "live_payment_processing_authorised": False, "new_kg_slice_authorised": False, "prd1_implementation_authorised": False, "next_authorised_item": "PRD-0.5", "evidence_owner": args.prd_owner, "evidence_captured_at": now, "target_branch": args.target_branch, "clean_git_state_at_capture": state["status_short"] == "", "git_state": state})
    update_register(now)
    write_json(RECORD, record)
    after = evaluate(Path("."))
    record["verification"] = after
    write_json(RECORD, record)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", after)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "test_dependency_bootstrap_baseline_snapshot.json", baseline)
    (EVIDENCE_DIR / "evidence_index.md").write_text("# PRD-0.4 Test/dependency Bootstrap Baseline Evidence\n\n" f"- Captured at: {now}\n" f"- Evidence owner: {args.prd_owner}\n" f"- Target branch: {args.target_branch}\n" f"- Valid: {after.get('valid')}\n" f"- Authority valid: {after.get('authority_valid')}\n" f"- Requirements files: {record.get('requirements_file_count')}\n" f"- Workflow count: {record.get('workflow_count')}\n" f"- Direct pytest workflow count: {record.get('direct_pytest_workflow_count')}\n" "- Backend test command contract: PYTHONPATH=. python3 -m pytest ...\n" "- Deferred test failure triage: PRD-0.5\n" "- Deferred workflow command convergence: PRD-0.6\n", encoding="utf-8")
    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    if args.json:
        print(json.dumps(after, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.4 evidence valid: {after.get('valid')}")
    return 0 if after.get("valid") else 1

if __name__ == "__main__":
    raise SystemExit(main())
