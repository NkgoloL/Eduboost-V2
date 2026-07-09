"""Capture PRD-6.5-6.9 security final assurance evidence and handoff."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.modules.security_assurance.assurance import build_default_security_final_assurance_report
from scripts.production_readiness.audit_prd605_609_security_final_assurance_handoff import ROOT, audit

RECORD = ROOT / "docs/roadmap/production_readiness/prd_605_609_security_final_assurance_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd6_security_assurance_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd6_security_final_assurance_handoff.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-605-609-security-final-assurance-handoff"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd605-609-security-final-assurance-handoff", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.claim_prd605_609_security_final_assurance_handoff:
        raise SystemExit("missing --claim-prd605-609-security-final-assurance-handoff")

    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    now = datetime.now(timezone.utc).isoformat()
    assurance = build_default_security_final_assurance_report().to_payload()

    record = _load(RECORD)
    record.update({
        "security_final_assurance_evidence_recorded": True,
        "security_final_assurance_snapshot": assurance,
        "external_or_independent_review_recorded": True,
        "security_signoff_recorded": True,
        "prd6_final_reconciliation_recorded": True,
        "prd6_sequence_complete": True,
        "prd7_handoff_authorised": True,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "next_authorised_item": "PRD-7",
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
        "status": "prd6_security_assurance_closed",
        "last_recorded_item": "PRD-6.5-6.9",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-7",
        "security_final_assurance_evidence_recorded": True,
        "external_or_independent_review_recorded": True,
        "security_signoff_recorded": True,
        "prd6_final_reconciliation_recorded": True,
        "prd6_sequence_complete": True,
        "prd7_handoff_authorised": True,
        "prd7_implementation_authorised": False,
    })
    for item in register.get("prd6_sequence", []):
        if item.get("prd_id") == "PRD-6.0-6.4":
            item.update({"status": "recorded", "authorised": True})
        if item.get("prd_id") == "PRD-6.5-6.9":
            item.update({"status": "recorded", "authorised": True})
    _write(REGISTER, register)

    prod = _load(PROD_REGISTER)
    prod.setdefault("current_truth", {})
    prod["current_truth"].update({
        "prd6_closed": True,
        "prd6_security_final_assurance_recorded": True,
        "prd6_external_or_independent_review_recorded": True,
        "prd6_final_reconciliation_recorded": True,
        "prd6_handoff_authorised": True,
        "prd6_next_authorised_item": "PRD-7",
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
        "status": "prd6_closed_prd7_handoff_authorised",
        "last_recorded_item": "PRD-6.5-6.9",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-7",
        "prd6_closed": True,
        "prd6_security_final_assurance_recorded": True,
        "prd6_external_or_independent_review_recorded": True,
        "prd6_final_reconciliation_recorded": True,
        "prd6_handoff_authorised": True,
        "prd6_next_authorised_item": "PRD-7",
    })
    _write(PROD_REGISTER, prod)

    after = audit(ROOT)
    summary = {
        "prd_id": "PRD-6.5-6.9",
        "captured_at": now,
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "next_authorised_item": after["next_authorised_item"],
        "register_next_authorised_item": after["register_next_authorised_item"],
        "security_final_assurance": assurance,
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
    _write(EVIDENCE_DIR / "security_final_assurance.json", assurance)
    _write(EVIDENCE_DIR / "summary.json", summary)

    if args.require_valid and not after["valid"]:
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
