"""Capture PRD-5.0-5.4 POPIA live-data privacy operations foundation evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.modules.privacy_ops.readiness import build_default_privacy_live_data_readiness_report
from scripts.production_readiness.audit_prd500_504_popia_live_data_privacy_ops_foundation import ROOT, audit

RECORD = ROOT / "docs/roadmap/production_readiness/prd_500_504_popia_live_data_privacy_ops_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd5_privacy_live_data_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd5_popia_live_data_privacy_ops_foundation.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-500-504-popia-live-data-privacy-ops-foundation"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd500-504-popia-live-data-privacy-ops-foundation", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.claim_prd500_504_popia_live_data_privacy_ops_foundation:
        raise SystemExit("missing --claim-prd500-504-popia-live-data-privacy-ops-foundation")

    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    now = datetime.now(timezone.utc).isoformat()
    readiness = build_default_privacy_live_data_readiness_report().to_payload()

    record = _load(RECORD)
    record.update({
        "live_data_privacy_foundation_recorded": True,
        "privacy_live_data_evidence_recorded": True,
        "privacy_live_data_readiness_snapshot": readiness,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "next_authorised_item": "PRD-5.5-5.9",
        "prd6_implementation_authorised": False,
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
        "status": "prd5_live_data_privacy_foundation_recorded",
        "last_recorded_item": "PRD-5.0-5.4",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-5.5-5.9",
        "live_data_privacy_foundation_recorded": True,
        "privacy_live_data_evidence_recorded": True,
    })
    for item in register.get("prd5_sequence", []):
        if item.get("prd_id") == "PRD-5.0-5.4":
            item.update({"status": "recorded", "authorised": True})
        if item.get("prd_id") == "PRD-5.5-5.9":
            item.update({"status": "authorised", "authorised": True})
    _write(REGISTER, register)

    prod = _load(PROD_REGISTER)
    prod.setdefault("current_truth", {})
    prod["current_truth"].update({
        "prd5_live_data_privacy_foundation_recorded": True,
        "prd5_next_authorised_item": "PRD-5.5-5.9",
    })
    prod.setdefault("authority_boundaries", {})
    prod["authority_boundaries"].update({
        "prd6_implementation_authorised": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "live_learner_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
    })
    prod.update({
        "last_recorded_item": "PRD-5.0-5.4",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-5.5-5.9",
        "prd5_live_data_privacy_foundation_recorded": True,
        "prd5_next_authorised_item": "PRD-5.5-5.9",
    })
    _write(PROD_REGISTER, prod)

    after = audit(ROOT)
    summary = {
        "prd_id": "PRD-5.0-5.4",
        "captured_at": now,
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "next_authorised_item": after["next_authorised_item"],
        "register_next_authorised_item": after["register_next_authorised_item"],
        "privacy_live_data_readiness": readiness,
        "boundaries": {key: after[key] for key in (
            "prd6_implementation_authorised",
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
    _write(EVIDENCE_DIR / "privacy_live_data_readiness.json", readiness)
    _write(EVIDENCE_DIR / "summary.json", summary)

    if args.require_valid and not after["valid"]:
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
