"""Audit PRD-4.0-4.4 content/CAPS/educational quality readiness foundation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-4.0-4.4"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_400_404_content_caps_quality_readiness_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd4_content_quality_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/content_quality/__init__.py",
    "app/modules/content_quality/readiness.py",
    "app/api_v2_routers/content_quality.py",
    "tests/unit/modules/content_quality/test_content_quality_readiness.py",
    "tests/unit/roadmap_reconciliation/test_prd400_404_content_caps_quality_readiness_foundation.py",
    "docs/engineering/prd4_content_caps_quality_readiness_foundation.md",
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


def _previous_prd3_valid(root: Path) -> bool:
    record = _load_json(
        root / "docs/roadmap/production_readiness/prd_305_309_learner_parent_vertical_journey_hardening_handoff_record.json"
    )
    register = _load_json(root / "docs/roadmap/production_readiness/prd3_vertical_journey_register.json")
    return all([
        record.get("vertical_journey_final_hardening_recorded") is True,
        record.get("vertical_journey_final_evidence_recorded") is True,
        record.get("prd3_sequence_complete") is True,
        record.get("prd4_handoff_authorised") is True,
        register.get("next_authorised_item") in {"PRD-4", "PRD-4.0-4.4", "PRD-4.5-4.9"},
    ])


def _readiness_helper_valid(root: Path) -> bool:
    try:
        from app.modules.content_quality.readiness import CAPS_STRANDS, build_default_grade4_maths_readiness_report, ContentQualityReadinessInputs, build_content_quality_readiness_report

        accepted = build_default_grade4_maths_readiness_report().to_payload()
        blocked = build_content_quality_readiness_report(ContentQualityReadinessInputs()).to_payload()
    except Exception:
        return False

    route_text = (root / "app/api_v2_routers/content_quality.py").read_text() if (root / "app/api_v2_routers/content_quality.py").exists() else ""
    api_text = (root / "app/api_v2.py").read_text() if (root / "app/api_v2.py").exists() else ""
    api_v2_router_text = (root / "app/api_v2_routers/api_v2.py").read_text() if (root / "app/api_v2_routers/api_v2.py").exists() else ""
    return all([
        accepted.get("prd_id") == PRD_ID,
        accepted.get("ready") is True,
        accepted.get("grade") == 4,
        accepted.get("subject") == "Mathematics",
        len(accepted.get("strand_readiness", [])) == len(CAPS_STRANDS),
        accepted.get("caps_coverage_complete") is True,
        accepted.get("bias_language_accessibility_ready") is True,
        accepted.get("misconception_remediation_ready") is True,
        accepted.get("live_learner_traffic_authorised") is False,
        accepted.get("production_release_authorised") is False,
        blocked.get("ready") is False,
        "caps_coverage_matrix_incomplete" in blocked.get("blockers", []),
        "get_grade4_maths_content_quality_readiness" in route_text,
        "content_quality" in api_text,
        "content_quality" in api_v2_router_text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    authority_valid = all([
        not missing_paths,
        _previous_prd3_valid(root),
        _readiness_helper_valid(root),
        record.get("content_quality_route_added") is True,
        record.get("content_quality_readiness_helper_added") is True,
        record.get("educator_reviewed_item_bank_visible") is True,
        record.get("caps_coverage_matrix_visible") is True,
        record.get("human_review_queue_visible") is True,
        record.get("bias_language_accessibility_review_visible") is True,
        record.get("misconception_remediation_validation_visible") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in {"PRD-4.0-4.4", "PRD-4.5-4.9"},
        prod_register.get("next_authorised_item") in {"PRD-4", "PRD-4.0-4.4", "PRD-4.5-4.9"},
    ])
    foundation_recorded = record.get("content_quality_foundation_recorded") is True
    evidence_recorded = record.get("content_quality_evidence_recorded") is True
    valid = all([
        authority_valid,
        foundation_recorded,
        evidence_recorded,
        record.get("next_authorised_item") == "PRD-4.5-4.9",
        register.get("next_authorised_item") == "PRD-4.5-4.9",
        prod_register.get("next_authorised_item") == "PRD-4.5-4.9",
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-4.0", "PRD-4.1", "PRD-4.2", "PRD-4.3", "PRD-4.4"]),
        "missing_paths": missing_paths,
        "previous_prd3_valid": _previous_prd3_valid(root),
        "content_quality_readiness_helper_valid": _readiness_helper_valid(root),
        "content_quality_foundation_recorded": foundation_recorded,
        "content_quality_evidence_recorded": evidence_recorded,
        "content_quality_route_added": record.get("content_quality_route_added") is True,
        "educator_reviewed_item_bank_visible": record.get("educator_reviewed_item_bank_visible") is True,
        "caps_coverage_matrix_visible": record.get("caps_coverage_matrix_visible") is True,
        "human_review_queue_visible": record.get("human_review_queue_visible") is True,
        "bias_language_accessibility_review_visible": record.get("bias_language_accessibility_review_visible") is True,
        "misconception_remediation_validation_visible": record.get("misconception_remediation_validation_visible") is True,
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
