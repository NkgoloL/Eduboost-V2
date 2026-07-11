"""Capture PRD-11.0R.RUNTIME-RESTORE-5 coverage/frontend/advisory evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.advisory_suites.advisory_gate import evaluate_advisory_quality_gate_contract, gate_command_plan
from scripts.production_readiness.audit_prd1100r_runtime_restore_5_coverage_frontend_advisory_gate_repair import ROOT, audit
from scripts.production_readiness.collect_prd1100r_true_state_runtime_baseline import collect_baseline

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE-5"
NEXT_ITEM = "PRD-11.0R.RUNTIME-RESTORE-6"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_5_coverage_frontend_advisory_gate_repair_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_5_coverage_frontend_advisory_gate_repair.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-5-coverage-frontend-advisory-gate-repair"
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
    parser.add_argument("--claim-prd1100r-runtime-restore-5-coverage-frontend-advisory-gate-repair", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--run-expensive-checks", action="store_true")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1100r_runtime_restore_5_coverage_frontend_advisory_gate_repair:
        raise SystemExit("missing --claim-prd1100r-runtime-restore-5-coverage-frontend-advisory-gate-repair")
    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    now = datetime.now(timezone.utc).isoformat()
    contract = evaluate_advisory_quality_gate_contract(ROOT)
    baseline = collect_baseline(ROOT, run_expensive_checks=args.run_expensive_checks)
    command_plan = gate_command_plan()
    blockers = [
        "Coverage execution has not yet produced a fresh green documentation-defined report.",
        "Frontend lint/Vitest/build have not all been independently captured as green in this slice.",
        "Ruff, mypy, Bandit, dependency audits, generated contracts, and secret baseline remain advisory blockers until independently green or dispositioned.",
        "Runtime baseline remains red until stack/schema/readiness blockers are cleared.",
    ]

    record = _load(RECORD)
    record.update({
        "status": "coverage_frontend_advisory_gate_evidence_recorded",
        "coverage_frontend_advisory_gate_evidence_recorded": True,
        "coverage_frontend_advisory_gate_contract_snapshot": contract,
        "coverage_frontend_advisory_command_plan": command_plan,
        "runtime_baseline_snapshot": baseline,
        "known_coverage_frontend_advisory_blockers": blockers,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "runtime_baseline_green": bool(baseline.get("runtime_baseline_green")),
        "runtime_baseline_status": baseline.get("overall_status"),
        "coverage_gate_green": False,
        "frontend_quality_green": False,
        "advisory_static_gate_green": False,
        "dependency_audit_gate_green": False,
        "generated_contracts_green": False,
        "secret_baseline_gate_green": False,
        "product_gate_green": False,
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
        "next_authorised_item": NEXT_ITEM,
        **FALSE_BOUNDARIES,
    })
    _write(RECORD, record)

    for path in (REGISTER, PROD_REGISTER):
        payload = _load(path)
        payload.update({
            "status": "prd11_runtime_restore_5_evidence_recorded",
            "last_recorded_item": PRD_ID,
            "last_recorded_at": now,
            "next_authorised_item": NEXT_ITEM,
            "runtime_restore_5_coverage_frontend_advisory_authority_recorded": True,
            "runtime_restore_5_coverage_frontend_advisory_evidence_recorded": True,
            "runtime_baseline_green": bool(baseline.get("runtime_baseline_green")),
            "runtime_baseline_status": baseline.get("overall_status"),
            "coverage_gate_green": False,
            "frontend_quality_green": False,
            "advisory_static_gate_green": False,
            "product_gate_green": False,
            "controlled_beta_activation_operational_hold": True,
            "live_learner_traffic_operationally_safe": False,
            "production_release_evidence_blocked_until_runtime_baseline_green": True,
        })
        payload.setdefault("authority_boundaries", {}).update(FALSE_BOUNDARIES)
        payload.setdefault("current_truth", {}).update({
            "prd11_runtime_restore_1_evidence_recorded": True,
            "prd11_runtime_restore_2_evidence_recorded": True,
            "prd11_runtime_restore_3_evidence_recorded": True,
            "prd11_runtime_restore_4_evidence_recorded": True,
            "prd11_runtime_restore_5_authority_recorded": True,
            "prd11_runtime_restore_5_evidence_recorded": True,
            "coverage_gate_green": False,
            "frontend_quality_green": False,
            "advisory_static_gate_green": False,
            "runtime_baseline_green": bool(baseline.get("runtime_baseline_green")),
            "product_gate_green": False,
            "controlled_beta_activation_operational_hold": True,
            "live_learner_traffic_operationally_safe": False,
            "production_release_evidence_blocked_until_runtime_baseline_green": True,
            "prd11_next_authorised_item": NEXT_ITEM,
        })
        if path == REGISTER:
            sequence = payload.setdefault("prd11_sequence", [])
            if not any(item.get("prd_id") == PRD_ID for item in sequence):
                sequence.append({"prd_id": PRD_ID, "title": "Coverage execution, frontend quality, and advisory gate repair", "status": "evidence_recorded", "authorised": True})
            for item in sequence:
                if item.get("prd_id") == PRD_ID:
                    item.update({"status": "evidence_recorded", "authorised": True})
        _write(path, payload)

    provisional_summary = {
        "prd_id": PRD_ID,
        "captured_at": now,
        "valid": False,
        "authority_valid": True,
        "next_authorised_item": NEXT_ITEM,
        "register_next_authorised_item": NEXT_ITEM,
        "production_register_next_authorised_item": NEXT_ITEM,
        "coverage_frontend_advisory_gate_contract_valid": contract.get("valid"),
        "runtime_baseline_green": bool(baseline.get("runtime_baseline_green")),
        "runtime_baseline_status": baseline.get("overall_status"),
        "baseline_blockers": baseline.get("blockers", []),
        "coverage_gate_green": False,
        "frontend_quality_green": False,
        "advisory_static_gate_green": False,
        "known_coverage_frontend_advisory_blockers": blockers,
        "controlled_beta_activation_operational_hold": True,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
    }
    _write(SUMMARY, provisional_summary)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "audit_before.json", before)
    _write(EVIDENCE_DIR / "coverage_frontend_advisory_gate_contract.json", contract)
    _write(EVIDENCE_DIR / "coverage_frontend_advisory_command_plan.json", {"commands": command_plan})
    _write(EVIDENCE_DIR / "true_state_runtime_baseline.json", baseline)
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
