"""Capture PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2 evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.advisory_suites.generated_frontend_quality_gate import ROOT, execute_gate_plan, gate_command_plan
from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_2_generated_contract_frontend_quality import audit

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2"
NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_2_generated_contract_frontend_quality_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
CONTRACT = ROOT / "docs/roadmap/production_readiness/generated_contract_frontend_quality_execution_contract.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_2_generated_contract_frontend_quality.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-execution-2-generated-contract-frontend-quality"
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


def _result_green(results: dict[str, Any], gate_ids: set[str]) -> bool:
    items = results.get("results", []) if isinstance(results.get("results"), list) else []
    selected = [item for item in items if item.get("gate_id") in gate_ids]
    return bool(selected) and all(item.get("green") is True for item in selected)


def _flatten_results(results: dict[str, Any]) -> list[dict[str, Any]]:
    flattened = []
    for item in results.get("results", []) if isinstance(results.get("results"), list) else []:
        result = item.get("result", {}) if isinstance(item.get("result"), dict) else {}
        flattened.append({
            "gate_id": item.get("gate_id"),
            "command": result.get("command") or " ".join(item.get("command", [])),
            "exit_code": result.get("exit_code"),
            "output_artifact": item.get("evidence_artifact"),
            "captured_at": result.get("captured_at") or results.get("captured_at"),
            "green": item.get("green") is True,
        })
    return flattened


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd1100r-runtime-restore-execution-2-generated-contract-frontend-quality", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--run-gates", action="store_true")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1100r_runtime_restore_execution_2_generated_contract_frontend_quality:
        raise SystemExit("missing --claim-prd1100r-runtime-restore-execution-2-generated-contract-frontend-quality")
    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    now = datetime.now(timezone.utc).isoformat()
    if args.run_gates:
        gate_results = execute_gate_plan(ROOT)
    else:
        gate_results = {"executed": False, "commands": gate_command_plan(ROOT), "results": [], "all_green": False, "captured_at": now}
    generated_green = _result_green(gate_results, {"generated_contract_regeneration", "generated_contract_drift_check"})
    frontend_green = _result_green(gate_results, {"frontend_typecheck", "frontend_lint", "frontend_vitest", "frontend_production_build"})
    record = _load(RECORD)
    record.update({
        "status": "runtime_restore_execution_2_evidence_recorded",
        "evidence_recorded": True,
        "generated_contract_frontend_quality_evidence_recorded": True,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "gate_results": gate_results,
        "generated_contracts_green": generated_green,
        "frontend_quality_green": frontend_green,
        "runtime_baseline_green": False,
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
        "next_authorised_item": NEXT,
        **FALSE_BOUNDARIES,
    })
    _write(RECORD, record)
    contract = _load(CONTRACT)
    contract.update({
        "last_reviewed_at": now,
        "execution_results": _flatten_results(gate_results),
        "generated_contracts_green": generated_green,
        "frontend_quality_green": frontend_green,
        "next_after_evidence": NEXT,
    })
    _write(CONTRACT, contract)
    for path in (REGISTER, PROD_REGISTER):
        payload = _load(path)
        payload.update({
            "status": "prd11_runtime_restore_execution_2_evidence_recorded",
            "last_recorded_item": PRD_ID,
            "last_recorded_at": now,
            "next_authorised_item": NEXT,
            "runtime_restore_execution_2_generated_contract_frontend_quality_authority_recorded": True,
            "runtime_restore_execution_2_generated_contract_frontend_quality_evidence_recorded": True,
            "generated_contracts_green": generated_green,
            "frontend_quality_green": frontend_green,
            "runtime_baseline_green": False,
            "controlled_beta_activation_operational_hold": True,
            "live_learner_traffic_operationally_safe": False,
            "production_release_evidence_blocked_until_runtime_baseline_green": True,
            **FALSE_BOUNDARIES,
        })
        payload.setdefault("authority_boundaries", {}).update(FALSE_BOUNDARIES)
        payload.setdefault("current_truth", {}).update({
            "prd11_runtime_restore_execution_2_authority_recorded": True,
            "prd11_runtime_restore_execution_2_evidence_recorded": True,
            "generated_contracts_green": generated_green,
            "frontend_quality_green": frontend_green,
            "runtime_baseline_green": False,
            "controlled_beta_activation_operational_hold": True,
            "live_learner_traffic_operationally_safe": False,
            "prd11_next_authorised_item": NEXT,
        })
        if path == REGISTER:
            sequence = payload.setdefault("prd11_sequence", [])
            if not any(isinstance(item, dict) and item.get("prd_id") == PRD_ID for item in sequence):
                sequence.append({"prd_id": PRD_ID, "title": "Generated contract regeneration and frontend quality execution", "status": "evidence_recorded", "authorised": True})
            for item in sequence:
                if isinstance(item, dict) and item.get("prd_id") == PRD_ID:
                    item.update({"status": "evidence_recorded", "authorised": True})
        _write(path, payload)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "prd_id": PRD_ID,
        "captured_at": now,
        "authority_valid": True,
        "valid": False,
        "generated_contracts_green": generated_green,
        "frontend_quality_green": frontend_green,
        "runtime_baseline_green": False,
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "next_authorised_item": NEXT,
        "register_next_authorised_item": NEXT,
        "production_register_next_authorised_item": NEXT,
    }
    _write(SUMMARY, summary)
    _write(EVIDENCE_DIR / "audit_before.json", before)
    _write(EVIDENCE_DIR / "generated_frontend_gate_results.json", gate_results)
    _write(EVIDENCE_DIR / "generated_contract_frontend_quality_contract.json", contract)
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
