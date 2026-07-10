"""Capture PRD-11.0R true-state runtime baseline restoration evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.modules.production_release import build_default_true_state_runtime_baseline_report
from scripts.production_readiness.audit_prd1100r_true_state_runtime_baseline_restoration import ROOT, audit
from scripts.production_readiness.collect_prd1100r_true_state_runtime_baseline import collect_baseline

RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_true_state_runtime_baseline_restoration_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_true_state_runtime_baseline_restoration.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-true-state-runtime-baseline-restoration"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd1100r-true-state-runtime-baseline-restoration", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--run-expensive-checks", action="store_true")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1100r_true_state_runtime_baseline_restoration:
        raise SystemExit("missing --claim-prd1100r-true-state-runtime-baseline-restoration")
    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    now = datetime.now(timezone.utc).isoformat()
    hold = build_default_true_state_runtime_baseline_report().to_payload()
    baseline = collect_baseline(ROOT, run_expensive_checks=args.run_expensive_checks)

    record = _load(RECORD)
    record.update({
        "status": "prd11_true_state_runtime_baseline_restoration_evidence_recorded",
        "true_state_runtime_baseline_evidence_recorded": True,
        "true_state_runtime_baseline_snapshot": baseline,
        "operational_hold_snapshot": hold,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "controlled_beta_activation_operational_hold": True,
        "controlled_beta_live_traffic_authorised": True,
        "live_learner_traffic_authorised": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
        "baseline_green_required_before_prd1100_evidence_capture": True,
        "runtime_baseline_green": bool(baseline.get("runtime_baseline_green")),
        "runtime_baseline_status": baseline.get("overall_status"),
        "runtime_evidence_mode": "actual_probe_evidence_required_not_constant_status",
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "prd12_implementation_authorised": False,
        "next_authorised_item": "PRD-11.0R.RUNTIME-RESTORE",
    })
    _write(RECORD, record)

    register = _load(REGISTER)
    register.update({
        "status": "prd11_true_state_runtime_baseline_operational_hold_recorded",
        "last_recorded_item": "PRD-11.0R",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-11.0R.RUNTIME-RESTORE",
        "true_state_runtime_baseline_restoration_authority_recorded": True,
        "true_state_runtime_baseline_evidence_recorded": True,
        "controlled_beta_activation_operational_hold": True,
        "controlled_beta_live_traffic_authorised": True,
        "live_learner_traffic_authorised": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
        "runtime_baseline_green": bool(baseline.get("runtime_baseline_green")),
        "runtime_baseline_status": baseline.get("overall_status"),
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "prd12_implementation_authorised": False,
    })
    sequence = register.setdefault("prd11_sequence", [])
    if not any(item.get("prd_id") == "PRD-11.0R" for item in sequence):
        sequence.insert(0, {"prd_id": "PRD-11.0R", "title": "True-state runtime baseline restoration and evidence hardening", "status": "recorded", "authorised": True})
    for item in sequence:
        if item.get("prd_id") == "PRD-11.0R":
            item.update({"status": "recorded_operational_hold", "authorised": True})
        if item.get("prd_id") == "PRD-11.0-11.4":
            item.update({"status": "blocked_until_runtime_baseline_green", "authorised": True})
    _write(REGISTER, register)

    prod = _load(PROD_REGISTER)
    prod.setdefault("current_truth", {})
    prod["current_truth"].update({
        "prd11_0r_true_state_runtime_baseline_restoration_recorded": True,
        "prd11_0r_true_state_runtime_baseline_evidence_recorded": True,
        "prd11_0r_runtime_baseline_green": bool(baseline.get("runtime_baseline_green")),
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
        "prd11_next_authorised_item": "PRD-11.0R.RUNTIME-RESTORE",
    })
    prod.setdefault("authority_boundaries", {})
    prod["authority_boundaries"].update({
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_authorised": True,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "prd12_implementation_authorised": False,
    })
    prod.update({
        "status": "prd11_true_state_runtime_baseline_operational_hold_recorded",
        "last_recorded_item": "PRD-11.0R",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-11.0R.RUNTIME-RESTORE",
    })
    _write(PROD_REGISTER, prod)

    after = audit(ROOT)
    summary = {
        "prd_id": "PRD-11.0R",
        "captured_at": now,
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "next_authorised_item": after["next_authorised_item"],
        "register_next_authorised_item": after["register_next_authorised_item"],
        "runtime_baseline_green": bool(baseline.get("runtime_baseline_green")),
        "runtime_baseline_status": baseline.get("overall_status"),
        "controlled_beta_activation_operational_hold": True,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
        "baseline_blockers": baseline.get("blockers", []),
        "true_state_runtime_baseline": baseline,
    }
    _write(SUMMARY, summary)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "audit_before.json", before)
    _write(EVIDENCE_DIR / "audit_after.json", after)
    _write(EVIDENCE_DIR / "operational_hold.json", hold)
    _write(EVIDENCE_DIR / "true_state_runtime_baseline.json", baseline)
    _write(EVIDENCE_DIR / "summary.json", summary)
    if args.require_valid and not after["valid"]:
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
