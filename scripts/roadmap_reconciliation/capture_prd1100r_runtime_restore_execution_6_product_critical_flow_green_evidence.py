"""Capture PRD-11.0R.RUNTIME-RESTORE.EXECUTION-6 evidence."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_6_product_critical_flow_green import ROOT, audit
from scripts.test_suites.product_critical_flow_green import OUTPUT_DIR, load_flow_summary

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-6"
NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7"
SLUG = "prd-1100r-runtime-restore-execution-6-product-critical-flow-green"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_6_product_critical_flow_green_record.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_6_product_critical_flow_green.json"
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
    data["frontend_quality_green"] = True
    data["generated_contracts_green"] = True
    data["product_gate_green"] = green
    data["product_runtime_gate_green"] = green
    data["critical_product_flows_green"] = green
    data["coverage_gate_green"] = False
    data["advisory_static_gate_green"] = False
    data["dependency_audit_gate_green"] = False
    data["secret_baseline_gate_green"] = False
    data["controlled_beta_activation_operational_hold"] = True
    data["live_learner_traffic_operationally_safe"] = False
    data["production_release_evidence_blocked_until_runtime_baseline_green"] = True
    for key in ("production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised"):
        data[key] = False
    bounds = data.setdefault("authority_boundaries", {})
    for key in ("production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised", "prd12_implementation_authorised"):
        bounds[key] = False
    current = data.setdefault("current_truth", {})
    current.update({
        "prd11_next_authorised_item": NEXT,
        "prd11_runtime_restore_execution_6_evidence_recorded": True,
        "runtime_baseline_green": True,
        "runtime_stack_green": True,
        "database_lineage_green": True,
        "schema_contract_green": True,
        "redis_readiness_green": True,
        "ready_probe_green": True,
        "frontend_quality_green": True,
        "generated_contracts_green": True,
        "product_flow_results_green": green,
        "product_gate_green": green,
        "product_runtime_gate_green": green,
        "critical_product_flows_green": green,
        "coverage_gate_green": False,
        "advisory_static_gate_green": False,
        "dependency_audit_gate_green": False,
        "secret_baseline_gate_green": False,
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
    })
    _write(path, data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd1100r-runtime-restore-execution-6-product-critical-flow-green", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-green", action="store_true")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1100r_runtime_restore_execution_6_product_critical_flow_green:
        raise SystemExit("explicit PRD-11.0R execution-6 claim flag is required")
    before = audit(ROOT, require_green=False)
    if not before.get("authority_valid"):
        raise SystemExit("authority state is not valid")
    flow_summary = load_flow_summary(ROOT, output_dir=OUTPUT_DIR)
    green = flow_summary.get("all_green") is True
    if args.require_green and not green:
        raise SystemExit("product critical-flow green evidence is required but current flow summary is not green")
    now = datetime.now(timezone.utc).isoformat()
    record = _load(RECORD)
    record.update({
        "evidence_recorded": True,
        "evidence_recorded_at": now,
        "evidence_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "product_flow_summary": flow_summary,
        "product_flow_results_green": green,
        "product_gate_green": green,
        "product_runtime_gate_green": green,
        "critical_product_flows_green": green,
        "runtime_baseline_green": True,
        "runtime_stack_green": True,
        "database_lineage_green": True,
        "schema_contract_green": True,
        "redis_readiness_green": True,
        "ready_probe_green": True,
        "frontend_quality_green": True,
        "generated_contracts_green": True,
        "coverage_gate_green": False,
        "advisory_static_gate_green": False,
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
        "next_authorised_item": NEXT,
    })
    _write(RECORD, record)
    _update_register(PROD_REGISTER, now=now, green=green)
    _update_register(PRD11_REGISTER, now=now, green=green)
    provisional = {"prd_id": PRD_ID, "captured_at": now, "product_flow_results_green": green}
    _write(SUMMARY, provisional)
    after = audit(ROOT, require_green=args.require_green)
    summary = {**after, "product_flow_results_green": green, "captured_at": now, "evidence_owner": args.prd_owner, "flow_summary_path": str(OUTPUT_DIR / "summary.json")}
    _write(SUMMARY, summary)
    _write(EVIDENCE_DIR / "summary.json", summary)
    _write(EVIDENCE_DIR / "flow_summary.json", flow_summary)
    if args.require_valid and not summary.get("valid"):
        raise SystemExit("captured evidence did not verify as valid")
    print(json.dumps(summary, indent=2, sort_keys=True) if args.json else summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
