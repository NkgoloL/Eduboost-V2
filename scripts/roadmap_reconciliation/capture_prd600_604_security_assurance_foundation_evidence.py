"""Capture PRD-6.0-6.4 security assurance foundation evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.modules.security_assurance import build_default_security_assurance_readiness_report
from scripts.production_readiness.audit_prd600_604_security_assurance_foundation import ROOT, audit

RECORD = ROOT / "docs/roadmap/production_readiness/prd_600_604_security_assurance_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd6_security_assurance_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd6_security_assurance_foundation.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-600-604-security-assurance-foundation"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd600-604-security-assurance-foundation", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.claim_prd600_604_security_assurance_foundation:
        raise SystemExit("missing --claim-prd600-604-security-assurance-foundation")

    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    now = datetime.now(timezone.utc).isoformat()
    readiness = build_default_security_assurance_readiness_report().to_payload()

    record = _load(RECORD)
    record.update({
        "security_assurance_foundation_recorded": True,
        "security_assurance_evidence_recorded": True,
        "security_assurance_readiness_snapshot": readiness,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "next_authorised_item": "PRD-6.5-6.9",
        "prd7_implementation_authorised": False,
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
        "status": "prd6_security_assurance_foundation_recorded",
        "last_recorded_item": "PRD-6.0-6.4",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-6.5-6.9",
        "security_assurance_foundation_recorded": True,
        "security_assurance_evidence_recorded": True,
        "prd7_implementation_authorised": False,
    })
    for item in register.get("prd6_sequence", []):
        if item.get("prd_id") == "PRD-6.0-6.4":
            item.update({"status": "recorded", "authorised": True})
        if item.get("prd_id") == "PRD-6.5-6.9":
            item.update({"status": "authorised", "authorised": True})
    _write(REGISTER, register)

    prod = _load(PROD_REGISTER)
    prod.setdefault("current_truth", {})
    prod["current_truth"].update({
        "prd6_started": True,
        "prd6_security_assurance_foundation_recorded": True,
        "prd6_next_authorised_item": "PRD-6.5-6.9",
    })
    prod.setdefault("authority_boundaries", {})
    prod["authority_boundaries"].update({
        "prd7_implementation_authorised": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "live_learner_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
    })
    prod.update({
        "status": "prd6_security_assurance_foundation_recorded",
        "last_recorded_item": "PRD-6.0-6.4",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-6.5-6.9",
        "prd6_started": True,
        "prd6_security_assurance_foundation_recorded": True,
        "prd6_next_authorised_item": "PRD-6.5-6.9",
    })
    _write(PROD_REGISTER, prod)

    after = audit(ROOT)
    summary = {
        "prd_id": "PRD-6.0-6.4",
        "captured_at": now,
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "next_authorised_item": after["next_authorised_item"],
        "register_next_authorised_item": after["register_next_authorised_item"],
        "security_assurance_readiness": readiness,
        "boundaries": {key: after[key] for key in (
            "prd7_implementation_authorised",
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
    _write(EVIDENCE_DIR / "security_assurance_readiness.json", readiness)
    _write(EVIDENCE_DIR / "summary.json", summary)

    if args.require_valid and not after["valid"]:
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
