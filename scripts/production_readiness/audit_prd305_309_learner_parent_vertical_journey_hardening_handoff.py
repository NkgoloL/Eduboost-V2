"""Audit PRD-3.5-3.9 learner/parent vertical journey hardening and handoff."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-3.5-3.9"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_305_309_learner_parent_vertical_journey_hardening_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd3_vertical_journey_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/vertical_journey/hardening.py",
    "app/modules/vertical_journey/service.py",
    "app/modules/vertical_journey/__init__.py",
    "app/api_v2_routers/vertical_journey.py",
    "tests/unit/modules/vertical_journey/test_vertical_journey_hardening.py",
    "tests/unit/roadmap_reconciliation/test_prd305_309_learner_parent_vertical_journey_hardening_handoff.py",
    "docs/engineering/prd3_learner_parent_vertical_journey_hardening_handoff.md",
]
FALSE_BOUNDARIES = [
    "prd4_implementation_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "live_learner_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd3_foundation_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd300_304_learner_parent_vertical_journey_foundation import audit as audit_prd300

        result = audit_prd300(root)
    except Exception:
        return False
    return bool(result.get("valid") or result.get("authority_valid"))


def _hardening_helper_valid(root: Path) -> bool:
    try:
        from app.modules.vertical_journey.hardening import build_vertical_journey_hardening_report
        from app.modules.vertical_journey.service import VerticalJourneyInputs, build_vertical_journey_snapshot

        snapshot = build_vertical_journey_snapshot(
            VerticalJourneyInputs(
                learner_id="audit-learner",
                guardian_id="audit-guardian",
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
        )
        complete_payload = build_vertical_journey_hardening_report(snapshot).to_payload()
        blocked_snapshot = build_vertical_journey_snapshot(
            VerticalJourneyInputs(
                learner_id="blocked-learner",
                guardian_id="audit-guardian",
                learner_profile_created=True,
                guardian_consent_active=False,
            )
        )
        blocked_payload = build_vertical_journey_hardening_report(blocked_snapshot).to_payload()
    except Exception:
        return False
    text = (root / "app/modules/vertical_journey/hardening.py").read_text() if (root / "app/modules/vertical_journey/hardening.py").exists() else ""
    route = (root / "app/api_v2_routers/vertical_journey.py").read_text() if (root / "app/api_v2_routers/vertical_journey.py").exists() else ""
    return all([
        complete_payload.get("prd_id") == PRD_ID,
        complete_payload.get("accepted") is True,
        complete_payload.get("prd4_implementation_authorised") is False,
        complete_payload.get("live_learner_traffic_authorised") is False,
        blocked_payload.get("accepted") is False,
        "guardian_consent_inactive" in blocked_payload.get("blockers", []),
        "build_vertical_journey_hardening_report" in route,
        "payload[\"hardening\"]" in route,
        "recommended_next_actions" in text,
        "runtime_kg_gap_profile_visible" in text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    authority_valid = all([
        not missing_paths,
        _previous_prd3_foundation_valid(root),
        _hardening_helper_valid(root),
        record.get("vertical_journey_hardening_helper_added") is True,
        record.get("vertical_journey_route_hardening_payload_added") is True,
        record.get("learner_parent_journey_acceptance_defined") is True,
        record.get("consent_blocker_preserved") is True,
        record.get("parent_report_visibility_confirmed") is True,
        record.get("popia_export_erasure_visibility_confirmed") is True,
        record.get("runtime_kg_gap_profile_visibility_confirmed") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in {"PRD-3.5-3.9", "PRD-4"},
        prod_register.get("next_authorised_item") in {"PRD-3.5-3.9", "PRD-4"},
    ])
    hardening_recorded = record.get("vertical_journey_final_hardening_recorded") is True
    final_evidence_recorded = record.get("vertical_journey_final_evidence_recorded") is True
    reconciliation_recorded = record.get("prd3_final_reconciliation_recorded") is True
    sequence_complete = record.get("prd3_sequence_complete") is True
    handoff = record.get("prd4_handoff_authorised") is True
    valid = all([
        authority_valid,
        hardening_recorded,
        final_evidence_recorded,
        reconciliation_recorded,
        sequence_complete,
        handoff,
        record.get("next_authorised_item") == "PRD-4",
        register.get("next_authorised_item") == "PRD-4",
        prod_register.get("next_authorised_item") == "PRD-4",
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-3.5", "PRD-3.6", "PRD-3.7", "PRD-3.8", "PRD-3.9"]),
        "missing_paths": missing_paths,
        "previous_prd3_foundation_valid": _previous_prd3_foundation_valid(root),
        "vertical_journey_hardening_helper_valid": _hardening_helper_valid(root),
        "vertical_journey_final_hardening_recorded": hardening_recorded,
        "vertical_journey_final_evidence_recorded": final_evidence_recorded,
        "prd3_final_reconciliation_recorded": reconciliation_recorded,
        "prd3_sequence_complete": sequence_complete,
        "prd4_handoff_authorised": handoff,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "prd4_implementation_authorised": record.get("prd4_implementation_authorised") is True,
        "production_release_authorised": record.get("production_release_authorised") is True,
        "deployment_authorised": record.get("deployment_authorised") is True,
        "release_tag_authorised": record.get("release_tag_authorised") is True,
        "public_beta_authorised": record.get("public_beta_authorised") is True,
        "live_learner_traffic_authorised": record.get("live_learner_traffic_authorised") is True,
        "billing_launch_authorised": record.get("billing_launch_authorised") is True,
        "live_payment_processing_authorised": record.get("live_payment_processing_authorised") is True,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--authority-only", action="store_true")
    args = parser.parse_args()
    result = audit(ROOT)
    if args.authority_only:
        result = {**result, "valid": False}
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"{PRD_ID}: valid={result['valid']} authority_valid={result['authority_valid']}")
