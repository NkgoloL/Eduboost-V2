"""Capture PRD-8.0-8.4 performance, scale, and cost execution foundation evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.modules.performance_scale_cost import build_default_performance_scale_cost_readiness_report
from scripts.production_readiness.audit_prd800_804_performance_scale_cost_execution_foundation import ROOT, audit

RECORD = ROOT / "docs/roadmap/production_readiness/prd_800_804_performance_scale_cost_execution_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd8_performance_scale_cost_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd8_performance_scale_cost_execution_foundation.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-800-804-performance-scale-cost-execution-foundation"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd800-804-performance-scale-cost-execution-foundation", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.claim_prd800_804_performance_scale_cost_execution_foundation:
        raise SystemExit("missing --claim-prd800-804-performance-scale-cost-execution-foundation")

    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    now = datetime.now(timezone.utc).isoformat()
    readiness = build_default_performance_scale_cost_readiness_report().to_payload()

    record = _load(RECORD)
    record.update({
        "performance_scale_cost_foundation_recorded": True,
        "performance_scale_cost_evidence_recorded": True,
        "performance_scale_cost_readiness_snapshot": readiness,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "next_authorised_item": "PRD-8.5-8.9",
        "prd9_implementation_authorised": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "live_learner_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
    })
    _write(RECORD, record)

    register = _load(REGISTER)
    register.update({
        "status": "prd8_performance_scale_cost_foundation_recorded",
        "last_recorded_item": "PRD-8.0-8.4",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-8.5-8.9",
        "performance_scale_cost_foundation_recorded": True,
        "performance_scale_cost_evidence_recorded": True,
        "prd9_implementation_authorised": False,
    })
    for item in register.get("prd8_sequence", []):
        if item.get("prd_id") == "PRD-8.0-8.4":
            item.update({"status": "recorded", "authorised": True})
        if item.get("prd_id") == "PRD-8.5-8.9":
            item.update({"status": "authorised", "authorised": True})
    _write(REGISTER, register)

    prod = _load(PROD_REGISTER)
    prod.setdefault("current_truth", {})
    prod["current_truth"].update({
        "prd8_performance_scale_cost_foundation_recorded": True,
        "prd8_next_authorised_item": "PRD-8.5-8.9",
    })
    prod.setdefault("authority_boundaries", {})
    prod["authority_boundaries"].update({
        "prd9_implementation_authorised": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "live_learner_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
    })
    prod.update({
        "status": "prd8_performance_scale_cost_foundation_recorded",
        "last_recorded_item": "PRD-8.0-8.4",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-8.5-8.9",
        "prd8_performance_scale_cost_foundation_recorded": True,
        "prd8_next_authorised_item": "PRD-8.5-8.9",
    })
    _write(PROD_REGISTER, prod)

    after = audit(ROOT)
    summary = {
        "prd_id": "PRD-8.0-8.4",
        "captured_at": now,
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "next_authorised_item": after["next_authorised_item"],
        "register_next_authorised_item": after["register_next_authorised_item"],
        "performance_scale_cost_readiness": readiness,
        "boundaries": {key: after[key] for key in (
            "prd9_implementation_authorised",
            "production_release_authorised",
            "deployment_authorised",
            "release_tag_authorised",
            "public_beta_authorised",
            "live_learner_traffic_authorised",
            "billing_launch_authorised",
            "live_payment_processing_authorised",
        )},
    }
    _write(SUMMARY, summary)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "audit_before.json", before)
    _write(EVIDENCE_DIR / "audit_after.json", after)
    _write(EVIDENCE_DIR / "performance_scale_cost_readiness.json", readiness)
    _write(EVIDENCE_DIR / "summary.json", summary)

    if args.require_valid and not after["valid"]:
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
