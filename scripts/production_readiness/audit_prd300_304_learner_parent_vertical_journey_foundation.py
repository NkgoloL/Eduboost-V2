"""Audit PRD-3.0-3.4 learner/parent vertical journey foundation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-3.0-3.4"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_300_304_learner_parent_vertical_journey_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd3_vertical_journey_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/vertical_journey/service.py",
    "app/modules/vertical_journey/__init__.py",
    "app/api_v2_routers/vertical_journey.py",
    "tests/unit/modules/vertical_journey/test_vertical_journey_service.py",
    "tests/unit/roadmap_reconciliation/test_prd300_304_learner_parent_vertical_journey_foundation.py",
    "docs/engineering/prd3_learner_parent_vertical_journey_foundation.md",
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


def _previous_prd2_valid() -> bool:
    try:
        from scripts.production_readiness.audit_prd207_209_runtime_kg_acceptance_handoff import audit as audit_prd207

        result = audit_prd207(ROOT)
    except Exception:
        return False
    return bool(result.get("valid") or result.get("authority_valid"))


def _vertical_journey_service_valid(root: Path) -> bool:
    try:
        from app.modules.vertical_journey.service import VerticalJourneyInputs, build_vertical_journey_snapshot

        payload = build_vertical_journey_snapshot(
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
        ).to_payload()
    except Exception:
        return False
    service_text = (root / "app/modules/vertical_journey/service.py").read_text() if (root / "app/modules/vertical_journey/service.py").exists() else ""
    return all([
        payload.get("complete") is True,
        payload.get("completion_ratio") == 1.0,
        payload.get("prd4_implementation_authorised") is False,
        "guardian_consent_inactive" in service_text,
        "runtime_kg_gap_profile_available" in service_text,
    ])


def _route_registered(root: Path) -> bool:
    main = (root / "app/api_v2.py").read_text() if (root / "app/api_v2.py").exists() else ""
    legacy = (root / "app/api_v2_routers/api_v2.py").read_text() if (root / "app/api_v2_routers/api_v2.py").exists() else ""
    route = (root / "app/api_v2_routers/vertical_journey.py").read_text() if (root / "app/api_v2_routers/vertical_journey.py").exists() else ""
    return all([
        "vertical_journey" in main,
        "vertical_journey.router" in main,
        "vertical_journey" in legacy,
        "vertical_journey.router" in legacy,
        "build_vertical_journey_snapshot" in route,
        "ConsentService" in route,
        "build_runtime_kg_study_plan_payload" in route,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    authority_valid = all([
        not missing_paths,
        _previous_prd2_valid(),
        _vertical_journey_service_valid(root),
        _route_registered(root),
        record.get("vertical_journey_service_added") is True,
        record.get("vertical_journey_route_added") is True,
        record.get("vertical_journey_route_registered") is True,
        record.get("guardian_consent_status_included") is True,
        record.get("runtime_kg_gap_profile_included") is True,
        record.get("popia_export_path_available") is True,
        record.get("popia_erasure_path_available") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in {"PRD-3.0-3.4", "PRD-3.5-3.9"},
        prod_register.get("next_authorised_item") in {"PRD-3", "PRD-3.0-3.4", "PRD-3.5-3.9"},
    ])
    recorded = record.get("learner_parent_vertical_journey_foundation_recorded") is True
    valid = all([
        authority_valid,
        recorded,
        record.get("vertical_journey_evidence_recorded") is True,
        record.get("next_authorised_item") == "PRD-3.5-3.9",
        register.get("next_authorised_item") == "PRD-3.5-3.9",
        prod_register.get("next_authorised_item") == "PRD-3.5-3.9",
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-3.0", "PRD-3.1", "PRD-3.2", "PRD-3.3", "PRD-3.4"]),
        "missing_paths": missing_paths,
        "previous_prd2_valid": _previous_prd2_valid(),
        "vertical_journey_service_added": _vertical_journey_service_valid(root),
        "vertical_journey_route_registered": _route_registered(root),
        "learner_parent_vertical_journey_foundation_recorded": recorded,
        "vertical_journey_evidence_recorded": record.get("vertical_journey_evidence_recorded") is True,
        "runtime_kg_gap_profile_included": record.get("runtime_kg_gap_profile_included") is True,
        "parent_progress_report_available": record.get("parent_progress_report_available") is True,
        "popia_export_path_available": record.get("popia_export_path_available") is True,
        "popia_erasure_path_available": record.get("popia_erasure_path_available") is True,
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
