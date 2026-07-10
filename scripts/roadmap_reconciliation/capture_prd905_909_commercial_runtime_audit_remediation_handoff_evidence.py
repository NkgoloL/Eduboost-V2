"""Capture PRD-9.5-9.9 commercial runtime audit remediation evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.modules.commercial_launch import build_default_commercial_runtime_audit_remediation_report
from scripts.production_readiness.audit_prd905_909_commercial_runtime_audit_remediation_handoff import ROOT, audit

RECORD = ROOT / "docs/roadmap/production_readiness/prd_905_909_commercial_runtime_audit_remediation_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd9_commercial_launch_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd9_commercial_runtime_audit_remediation_handoff.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-905-909-commercial-runtime-audit-remediation-handoff"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd905-909-commercial-runtime-audit-remediation-handoff", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.claim_prd905_909_commercial_runtime_audit_remediation_handoff:
        raise SystemExit("missing --claim-prd905-909-commercial-runtime-audit-remediation-handoff")

    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    now = datetime.now(timezone.utc).isoformat()
    remediation = build_default_commercial_runtime_audit_remediation_report().to_payload()

    record = _load(RECORD)
    record.update({
        "status": "prd9_commercial_runtime_audit_remediation_handoff_recorded",
        "commercial_final_evidence_recorded": True,
        "prd9_final_reconciliation_recorded": True,
        "prd9_sequence_complete": True,
        "prd10_handoff_authorised": True,
        "commercial_runtime_blockers_remediated": True,
        "audit_2026_07_09_runtime_findings_reconciled": True,
        "commercial_runtime_audit_remediation_snapshot": remediation,
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "next_authorised_item": "PRD-10",
        "prd10_implementation_authorised": False,
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
        "status": "prd9_closed_handoff_to_prd10_authorised",
        "last_recorded_item": "PRD-9.5-9.9",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-10",
        "commercial_runtime_blockers_remediated": True,
        "commercial_final_evidence_recorded": True,
        "prd9_final_reconciliation_recorded": True,
        "prd9_sequence_complete": True,
        "prd10_handoff_authorised": True,
        "prd10_implementation_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
    })
    for item in register.get("prd9_sequence", []):
        if item.get("prd_id") == "PRD-9.0-9.4":
            item.update({"status": "recorded", "authorised": True})
        if item.get("prd_id") == "PRD-9.5-9.9":
            item.update({"status": "recorded", "authorised": True})
    _write(REGISTER, register)

    prod = _load(PROD_REGISTER)
    prod.setdefault("current_truth", {})
    prod["current_truth"].update({
        "prd9_closed": True,
        "prd9_final_reconciliation_recorded": True,
        "prd9_handoff_authorised": True,
        "prd9_commercial_runtime_blockers_remediated": True,
        "prd9_audit_2026_07_09_runtime_findings_reconciled": True,
        "prd9_next_authorised_item": "PRD-10",
    })
    prod.setdefault("authority_boundaries", {})
    prod["authority_boundaries"].update({
        "prd10_implementation_authorised": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "live_learner_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
    })
    prod.update({
        "status": "prd9_closed_handoff_to_prd10_authorised",
        "last_recorded_item": "PRD-9.5-9.9",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-10",
        "prd9_closed": True,
        "prd9_final_reconciliation_recorded": True,
        "prd9_handoff_authorised": True,
        "prd9_next_authorised_item": "PRD-10",
    })
    _write(PROD_REGISTER, prod)

    after = audit(ROOT)
    summary = {
        "prd_id": "PRD-9.5-9.9",
        "captured_at": now,
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "next_authorised_item": after["next_authorised_item"],
        "register_next_authorised_item": after["register_next_authorised_item"],
        "commercial_runtime_audit_remediation": remediation,
    }
    _write(SUMMARY, summary)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "audit_before.json", before)
    _write(EVIDENCE_DIR / "audit_after.json", after)
    _write(EVIDENCE_DIR / "commercial_runtime_audit_remediation.json", remediation)
    _write(EVIDENCE_DIR / "summary.json", summary)

    if args.require_valid and not after["valid"]:
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
