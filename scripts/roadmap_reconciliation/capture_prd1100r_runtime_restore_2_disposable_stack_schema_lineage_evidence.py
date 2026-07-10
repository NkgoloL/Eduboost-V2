"""Capture PRD-11.0R.RUNTIME-RESTORE-2 disposable stack/schema-lineage evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.production_readiness.audit_prd1100r_runtime_restore_2_disposable_stack_schema_lineage import ROOT, audit
from scripts.production_readiness.collect_prd1100r_true_state_runtime_baseline import collect_baseline
from scripts.runtime.disposable_stack_lineage import verify_disposable_stack_lineage_contract

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE-2"
NEXT_ITEM = "PRD-11.0R.RUNTIME-RESTORE-3"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_2_disposable_stack_schema_lineage_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_2_disposable_stack_schema_lineage.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-2-disposable-stack-schema-lineage"
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
    parser.add_argument("--claim-prd1100r-runtime-restore-2-disposable-stack-schema-lineage", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--run-expensive-checks", action="store_true")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1100r_runtime_restore_2_disposable_stack_schema_lineage:
        raise SystemExit("missing --claim-prd1100r-runtime-restore-2-disposable-stack-schema-lineage")
    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    now = datetime.now(timezone.utc).isoformat()
    lineage_contract = verify_disposable_stack_lineage_contract(ROOT, require_live=False)
    baseline = collect_baseline(ROOT, run_expensive_checks=args.run_expensive_checks)

    record = _load(RECORD)
    record.update({
        "status": "disposable_stack_schema_lineage_evidence_recorded",
        "disposable_stack_schema_lineage_evidence_recorded": True,
        "disposable_stack_schema_lineage_contract_snapshot": lineage_contract,
        "runtime_baseline_snapshot": baseline,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "runtime_baseline_green": bool(baseline.get("runtime_baseline_green")),
        "runtime_baseline_status": baseline.get("overall_status"),
        "live_lineage_schema_green": bool(lineage_contract.get("live_lineage_schema_green")),
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
            "status": "prd11_runtime_restore_2_evidence_recorded",
            "last_recorded_item": PRD_ID,
            "last_recorded_at": now,
            "next_authorised_item": NEXT_ITEM,
            "runtime_restore_2_disposable_stack_schema_lineage_authority_recorded": True,
            "runtime_restore_2_disposable_stack_schema_lineage_evidence_recorded": True,
            "runtime_baseline_green": bool(baseline.get("runtime_baseline_green")),
            "runtime_baseline_status": baseline.get("overall_status"),
            "controlled_beta_activation_operational_hold": True,
            "live_learner_traffic_operationally_safe": False,
            "production_release_evidence_blocked_until_runtime_baseline_green": True,
        })
        payload.setdefault("authority_boundaries", {}).update(FALSE_BOUNDARIES)
        payload.setdefault("current_truth", {}).update({
            "prd11_runtime_restore_1_evidence_recorded": True,
            "prd11_runtime_restore_2_authority_recorded": True,
            "prd11_runtime_restore_2_evidence_recorded": True,
            "runtime_restore_1_runtime_stack_db_lineage_readiness_evidence_recorded": True,
            "runtime_restore_2_disposable_stack_schema_lineage_evidence_recorded": True,
            "runtime_baseline_green": bool(baseline.get("runtime_baseline_green")),
            "controlled_beta_activation_operational_hold": True,
            "live_learner_traffic_operationally_safe": False,
            "production_release_evidence_blocked_until_runtime_baseline_green": True,
            "prd11_next_authorised_item": NEXT_ITEM,
        })
        if path == REGISTER:
            sequence = payload.setdefault("prd11_sequence", [])
            if not any(item.get("prd_id") == PRD_ID for item in sequence):
                sequence.append({"prd_id": PRD_ID, "title": "Disposable stack execution and schema lineage reconciliation", "status": "evidence_recorded", "authorised": True})
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
        "runtime_baseline_green": bool(baseline.get("runtime_baseline_green")),
        "runtime_baseline_status": baseline.get("overall_status"),
        "baseline_blockers": baseline.get("blockers", []),
        "disposable_stack_schema_lineage_contract_valid": lineage_contract.get("contract_valid"),
        "live_lineage_schema_green": lineage_contract.get("live_lineage_schema_green"),
        "controlled_beta_activation_operational_hold": True,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
    }
    _write(SUMMARY, provisional_summary)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "audit_before.json", before)
    _write(EVIDENCE_DIR / "disposable_stack_schema_lineage_contract.json", lineage_contract)
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
