"""Audit PRD-4.5-4.9 content quality final evidence and handoff."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-4.5-4.9"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_405_409_content_quality_final_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd4_content_quality_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/content_quality/acceptance.py",
    "app/modules/content_quality/readiness.py",
    "app/modules/content_quality/__init__.py",
    "app/api_v2_routers/content_quality.py",
    "tests/unit/modules/content_quality/test_content_quality_acceptance.py",
    "tests/unit/roadmap_reconciliation/test_prd405_409_content_quality_final_handoff.py",
    "docs/engineering/prd4_content_quality_final_handoff.md",
]
FALSE_BOUNDARIES = [
    "prd5_implementation_authorised",
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


def _previous_prd4_foundation_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd400_404_content_caps_quality_readiness_foundation import audit as audit_prd400

        result = audit_prd400(root)
    except Exception:
        return False
    return bool(result.get("valid") or result.get("authority_valid"))


def _acceptance_helper_valid(root: Path) -> bool:
    try:
        from app.modules.content_quality.acceptance import (
            ACCEPTANCE_CRITERIA,
            build_content_quality_final_acceptance_report,
            build_default_grade4_maths_content_quality_acceptance_report,
        )
        from app.modules.content_quality.readiness import ContentQualityReadinessInputs

        accepted = build_default_grade4_maths_content_quality_acceptance_report().to_payload()
        blocked = build_content_quality_final_acceptance_report(ContentQualityReadinessInputs()).to_payload()
    except Exception:
        return False

    route = (root / "app/api_v2_routers/content_quality.py").read_text() if (root / "app/api_v2_routers/content_quality.py").exists() else ""
    init_text = (root / "app/modules/content_quality/__init__.py").read_text() if (root / "app/modules/content_quality/__init__.py").exists() else ""
    return all([
        accepted.get("prd_id") == PRD_ID,
        accepted.get("source_readiness_prd_id") == "PRD-4.0-4.4",
        accepted.get("accepted") is True,
        accepted.get("prd4_sequence_complete") is True,
        accepted.get("prd5_handoff_ready") is True,
        accepted.get("prd5_implementation_authorised") is False,
        accepted.get("live_learner_traffic_authorised") is False,
        "handoff_to_prd5_privacy_live_data_operations" in accepted.get("recommended_next_actions", []),
        blocked.get("accepted") is False,
        "educator_reviewed_item_bank_missing" in blocked.get("blockers", []),
        len(ACCEPTANCE_CRITERIA) >= 5,
        "get_grade4_maths_content_quality_final_acceptance" in route,
        "build_default_grade4_maths_content_quality_acceptance_report" in route,
        "ContentQualityFinalAcceptanceReport" in init_text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    authority_valid = all([
        not missing_paths,
        _previous_prd4_foundation_valid(root),
        _acceptance_helper_valid(root),
        record.get("content_quality_final_acceptance_helper_added") is True,
        record.get("content_quality_final_acceptance_route_added") is True,
        record.get("educational_readiness_closure_defined") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in {"PRD-4.5-4.9", "PRD-5"},
        prod_register.get("next_authorised_item") in {"PRD-4.5-4.9", "PRD-5"},
    ])
    final_evidence_recorded = record.get("content_quality_final_evidence_recorded") is True
    reconciliation_recorded = record.get("prd4_final_reconciliation_recorded") is True
    sequence_complete = record.get("prd4_sequence_complete") is True
    handoff = record.get("prd5_handoff_authorised") is True
    valid = all([
        authority_valid,
        final_evidence_recorded,
        reconciliation_recorded,
        sequence_complete,
        handoff,
        record.get("next_authorised_item") == "PRD-5",
        register.get("next_authorised_item") == "PRD-5",
        prod_register.get("next_authorised_item") == "PRD-5",
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-4.5", "PRD-4.6", "PRD-4.7", "PRD-4.8", "PRD-4.9"]),
        "missing_paths": missing_paths,
        "previous_prd4_foundation_valid": _previous_prd4_foundation_valid(root),
        "content_quality_final_acceptance_valid": _acceptance_helper_valid(root),
        "content_quality_final_evidence_recorded": final_evidence_recorded,
        "prd4_final_reconciliation_recorded": reconciliation_recorded,
        "prd4_sequence_complete": sequence_complete,
        "prd5_handoff_authorised": handoff,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "prd5_implementation_authorised": record.get("prd5_implementation_authorised") is True,
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
