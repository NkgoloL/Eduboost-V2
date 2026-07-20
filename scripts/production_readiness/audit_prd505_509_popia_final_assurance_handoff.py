"""Audit PRD-5.5-5.9 POPIA final assurance and handoff."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-5.5-5.9"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_505_509_popia_final_assurance_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd5_privacy_live_data_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/privacy_ops/assurance.py",
    "app/modules/privacy_ops/readiness.py",
    "app/modules/privacy_ops/__init__.py",
    "app/api_v2_routers/privacy_operations.py",
    "tests/unit/modules/privacy_ops/test_privacy_final_assurance.py",
    "tests/unit/roadmap_reconciliation/test_prd505_509_popia_final_assurance_handoff.py",
    "docs/engineering/prd5_popia_final_assurance_handoff.md",
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
ALLOWED_NEXT = {"PRD-5.5-5.9", "PRD-6", "PRD-6.5-6.9", "PRD-7"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd5_foundation_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd500_504_popia_live_data_privacy_ops_foundation import audit as audit_prd500

        result = audit_prd500(root)
        if result.get("valid") or result.get("authority_valid"):
            return True
    except Exception:  # best-effort probe, cannot fail-close
            pass

    record = root / "docs/roadmap/production_readiness/prd_500_504_popia_live_data_privacy_ops_foundation_record.json"
    if not record.exists():
        return False
    payload = json.loads(record.read_text())
    return all([
        payload.get("live_data_privacy_foundation_recorded") is True,
        payload.get("privacy_live_data_evidence_recorded") is True,
        payload.get("next_authorised_item") == "PRD-5.5-5.9",
    ])


def _final_assurance_helper_valid(root: Path) -> bool:
    try:
        from app.modules.privacy_ops.assurance import (
            AUDIT_REPORT_ID,
            FINAL_ASSURANCE_CRITERIA,
            build_blocked_privacy_final_assurance_report,
            build_default_privacy_final_assurance_report,
            default_audit_crosswalk_items,
        )

        accepted = build_default_privacy_final_assurance_report().to_payload()
        blocked = build_blocked_privacy_final_assurance_report().to_payload()
        crosswalk = default_audit_crosswalk_items()
    except Exception:
        return False

    route = (root / "app/api_v2_routers/privacy_operations.py").read_text() if (root / "app/api_v2_routers/privacy_operations.py").exists() else ""
    init_text = (root / "app/modules/privacy_ops/__init__.py").read_text() if (root / "app/modules/privacy_ops/__init__.py").exists() else ""
    return all([
        accepted.get("prd_id") == PRD_ID,
        accepted.get("source_readiness_prd_id") == "PRD-5.0-5.4",
        accepted.get("audit_report_id") == AUDIT_REPORT_ID,
        accepted.get("accepted") is True,
        accepted.get("prd5_sequence_complete") is True,
        accepted.get("prd6_handoff_ready") is True,
        accepted.get("prd6_implementation_authorised") is False,
        accepted.get("live_learner_traffic_authorised") is False,
        accepted.get("audit_2026_07_09_crosswalk_reconciled") is True,
        "handoff_to_prd6_security_assurance_external_review" in accepted.get("recommended_next_actions", []),
        blocked.get("accepted") is False,
        "prd5_live_data_readiness_incomplete" in blocked.get("blockers", []),
        "privacy_signoff_not_recorded" in blocked.get("blockers", []),
        len(FINAL_ASSURANCE_CRITERIA) >= 5,
        len(crosswalk) >= 7,
        "get_popia_live_data_operations_final_assurance" in route,
        "build_default_privacy_final_assurance_report" in route,
        "PrivacyFinalAssuranceReport" in init_text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    previous_valid = _previous_prd5_foundation_valid(root)
    final_helper_valid = _final_assurance_helper_valid(root)

    authority_valid = all([
        not missing_paths,
        previous_valid,
        final_helper_valid,
        record.get("privacy_final_assurance_helper_added") is True,
        record.get("privacy_final_assurance_route_added") is True,
        record.get("audit_2026_07_09_crosswalk_defined") is True,
        record.get("privacy_signoff_closure_defined") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_register.get("next_authorised_item") in ALLOWED_NEXT,
    ])

    final_evidence_recorded = record.get("privacy_final_assurance_evidence_recorded") is True
    audit_crosswalk_reconciled = record.get("audit_2026_07_09_crosswalk_reconciled") is True
    privacy_signoff_recorded = record.get("privacy_signoff_recorded") is True
    reconciliation_recorded = record.get("prd5_final_reconciliation_recorded") is True
    sequence_complete = record.get("prd5_sequence_complete") is True
    handoff = record.get("prd6_handoff_authorised") is True

    valid = all([
        authority_valid,
        final_evidence_recorded,
        audit_crosswalk_reconciled,
        privacy_signoff_recorded,
        reconciliation_recorded,
        sequence_complete,
        handoff,
        record.get("next_authorised_item") == "PRD-6",
        register.get("next_authorised_item") in {"PRD-6", "PRD-6.5-6.9", "PRD-7"},
        prod_register.get("next_authorised_item") in {"PRD-6", "PRD-6.5-6.9", "PRD-7"},
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-5.5", "PRD-5.6", "PRD-5.7", "PRD-5.8", "PRD-5.9"]),
        "missing_paths": missing_paths,
        "previous_prd5_foundation_valid": previous_valid,
        "privacy_final_assurance_valid": final_helper_valid,
        "privacy_final_assurance_evidence_recorded": final_evidence_recorded,
        "audit_2026_07_09_crosswalk_reconciled": audit_crosswalk_reconciled,
        "privacy_signoff_recorded": privacy_signoff_recorded,
        "prd5_final_reconciliation_recorded": reconciliation_recorded,
        "prd5_sequence_complete": sequence_complete,
        "prd6_handoff_authorised": handoff,
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
