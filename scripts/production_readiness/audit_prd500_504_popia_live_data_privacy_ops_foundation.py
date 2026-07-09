"""Audit PRD-5.0-5.4 POPIA live-data privacy operations foundation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-5.0-5.4"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_500_504_popia_live_data_privacy_ops_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd5_privacy_live_data_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/privacy_ops/readiness.py",
    "app/modules/privacy_ops/__init__.py",
    "app/api_v2_routers/privacy_operations.py",
    "tests/unit/modules/privacy_ops/test_privacy_live_data_readiness.py",
    "tests/unit/roadmap_reconciliation/test_prd500_504_popia_live_data_privacy_ops_foundation.py",
    "docs/engineering/prd5_popia_live_data_privacy_ops_foundation.md",
]
FALSE_BOUNDARIES = [
    "prd6_implementation_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "live_learner_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]
ALLOWED_NEXT = {"PRD-5", "PRD-5.0-5.4", "PRD-5.5-5.9"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd4_handoff_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd405_409_content_quality_final_handoff import audit as audit_prd405

        result = audit_prd405(root)
    except Exception:
        return False
    return bool(result.get("valid") or result.get("authority_valid"))


def _privacy_readiness_helper_valid(root: Path) -> bool:
    try:
        from app.modules.privacy_ops.readiness import (
            DATA_FLOW_AREAS,
            PRD5_SCOPE_ITEMS,
            REDUCTION_RULES,
            PrivacyLiveDataReadinessInputs,
            build_default_privacy_live_data_readiness_report,
            build_privacy_live_data_readiness_report,
        )

        accepted = build_default_privacy_live_data_readiness_report().to_payload()
        blocked = build_privacy_live_data_readiness_report(PrivacyLiveDataReadinessInputs()).to_payload()
    except Exception:
        return False

    route = (root / "app/api_v2_routers/privacy_operations.py").read_text() if (root / "app/api_v2_routers/privacy_operations.py").exists() else ""
    app_text = (root / "app/api_v2.py").read_text() if (root / "app/api_v2.py").exists() else ""
    compat_app_text = (root / "app/api_v2_routers/api_v2.py").read_text() if (root / "app/api_v2_routers/api_v2.py").exists() else ""
    init_text = (root / "app/modules/privacy_ops/__init__.py").read_text() if (root / "app/modules/privacy_ops/__init__.py").exists() else ""
    return all([
        accepted.get("prd_id") == PRD_ID,
        accepted.get("ready") is True,
        accepted.get("data_flow_matrix_ready") is True,
        accepted.get("consent_withdrawal_drill_proven") is True,
        accepted.get("export_drill_proven") is True,
        accepted.get("deletion_drill_proven") is True,
        accepted.get("retention_drill_proven") is True,
        accepted.get("ai_prompt_pii_redaction_proven") is True,
        accepted.get("telemetry_pii_redaction_proven") is True,
        accepted.get("subprocessor_data_flow_confirmed") is True,
        accepted.get("privacy_signoff_path_visible") is True,
        accepted.get("prd6_implementation_authorised") is False,
        accepted.get("live_learner_traffic_authorised") is False,
        "prepare_prd5_final_privacy_assurance_handoff" in accepted.get("recommended_next_actions", []),
        blocked.get("ready") is False,
        "live_data_processing_impact_assessment_missing" in blocked.get("blockers", []),
        len(DATA_FLOW_AREAS) >= 8,
        len(PRD5_SCOPE_ITEMS) >= 5,
        len(REDUCTION_RULES) >= 5,
        "get_popia_live_data_operations_readiness" in route,
        "build_default_privacy_live_data_readiness_report" in route,
        "privacy_operations" in app_text,
        "privacy_operations" in compat_app_text,
        "PrivacyLiveDataReadinessReport" in init_text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    previous_valid = _previous_prd4_handoff_valid(root)
    helper_valid = _privacy_readiness_helper_valid(root)
    authority_valid = all([
        not missing_paths,
        previous_valid,
        helper_valid,
        record.get("live_data_processing_impact_assessment_visible") is True,
        record.get("consent_withdrawal_drill_visible") is True,
        record.get("export_deletion_retention_drills_visible") is True,
        record.get("ai_prompt_telemetry_pii_redaction_visible") is True,
        record.get("subprocessor_data_flow_privacy_signoff_visible") is True,
        record.get("privacy_operations_route_added") is True,
        record.get("privacy_operations_helper_added") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_register.get("next_authorised_item") in ALLOWED_NEXT,
    ])
    foundation_recorded = record.get("live_data_privacy_foundation_recorded") is True
    evidence_recorded = record.get("privacy_live_data_evidence_recorded") is True
    valid = all([
        authority_valid,
        foundation_recorded,
        evidence_recorded,
        record.get("next_authorised_item") == "PRD-5.5-5.9",
        register.get("next_authorised_item") == "PRD-5.5-5.9",
        prod_register.get("next_authorised_item") == "PRD-5.5-5.9",
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-5.0", "PRD-5.1", "PRD-5.2", "PRD-5.3", "PRD-5.4"]),
        "missing_paths": missing_paths,
        "previous_prd4_handoff_valid": previous_valid,
        "privacy_live_data_readiness_valid": helper_valid,
        "live_data_privacy_foundation_recorded": foundation_recorded,
        "privacy_live_data_evidence_recorded": evidence_recorded,
        "live_data_processing_impact_assessment_visible": record.get("live_data_processing_impact_assessment_visible") is True,
        "consent_withdrawal_drill_visible": record.get("consent_withdrawal_drill_visible") is True,
        "export_deletion_retention_drills_visible": record.get("export_deletion_retention_drills_visible") is True,
        "ai_prompt_telemetry_pii_redaction_visible": record.get("ai_prompt_telemetry_pii_redaction_visible") is True,
        "subprocessor_data_flow_privacy_signoff_visible": record.get("subprocessor_data_flow_privacy_signoff_visible") is True,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "prd6_implementation_authorised": record.get("prd6_implementation_authorised") is True,
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
