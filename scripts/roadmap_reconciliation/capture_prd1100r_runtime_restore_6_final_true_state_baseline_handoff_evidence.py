"""Capture PRD-11.0R.RUNTIME-RESTORE-6 final true-state baseline handoff evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.production_readiness.audit_prd1100r_runtime_restore_6_final_true_state_baseline_handoff import ROOT, audit
from scripts.runtime.final_true_state_baseline import collect_final_true_state_baseline, evaluate_final_true_state_handoff_contract

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE-6"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_6_final_true_state_baseline_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_6_final_true_state_baseline_handoff.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-6-final-true-state-baseline-handoff"
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
    parser.add_argument("--claim-prd1100r-runtime-restore-6-final-true-state-baseline-handoff", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--run-expensive-checks", action="store_true")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1100r_runtime_restore_6_final_true_state_baseline_handoff:
        raise SystemExit("missing --claim-prd1100r-runtime-restore-6-final-true-state-baseline-handoff")
    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    now = datetime.now(timezone.utc).isoformat()
    contract = evaluate_final_true_state_handoff_contract(ROOT)
    baseline = collect_final_true_state_baseline(ROOT, run_expensive_checks=args.run_expensive_checks)
    next_item = str(baseline.get("next_authorised_item"))
    all_green = baseline.get("all_release_gates_green") is True
    hold = not all_green
    blockers = baseline.get("blockers", []) if isinstance(baseline.get("blockers"), list) else []

    record = _load(RECORD)
    record.update({
        "status": "final_true_state_baseline_handoff_evidence_recorded",
        "final_true_state_baseline_handoff_evidence_recorded": True,
        "final_true_state_baseline_contract_snapshot": contract,
        "final_true_state_baseline_snapshot": baseline,
        "known_final_true_state_blockers": blockers,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "runtime_baseline_green": baseline.get("green_state", {}).get("runtime_baseline_green") is True,
        "product_runtime_gate_green": baseline.get("green_state", {}).get("product_runtime_gate_green") is True,
        "product_gate_green": baseline.get("green_state", {}).get("product_gate_green") is True,
        "coverage_gate_green": baseline.get("green_state", {}).get("coverage_gate_green") is True,
        "frontend_quality_green": baseline.get("green_state", {}).get("frontend_quality_green") is True,
        "advisory_static_gate_green": baseline.get("green_state", {}).get("advisory_static_gate_green") is True,
        "dependency_audit_gate_green": baseline.get("green_state", {}).get("dependency_audit_gate_green") is True,
        "generated_contracts_green": baseline.get("green_state", {}).get("generated_contracts_green") is True,
        "secret_baseline_gate_green": baseline.get("green_state", {}).get("secret_baseline_gate_green") is True,
        "all_release_gates_green": all_green,
        "controlled_handoff_to_prd1100_1104_authorised": all_green,
        "controlled_beta_activation_operational_hold": hold,
        "live_learner_traffic_operationally_safe": all_green,
        "production_release_evidence_blocked_until_runtime_baseline_green": hold,
        "next_authorised_item": next_item,
        **FALSE_BOUNDARIES,
    })
    _write(RECORD, record)

    for path in (REGISTER, PROD_REGISTER):
        payload = _load(path)
        payload.update({
            "status": "prd11_runtime_restore_6_evidence_recorded",
            "last_recorded_item": PRD_ID,
            "last_recorded_at": now,
            "next_authorised_item": next_item,
            "runtime_restore_6_final_true_state_baseline_handoff_authority_recorded": True,
            "runtime_restore_6_final_true_state_baseline_handoff_evidence_recorded": True,
            "runtime_baseline_green": baseline.get("green_state", {}).get("runtime_baseline_green") is True,
            "product_runtime_gate_green": baseline.get("green_state", {}).get("product_runtime_gate_green") is True,
            "product_gate_green": baseline.get("green_state", {}).get("product_gate_green") is True,
            "coverage_gate_green": baseline.get("green_state", {}).get("coverage_gate_green") is True,
            "frontend_quality_green": baseline.get("green_state", {}).get("frontend_quality_green") is True,
            "advisory_static_gate_green": baseline.get("green_state", {}).get("advisory_static_gate_green") is True,
            "dependency_audit_gate_green": baseline.get("green_state", {}).get("dependency_audit_gate_green") is True,
            "generated_contracts_green": baseline.get("green_state", {}).get("generated_contracts_green") is True,
            "secret_baseline_gate_green": baseline.get("green_state", {}).get("secret_baseline_gate_green") is True,
            "all_release_gates_green": all_green,
            "controlled_handoff_to_prd1100_1104_authorised": all_green,
            "controlled_beta_activation_operational_hold": hold,
            "live_learner_traffic_operationally_safe": all_green,
            "production_release_evidence_blocked_until_runtime_baseline_green": hold,
        })
        payload.setdefault("authority_boundaries", {}).update(FALSE_BOUNDARIES)
        payload.setdefault("current_truth", {}).update({
            "prd11_runtime_restore_1_evidence_recorded": True,
            "prd11_runtime_restore_2_evidence_recorded": True,
            "prd11_runtime_restore_3_evidence_recorded": True,
            "prd11_runtime_restore_4_evidence_recorded": True,
            "prd11_runtime_restore_5_evidence_recorded": True,
            "prd11_runtime_restore_6_authority_recorded": True,
            "prd11_runtime_restore_6_evidence_recorded": True,
            "runtime_baseline_green": baseline.get("green_state", {}).get("runtime_baseline_green") is True,
            "product_runtime_gate_green": baseline.get("green_state", {}).get("product_runtime_gate_green") is True,
            "product_gate_green": baseline.get("green_state", {}).get("product_gate_green") is True,
            "coverage_gate_green": baseline.get("green_state", {}).get("coverage_gate_green") is True,
            "frontend_quality_green": baseline.get("green_state", {}).get("frontend_quality_green") is True,
            "advisory_static_gate_green": baseline.get("green_state", {}).get("advisory_static_gate_green") is True,
            "dependency_audit_gate_green": baseline.get("green_state", {}).get("dependency_audit_gate_green") is True,
            "generated_contracts_green": baseline.get("green_state", {}).get("generated_contracts_green") is True,
            "secret_baseline_gate_green": baseline.get("green_state", {}).get("secret_baseline_gate_green") is True,
            "all_release_gates_green": all_green,
            "controlled_handoff_to_prd1100_1104_authorised": all_green,
            "controlled_beta_activation_operational_hold": hold,
            "live_learner_traffic_operationally_safe": all_green,
            "production_release_evidence_blocked_until_runtime_baseline_green": hold,
            "prd11_next_authorised_item": next_item,
        })
        if path == REGISTER:
            sequence = payload.setdefault("prd11_sequence", [])
            if not any(item.get("prd_id") == PRD_ID for item in sequence):
                sequence.append({"prd_id": PRD_ID, "title": "Final true-state baseline proof and controlled handoff", "status": "evidence_recorded", "authorised": True})
            for item in sequence:
                if item.get("prd_id") == PRD_ID:
                    item.update({"status": "evidence_recorded", "authorised": True})
        _write(path, payload)

    provisional_summary = {
        "prd_id": PRD_ID,
        "captured_at": now,
        "valid": False,
        "authority_valid": True,
        "next_authorised_item": next_item,
        "register_next_authorised_item": next_item,
        "production_register_next_authorised_item": next_item,
        "final_true_state_baseline_contract_valid": contract.get("valid"),
        "all_release_gates_green": all_green,
        "controlled_handoff_to_prd1100_1104_authorised": all_green,
        "controlled_beta_activation_operational_hold": hold,
        "live_learner_traffic_operationally_safe": all_green,
        "production_release_evidence_blocked_until_runtime_baseline_green": hold,
        "blockers": blockers,
    }
    _write(SUMMARY, provisional_summary)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "audit_before.json", before)
    _write(EVIDENCE_DIR / "final_true_state_baseline_contract.json", contract)
    _write(EVIDENCE_DIR / "final_true_state_baseline_snapshot.json", baseline)
    _write(EVIDENCE_DIR / "summary.json", provisional_summary)

    after = audit(ROOT)
    summary = {**provisional_summary, **{
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "next_authorised_item": after["next_authorised_item"],
        "register_next_authorised_item": after["register_next_authorised_item"],
        "production_register_next_authorised_item": after["production_register_next_authorised_item"],
    }}
    _write(SUMMARY, summary)
    _write(EVIDENCE_DIR / "audit_after.json", after)
    _write(EVIDENCE_DIR / "summary.json", summary)
    if args.require_valid and not after["valid"]:
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
