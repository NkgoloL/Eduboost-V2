"""Capture PRD-11.0R.RUNTIME-RESTORE.EXECUTION-1 evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_1_runtime_command_frontend_generated_contracts import ROOT, audit
from scripts.production_readiness.collect_prd1100r_true_state_runtime_baseline import collect_baseline

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-1"
NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_1_runtime_command_frontend_generated_contracts_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_1_runtime_command_frontend_generated_contracts.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-execution-1-runtime-command-frontend-generated-contracts"
FALSE_BOUNDARIES = {
    "production_release_authorised": False,
    "deployment_authorised": False,
    "release_tag_authorised": False,
    "public_beta_authorised": False,
    "public_beta_live_traffic_authorised": False,
    "billing_launch_authorised": False,
    "live_payment_processing_authorised": False,
    "prd12_implementation_authorised": False,
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd1100r-runtime-restore-execution-1-runtime-command-frontend-generated-contracts", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--run-expensive-checks", action="store_true")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1100r_runtime_restore_execution_1_runtime_command_frontend_generated_contracts:
        raise SystemExit("missing --claim-prd1100r-runtime-restore-execution-1-runtime-command-frontend-generated-contracts")
    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    now = datetime.now(timezone.utc).isoformat()
    baseline = collect_baseline(ROOT, run_expensive_checks=args.run_expensive_checks)
    record = _load(RECORD)
    record.update({
        "status": "runtime_restore_execution_1_evidence_recorded",
        "evidence_recorded": True,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "baseline_snapshot": baseline,
        "runtime_baseline_green": baseline.get("runtime_baseline_green") is True,
        "frontend_quality_green": baseline.get("checks", {}).get("frontend_quality_gate", {}).get("status") == "pass",
        "generated_contracts_green": baseline.get("checks", {}).get("generated_contracts", {}).get("status") == "pass",
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
        "next_authorised_item": NEXT,
        **FALSE_BOUNDARIES,
    })
    _write(RECORD, record)
    for path in (REGISTER, PROD_REGISTER):
        payload = _load(path)
        payload.update({
            "status": "prd11_runtime_restore_execution_1_evidence_recorded",
            "last_recorded_item": PRD_ID,
            "last_recorded_at": now,
            "next_authorised_item": NEXT,
            "runtime_restore_execution_1_runtime_command_frontend_generated_contracts_authority_recorded": True,
            "runtime_restore_execution_1_runtime_command_frontend_generated_contracts_evidence_recorded": True,
            "runtime_baseline_green": baseline.get("runtime_baseline_green") is True,
            "frontend_quality_green": baseline.get("checks", {}).get("frontend_quality_gate", {}).get("status") == "pass",
            "generated_contracts_green": baseline.get("checks", {}).get("generated_contracts", {}).get("status") == "pass",
            "controlled_beta_activation_operational_hold": True,
            "live_learner_traffic_operationally_safe": False,
            "production_release_evidence_blocked_until_runtime_baseline_green": True,
            **FALSE_BOUNDARIES,
        })
        payload.setdefault("authority_boundaries", {}).update(FALSE_BOUNDARIES)
        payload.setdefault("current_truth", {}).update({
            "prd11_runtime_restore_execution_1_authority_recorded": True,
            "prd11_runtime_restore_execution_1_evidence_recorded": True,
            "runtime_command_execution_repaired": True,
            "frontend_conditional_hook_repaired": True,
            "generated_contract_gate_uses_current_interpreter": True,
            "runtime_baseline_green": baseline.get("runtime_baseline_green") is True,
            "controlled_beta_activation_operational_hold": True,
            "live_learner_traffic_operationally_safe": False,
            "prd11_next_authorised_item": NEXT,
        })
        if path == REGISTER:
            sequence = payload.setdefault("prd11_sequence", [])
            if not any(item.get("prd_id") == PRD_ID for item in sequence if isinstance(item, dict)):
                sequence.append({"prd_id": PRD_ID, "title": "Runtime command execution, frontend hook repair, and generated contract gate activation", "status": "evidence_recorded", "authorised": True})
            for item in sequence:
                if isinstance(item, dict) and item.get("prd_id") == PRD_ID:
                    item.update({"status": "evidence_recorded", "authorised": True})
        _write(path, payload)
    summary = {
        "prd_id": PRD_ID,
        "captured_at": now,
        "authority_valid": True,
        "valid": False,
        "runtime_baseline_green": baseline.get("runtime_baseline_green") is True,
        "frontend_quality_green": baseline.get("checks", {}).get("frontend_quality_gate", {}).get("status") == "pass",
        "generated_contracts_green": baseline.get("checks", {}).get("generated_contracts", {}).get("status") == "pass",
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "next_authorised_item": NEXT,
        "register_next_authorised_item": NEXT,
        "production_register_next_authorised_item": NEXT,
    }
    _write(SUMMARY, summary)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "audit_before.json", before)
    _write(EVIDENCE_DIR / "runtime_baseline_snapshot.json", baseline)
    after = audit(ROOT)
    summary.update({
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "register_next_authorised_item": after["register_next_authorised_item"],
        "production_register_next_authorised_item": after["production_register_next_authorised_item"],
    })
    _write(SUMMARY, summary)
    _write(EVIDENCE_DIR / "audit_after.json", after)
    _write(EVIDENCE_DIR / "summary.json", summary)
    if args.require_valid and not after["valid"]:
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
