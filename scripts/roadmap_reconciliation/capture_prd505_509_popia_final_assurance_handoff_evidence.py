"""Capture PRD-5.5-5.9 POPIA final assurance evidence and handoff."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.modules.privacy_ops.assurance import build_default_privacy_final_assurance_report
from scripts.production_readiness.audit_prd505_509_popia_final_assurance_handoff import ROOT, audit

RECORD = ROOT / "docs/roadmap/production_readiness/prd_505_509_popia_final_assurance_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd5_privacy_live_data_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd5_popia_final_assurance_handoff.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-505-509-popia-final-assurance-handoff"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd505-509-popia-final-assurance-handoff", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.claim_prd505_509_popia_final_assurance_handoff:
        raise SystemExit("missing --claim-prd505-509-popia-final-assurance-handoff")

    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    now = datetime.now(timezone.utc).isoformat()
    assurance = build_default_privacy_final_assurance_report().to_payload()

    record = _load(RECORD)
    record.update({
        "privacy_final_assurance_evidence_recorded": True,
        "privacy_final_assurance_snapshot": assurance,
        "audit_2026_07_09_crosswalk_reconciled": True,
        "privacy_signoff_recorded": True,
        "prd5_final_reconciliation_recorded": True,
        "prd5_sequence_complete": True,
        "prd6_handoff_authorised": True,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "next_authorised_item": "PRD-6",
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
        "status": "prd5_popia_privacy_assurance_closed",
        "last_recorded_item": "PRD-5.5-5.9",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-6",
        "privacy_final_assurance_evidence_recorded": True,
        "audit_2026_07_09_crosswalk_reconciled": True,
        "privacy_signoff_recorded": True,
        "prd5_final_reconciliation_recorded": True,
        "prd5_sequence_complete": True,
        "prd6_handoff_authorised": True,
        "prd6_implementation_authorised": False,
    })
    for item in register.get("prd5_sequence", []):
        if item.get("prd_id") == "PRD-5.0-5.4":
            item.update({"status": "recorded", "authorised": True})
        if item.get("prd_id") == "PRD-5.5-5.9":
            item.update({"status": "recorded", "authorised": True})
    _write(REGISTER, register)

    prod = _load(PROD_REGISTER)
    prod.setdefault("current_truth", {})
    prod["current_truth"].update({
        "prd5_closed": True,
        "prd5_privacy_final_assurance_recorded": True,
        "prd5_final_reconciliation_recorded": True,
        "prd5_audit_2026_07_09_crosswalk_reconciled": True,
        "prd5_handoff_authorised": True,
        "prd5_next_authorised_item": "PRD-6",
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
        "status": "prd5_closed_prd6_handoff_authorised",
        "last_recorded_item": "PRD-5.5-5.9",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-6",
        "prd5_closed": True,
        "prd5_privacy_final_assurance_recorded": True,
        "prd5_final_reconciliation_recorded": True,
        "prd5_audit_2026_07_09_crosswalk_reconciled": True,
        "prd5_handoff_authorised": True,
        "prd5_next_authorised_item": "PRD-6",
    })
    _write(PROD_REGISTER, prod)

    after = audit(ROOT)
    summary = {
        "prd_id": "PRD-5.5-5.9",
        "captured_at": now,
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "next_authorised_item": after["next_authorised_item"],
        "register_next_authorised_item": after["register_next_authorised_item"],
        "privacy_final_assurance": assurance,
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
    _write(EVIDENCE_DIR / "privacy_final_assurance.json", assurance)
    _write(EVIDENCE_DIR / "summary.json", summary)

    if args.require_valid and not after["valid"]:
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
