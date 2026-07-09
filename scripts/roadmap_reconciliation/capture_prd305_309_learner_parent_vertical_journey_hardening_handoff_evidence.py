"""Capture PRD-3.5-3.9 learner/parent vertical journey hardening evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.modules.vertical_journey.hardening import build_vertical_journey_hardening_report
from app.modules.vertical_journey.service import VerticalJourneyInputs, build_vertical_journey_snapshot
from scripts.production_readiness.audit_prd305_309_learner_parent_vertical_journey_hardening_handoff import ROOT, audit

RECORD = ROOT / "docs/roadmap/production_readiness/prd_305_309_learner_parent_vertical_journey_hardening_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd3_vertical_journey_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-305-309-learner-parent-vertical-journey-hardening-handoff"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd3_learner_parent_vertical_journey_hardening_handoff.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _complete_inputs() -> VerticalJourneyInputs:
    return VerticalJourneyInputs(
        learner_id="prd3-final-learner",
        guardian_id="prd3-final-guardian",
        learner_profile_created=True,
        guardian_consent_active=True,
        learner_onboarding_completed=True,
        diagnostic_completed=True,
        runtime_kg_gap_profile_available=True,
        lesson_generated=True,
        lesson_completed=True,
        assessment_attempted=True,
        mastery_updated=True,
        study_plan_generated=True,
        gamification_profile_available=True,
        parent_progress_report_available=True,
        popia_export_path_available=True,
        popia_erasure_path_available=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd305-309-learner-parent-vertical-journey-hardening-handoff", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    before = audit(ROOT)
    if not args.claim_prd305_309_learner_parent_vertical_journey_hardening_handoff:
        raise SystemExit("missing --claim-prd305-309-learner-parent-vertical-journey-hardening-handoff")
    if not before["authority_valid"]:
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    now = datetime.now(timezone.utc).isoformat()
    complete_snapshot = build_vertical_journey_snapshot(_complete_inputs())
    hardening_report = build_vertical_journey_hardening_report(complete_snapshot).to_payload()
    blocked_snapshot = build_vertical_journey_snapshot(
        VerticalJourneyInputs(
            learner_id="prd3-blocked-learner",
            guardian_id="prd3-final-guardian",
            learner_profile_created=True,
            guardian_consent_active=False,
        )
    )
    blocked_report = build_vertical_journey_hardening_report(blocked_snapshot).to_payload()

    record = _load(RECORD)
    record.update({
        "status": "recorded",
        "vertical_journey_final_hardening_recorded": True,
        "vertical_journey_final_evidence_recorded": True,
        "prd3_final_reconciliation_recorded": True,
        "prd3_sequence_complete": True,
        "prd4_handoff_authorised": True,
        "recorded_at": now,
        "recorded_by": args.prd_owner,
        "target_branch": args.target_branch,
        "next_authorised_item": "PRD-4",
        "prd4_implementation_authorised": False,
    })
    _write(RECORD, record)

    register = _load(REGISTER)
    register.update({
        "status": "prd3_vertical_journey_hardening_closed",
        "last_recorded_item": "PRD-3.5-3.9",
        "last_recorded_at": now,
        "next_authorised_item": "PRD-4",
        "vertical_journey_final_hardening_recorded": True,
        "vertical_journey_final_evidence_recorded": True,
        "prd3_sequence_complete": True,
        "prd4_handoff_authorised": True,
        "prd4_implementation_authorised": False,
    })
    for item in register.get("prd3_sequence", []):
        if item.get("prd_id") == "PRD-3.5-3.9":
            item["status"] = "recorded"
            item["authorised"] = True
    _write(REGISTER, register)

    prod = _load(PROD_REGISTER)
    prod["last_recorded_item"] = "PRD-3.5-3.9"
    prod["last_recorded_at"] = now
    prod["next_authorised_item"] = "PRD-4"
    prod.setdefault("current_truth", {})
    prod["current_truth"].update({
        "prd3_closed": True,
        "prd3_final_reconciliation_recorded": True,
        "prd3_learner_parent_vertical_journey_hardened": True,
        "prd3_final_evidence_recorded": True,
        "prd3_handoff_authorised": True,
        "prd3_next_authorised_item": "PRD-4",
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
        "prd4_implementation_authorised": False,
    })
    _write(PROD_REGISTER, prod)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "prd305_309_audit_before_capture.json", before)
    _write(EVIDENCE_DIR / "vertical_journey_hardening_acceptance_report.json", hardening_report)
    _write(EVIDENCE_DIR / "vertical_journey_blocked_consent_report.json", blocked_report)

    after = audit(ROOT)
    _write(EVIDENCE_DIR / "prd305_309_audit_after_capture.json", after)
    _write(SUMMARY, {
        "prd_id": "PRD-3.5-3.9",
        "recorded_at": now,
        "recorded_by": args.prd_owner,
        "target_branch": args.target_branch,
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "next_authorised_item": after["register_next_authorised_item"],
        "hardening_report": hardening_report,
        "blocked_consent_report": blocked_report,
    })

    if args.require_valid and not after["valid"]:
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
