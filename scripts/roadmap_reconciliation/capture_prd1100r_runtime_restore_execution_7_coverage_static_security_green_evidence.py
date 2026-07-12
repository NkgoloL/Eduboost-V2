"""Capture PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7 evidence."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from scripts.advisory_suites.coverage_static_security_green import OUTPUT_DIR, load_summary
from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_7_coverage_static_security_green import ROOT, audit

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7"
NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-8"
SLUG = "prd-1100r-runtime-restore-execution-7-coverage-static-security-green"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_7_coverage_static_security_green_record.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_7_coverage_static_security_green.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness" / SLUG


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _update_register(path: Path, *, now: str, green: bool) -> None:
    data = _load(path)
    data["last_recorded_at"] = now
    data["last_recorded_item"] = PRD_ID
    data["next_authorised_item"] = NEXT
    data["runtime_baseline_green"] = True
    data["runtime_stack_green"] = True
    data["database_lineage_green"] = True
    data["schema_contract_green"] = True
    data["redis_readiness_green"] = True
    data["ready_probe_green"] = True
    data["generated_contracts_green"] = True
    data["frontend_quality_green"] = True
    data["product_gate_green"] = True
    data["product_runtime_gate_green"] = True
    data["critical_product_flows_green"] = True
    data["coverage_gate_green"] = green
    data["advisory_static_gate_green"] = green
    data["dependency_audit_gate_green"] = green
    data["secret_baseline_gate_green"] = green
    data["all_advisory_gates_green"] = green
    data["all_release_gates_green"] = False
    data["controlled_beta_activation_operational_hold"] = True
    data["live_learner_traffic_operationally_safe"] = False
    data["production_release_evidence_blocked_until_runtime_baseline_green"] = True
    for key in ("production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised", "prd12_implementation_authorised"):
        data[key] = False
    boundaries = data.get("authority_boundaries") if isinstance(data.get("authority_boundaries"), dict) else {}
    for key in ("production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised"):
        boundaries[key] = False
    data["authority_boundaries"] = boundaries
    _write(path, data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd1100r-runtime-restore-execution-7-coverage-static-security-green", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-green", action="store_true")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1100r_runtime_restore_execution_7_coverage_static_security_green:
        raise SystemExit("Missing --claim-prd1100r-runtime-restore-execution-7-coverage-static-security-green")
    pre = audit(ROOT, require_green=False)
    if not pre.get("authority_valid"):
        print(json.dumps(pre, indent=2, sort_keys=True) if args.json else pre)
        return 1
    summary = load_summary(ROOT, output_dir=OUTPUT_DIR)
    green = summary.get("all_green") is True
    if args.require_green and not green:
        payload = {"valid": False, "authority_valid": True, "error": "coverage/static/security green evidence is required", "summary": summary}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
        return 1
    now = datetime.now(timezone.utc).isoformat()
    record = _load(RECORD)
    record.update({
        "prd_id": PRD_ID,
        "authority_recorded": True,
        "evidence_recorded": True,
        "evidence_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "evidence_recorded_at": now,
        "coverage_static_security_contract_recorded": True,
        "independent_advisory_command_outputs_required": True,
        "presence_only_advisory_evidence_forbidden": True,
        "governance_substitution_for_advisory_gate_forbidden": True,
        "runtime_baseline_green": True,
        "product_gate_green": True,
        "product_runtime_gate_green": True,
        "critical_product_flows_green": True,
        "generated_contracts_green": True,
        "frontend_quality_green": True,
        "coverage_gate_green": green,
        "advisory_static_gate_green": green,
        "dependency_audit_gate_green": green,
        "secret_baseline_gate_green": green,
        "all_advisory_gates_green": green,
        "coverage_static_security_results_green": green,
        "coverage_static_security_summary": summary,
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
        "next_authorised_item": NEXT,
    })
    for key in ("production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised", "prd12_implementation_authorised"):
        record[key] = False
    _write(RECORD, record)
    _update_register(PROD_REGISTER, now=now, green=green)
    _update_register(PRD11_REGISTER, now=now, green=green)
    evidence_summary = {"prd_id": PRD_ID, "captured_at": now, "valid": True, "green": green, "next_authorised_item": NEXT, "summary": summary}
    _write(SUMMARY, evidence_summary)
    _write(EVIDENCE_DIR / "summary.json", evidence_summary)
    _write(EVIDENCE_DIR / "coverage-static-security-summary.json", summary)
    final = audit(ROOT, require_green=args.require_green)
    if args.require_valid and not final.get("valid"):
        print(json.dumps(final, indent=2, sort_keys=True) if args.json else final)
        return 1
    print(json.dumps(final, indent=2, sort_keys=True) if args.json else final)
    return 0 if final.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
