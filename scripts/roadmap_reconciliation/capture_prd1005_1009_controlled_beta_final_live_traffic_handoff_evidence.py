"""Capture PRD-10.5-10.9 controlled beta final live-traffic handoff evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.modules.controlled_beta import build_default_controlled_beta_final_authorisation_report
from scripts.production_readiness.audit_prd1005_1009_controlled_beta_final_live_traffic_handoff import ROOT, audit

RECORD = ROOT / "docs/roadmap/production_readiness/prd_1005_1009_controlled_beta_final_live_traffic_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd10_controlled_beta_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd10_controlled_beta_final_live_traffic_handoff.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1005-1009-controlled-beta-final-live-traffic-handoff"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd1005-1009-controlled-beta-final-live-traffic-handoff", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1005_1009_controlled_beta_final_live_traffic_handoff:
        raise SystemExit("missing --claim-prd1005-1009-controlled-beta-final-live-traffic-handoff")
    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    now = datetime.now(timezone.utc).isoformat()
    final_authorisation = build_default_controlled_beta_final_authorisation_report().to_payload()
    record = _load(RECORD)
    record.update({
        "status": "prd10_controlled_beta_live_traffic_authorised",
        "controlled_beta_final_evidence_recorded": True,
        "controlled_beta_final_authorisation_snapshot": final_authorisation,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "controlled_beta_live_traffic_authorised": True,
        "live_learner_traffic_authorised": True,
        "prd10_final_reconciliation_recorded": True,
        "prd10_sequence_complete": True,
        "prd11_handoff_authorised": True,
        "prd11_implementation_authorised": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "next_authorised_item": "PRD-11",
    })
    _write(RECORD, record)

    register = _load(REGISTER)
    register.update({
        "status": "prd10_closed_controlled_beta_live_traffic_authorised",
        "last_recorded_item": "PRD-10.5-10.9",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-11",
        "controlled_beta_final_authority_recorded": True,
        "controlled_beta_final_evidence_recorded": True,
        "controlled_beta_live_traffic_authorised": True,
        "live_learner_traffic_authorised": True,
        "prd10_final_reconciliation_recorded": True,
        "prd10_sequence_complete": True,
        "prd11_handoff_authorised": True,
        "prd11_implementation_authorised": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
    })
    for item in register.get("prd10_sequence", []):
        if item.get("prd_id") in {"PRD-10.0-10.4", "PRD-10.5-10.9"}:
            item.update({"status": "recorded", "authorised": True})
    _write(REGISTER, register)

    prod = _load(PROD_REGISTER)
    prod.setdefault("current_truth", {})
    prod["current_truth"].update({
        "prd10_started": True,
        "prd10_controlled_beta_preflight_foundation_recorded": True,
        "prd10_controlled_beta_preflight_evidence_recorded": True,
        "prd10_controlled_beta_final_authority_recorded": True,
        "prd10_controlled_beta_final_evidence_recorded": True,
        "prd10_live_learner_traffic_authorised": True,
        "prd10_final_reconciliation_recorded": True,
        "prd10_sequence_complete": True,
        "prd10_closed": True,
        "prd10_handoff_authorised": True,
        "prd10_next_authorised_item": "PRD-11",
    })
    prod.setdefault("authority_boundaries", {})
    prod["authority_boundaries"].update({
        "prd11_implementation_authorised": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "live_learner_traffic_authorised": True,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
    })
    prod.update({
        "status": "prd10_closed_controlled_beta_live_traffic_authorised",
        "last_recorded_item": "PRD-10.5-10.9",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-11",
    })
    _write(PROD_REGISTER, prod)

    after = audit(ROOT)
    summary = {
        "prd_id": "PRD-10.5-10.9",
        "captured_at": now,
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "next_authorised_item": after["next_authorised_item"],
        "register_next_authorised_item": after["register_next_authorised_item"],
        "controlled_beta_final_authorisation": final_authorisation,
    }
    _write(SUMMARY, summary)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "audit_before.json", before)
    _write(EVIDENCE_DIR / "audit_after.json", after)
    _write(EVIDENCE_DIR / "controlled_beta_final_authorisation.json", final_authorisation)
    _write(EVIDENCE_DIR / "summary.json", summary)
    if args.require_valid and not after["valid"]:
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
