"""Capture PRD-11.0-11.4 production release/deployment preflight evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.modules.production_release import build_default_production_release_preflight_report
from scripts.production_readiness.audit_prd1100_1104_production_release_deployment_preflight_foundation import ROOT, audit

RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100_1104_production_release_deployment_preflight_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_production_release_deployment_preflight_foundation.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100-1104-production-release-deployment-preflight-foundation"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd1100-1104-production-release-deployment-preflight-foundation", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1100_1104_production_release_deployment_preflight_foundation:
        raise SystemExit("missing --claim-prd1100-1104-production-release-deployment-preflight-foundation")
    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    now = datetime.now(timezone.utc).isoformat()
    preflight = build_default_production_release_preflight_report().to_payload()

    record = _load(RECORD)
    record.update({
        "status": "prd11_production_release_preflight_evidence_recorded",
        "production_release_preflight_evidence_recorded": True,
        "production_release_preflight_snapshot": preflight,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "controlled_beta_live_traffic_authorised": True,
        "live_learner_traffic_authorised": True,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "prd12_implementation_authorised": False,
        "next_authorised_item": "PRD-11.5-11.9",
    })
    _write(RECORD, record)

    register = _load(REGISTER)
    register.update({
        "status": "prd11_production_release_preflight_evidence_recorded",
        "last_recorded_item": "PRD-11.0-11.4",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-11.5-11.9",
        "prd11_production_release_preflight_foundation_recorded": True,
        "production_release_preflight_evidence_recorded": True,
        "controlled_beta_live_traffic_authorised": True,
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
    for item in register.get("prd11_sequence", []):
        if item.get("prd_id") == "PRD-11.0-11.4":
            item.update({"status": "recorded", "authorised": True})
        if item.get("prd_id") == "PRD-11.5-11.9":
            item.update({"status": "authorised_next", "authorised": True})
    _write(REGISTER, register)

    prod = _load(PROD_REGISTER)
    prod.setdefault("current_truth", {})
    prod["current_truth"].update({
        "prd11_started": True,
        "prd11_production_release_preflight_foundation_recorded": True,
        "prd11_production_release_preflight_evidence_recorded": True,
        "prd11_next_authorised_item": "PRD-11.5-11.9",
    })
    prod.setdefault("authority_boundaries", {})
    prod["authority_boundaries"].update({
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "live_learner_traffic_authorised": True,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "prd12_implementation_authorised": False,
    })
    prod.update({
        "status": "prd11_production_release_preflight_evidence_recorded",
        "last_recorded_item": "PRD-11.0-11.4",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-11.5-11.9",
    })
    _write(PROD_REGISTER, prod)

    after = audit(ROOT)
    summary = {
        "prd_id": "PRD-11.0-11.4",
        "captured_at": now,
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "next_authorised_item": after["next_authorised_item"],
        "register_next_authorised_item": after["register_next_authorised_item"],
        "production_release_preflight": preflight,
    }
    _write(SUMMARY, summary)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "audit_before.json", before)
    _write(EVIDENCE_DIR / "audit_after.json", after)
    _write(EVIDENCE_DIR / "production_release_preflight.json", preflight)
    _write(EVIDENCE_DIR / "summary.json", summary)
    if args.require_valid and not after["valid"]:
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
