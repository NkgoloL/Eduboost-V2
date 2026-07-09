"""Capture PRD-4.0-4.4 content/CAPS/educational quality readiness evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.modules.content_quality.readiness import ContentQualityReadinessInputs, build_content_quality_readiness_report, build_default_grade4_maths_readiness_report
from scripts.production_readiness.audit_prd400_404_content_caps_quality_readiness_foundation import ROOT, audit

RECORD = ROOT / "docs/roadmap/production_readiness/prd_400_404_content_caps_quality_readiness_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd4_content_quality_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-400-404-content-caps-quality-readiness-foundation"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd4_content_caps_quality_readiness_foundation.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd400-404-content-caps-quality-readiness-foundation", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.claim_prd400_404_content_caps_quality_readiness_foundation:
        raise SystemExit("missing --claim-prd400-404-content-caps-quality-readiness-foundation")
    before = audit(ROOT)
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    now = datetime.now(timezone.utc).isoformat()
    accepted = build_default_grade4_maths_readiness_report().to_payload()
    blocked = build_content_quality_readiness_report(ContentQualityReadinessInputs()).to_payload()

    record = _load(RECORD)
    record.update({
        "status": "recorded",
        "content_quality_foundation_recorded": True,
        "content_quality_evidence_recorded": True,
        "recorded_at": now,
        "recorded_by": args.prd_owner,
        "target_branch": args.target_branch,
        "next_authorised_item": "PRD-4.5-4.9",
        "prd5_implementation_authorised": False,
    })
    _write(RECORD, record)

    register = _load(REGISTER)
    register.update({
        "status": "prd4_content_quality_foundation_recorded",
        "last_recorded_item": "PRD-4.0-4.4",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-4.5-4.9",
        "content_quality_foundation_recorded": True,
        "content_quality_evidence_recorded": True,
        "prd5_implementation_authorised": False,
    })
    for item in register.get("prd4_sequence", []):
        if item.get("prd_id") == "PRD-4.0-4.4":
            item["status"] = "recorded"
            item["authorised"] = True
        if item.get("prd_id") == "PRD-4.5-4.9":
            item["status"] = "authorised"
            item["authorised"] = True
    _write(REGISTER, register)

    prod = _load(PROD_REGISTER)
    prod["last_recorded_item"] = "PRD-4.0-4.4"
    prod["last_recorded_at"] = now
    prod["next_authorised_item"] = "PRD-4.5-4.9"
    prod.setdefault("current_truth", {})
    prod["current_truth"].update({
        "prd4_content_quality_foundation_started": True,
        "prd4_content_quality_foundation_recorded": True,
        "prd4_next_authorised_item": "PRD-4.5-4.9",
    })
    prod.setdefault("authority_boundaries", {})
    prod["authority_boundaries"].update({
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "live_learner_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "prd5_implementation_authorised": False,
    })
    _write(PROD_REGISTER, prod)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "prd400_404_audit_before_capture.json", before)
    _write(EVIDENCE_DIR / "content_quality_readiness_report.json", accepted)
    _write(EVIDENCE_DIR / "content_quality_blocked_report.json", blocked)
    after = audit(ROOT)
    _write(EVIDENCE_DIR / "prd400_404_audit_after_capture.json", after)
    _write(SUMMARY, {
        "prd_id": "PRD-4.0-4.4",
        "recorded_at": now,
        "recorded_by": args.prd_owner,
        "target_branch": args.target_branch,
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "next_authorised_item": after["register_next_authorised_item"],
        "content_quality_readiness_report": accepted,
        "content_quality_blocked_report": blocked,
    })

    if args.require_valid and not after["valid"]:
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
