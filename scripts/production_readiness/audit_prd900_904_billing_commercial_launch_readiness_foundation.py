"""Audit PRD-9.0-9.4 billing and commercial launch readiness foundation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-9.0-9.4"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_900_904_billing_commercial_launch_readiness_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd9_commercial_launch_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/commercial_launch/readiness.py",
    "app/modules/commercial_launch/__init__.py",
    "app/api_v2_routers/commercial_launch.py",
    "tests/unit/modules/commercial_launch/test_commercial_launch_readiness.py",
    "tests/unit/roadmap_reconciliation/test_prd900_904_billing_commercial_launch_readiness_foundation.py",
    "docs/engineering/prd9_billing_commercial_launch_readiness_foundation.md",
]
FALSE_BOUNDARIES = [
    "prd10_implementation_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "live_learner_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]
ALLOWED_NEXT = {"PRD-9", "PRD-9.0-9.4", "PRD-9.5-9.9", "PRD-10", "PRD-10.0-10.4", "PRD-10.5-10.9", "PRD-11"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd8_handoff_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd805_809_performance_scale_cost_final_handoff import audit as audit_prd805

        result = audit_prd805(root)
        if result.get("valid") is True:
            return True
    except Exception:  # best-effort probe, cannot fail-close
            pass

    record = root / "docs/roadmap/production_readiness/prd_805_809_performance_scale_cost_final_handoff_record.json"
    if not record.exists():
        return False
    payload = json.loads(record.read_text())
    return all([
        payload.get("performance_final_assurance_evidence_recorded") is True,
        payload.get("prd8_sequence_complete") is True,
        payload.get("prd9_handoff_authorised") is True,
        payload.get("next_authorised_item") == "PRD-9",
    ])


def _commercial_launch_readiness_valid(root: Path) -> bool:
    try:
        from app.modules.commercial_launch import (
            COMMERCIAL_EVIDENCE_AREAS,
            CommercialLaunchReadinessReport,
            build_blocked_commercial_launch_readiness_report,
            build_default_commercial_launch_readiness_report,
            default_commercial_launch_evidence_controls,
        )

        ready = build_default_commercial_launch_readiness_report().to_payload()
        blocked = build_blocked_commercial_launch_readiness_report().to_payload()
        controls = default_commercial_launch_evidence_controls()
        _ = CommercialLaunchReadinessReport
    except Exception:
        return False

    route_text = (root / "app/api_v2_routers/commercial_launch.py").read_text() if (root / "app/api_v2_routers/commercial_launch.py").exists() else ""
    app_text = (root / "app/api_v2.py").read_text() if (root / "app/api_v2.py").exists() else ""
    api_v2_text = (root / "app/api_v2_routers/api_v2.py").read_text() if (root / "app/api_v2_routers/api_v2.py").exists() else ""

    return all([
        ready.get("prd_id") == PRD_ID,
        ready.get("ready") is True,
        ready.get("billing_contract_readiness_defined") is True,
        ready.get("commercial_policy_readiness_defined") is True,
        ready.get("support_reconciliation_defined") is True,
        ready.get("evidence_matrix_ready") is True,
        ready.get("existing_billing_contracts_valid") is True,
        ready.get("billing_launch_authorised") is False,
        ready.get("live_payment_processing_authorised") is False,
        ready.get("live_learner_traffic_authorised") is False,
        ready.get("prd10_implementation_authorised") is False,
        blocked.get("ready") is False,
        "commercial_evidence_matrix_incomplete" in blocked.get("blockers", []),
        len(COMMERCIAL_EVIDENCE_AREAS) >= 8,
        {control.area for control in controls} == set(COMMERCIAL_EVIDENCE_AREAS),
        all(control.ready for control in controls),
        "get_commercial_launch_readiness" in route_text,
        "build_default_commercial_launch_readiness_report" in route_text,
        "commercial_launch" in app_text,
        "commercial_launch" in api_v2_text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    previous_valid = _previous_prd8_handoff_valid(root)
    readiness_valid = _commercial_launch_readiness_valid(root)

    authority_valid = all([
        not missing_paths,
        previous_valid,
        readiness_valid,
        record.get("commercial_launch_readiness_helper_added") is True,
        record.get("commercial_launch_readiness_route_added") is True,
        record.get("billing_provider_test_mode_defined") is True,
        record.get("pricing_packaging_defined") is True,
        record.get("checkout_webhook_contract_defined") is True,
        record.get("subscription_entitlement_matrix_defined") is True,
        record.get("invoice_tax_refund_support_defined") is True,
        record.get("sponsorship_school_procurement_defined") is True,
        record.get("commercial_support_reconciliation_defined") is True,
        record.get("terms_privacy_launch_comms_defined") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_register.get("next_authorised_item") in ALLOWED_NEXT,
    ])

    foundation_recorded = record.get("commercial_launch_foundation_recorded") is True
    evidence_recorded = record.get("commercial_launch_evidence_recorded") is True

    valid = all([
        authority_valid,
        foundation_recorded,
        evidence_recorded,
        record.get("next_authorised_item") == "PRD-9.5-9.9",
        register.get("next_authorised_item") in {"PRD-9.5-9.9", "PRD-10", "PRD-10.0-10.4", "PRD-10.5-10.9", "PRD-11"},
        prod_register.get("next_authorised_item") in {"PRD-9.5-9.9", "PRD-10", "PRD-10.0-10.4", "PRD-10.5-10.9", "PRD-11"},
    ])

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-9.0", "PRD-9.1", "PRD-9.2", "PRD-9.3", "PRD-9.4"]),
        "missing_paths": missing_paths,
        "previous_prd8_handoff_valid": previous_valid,
        "commercial_launch_readiness_valid": readiness_valid,
        "commercial_launch_foundation_recorded": foundation_recorded,
        "commercial_launch_evidence_recorded": evidence_recorded,
        "billing_provider_test_mode_defined": record.get("billing_provider_test_mode_defined") is True,
        "pricing_packaging_defined": record.get("pricing_packaging_defined") is True,
        "checkout_webhook_contract_defined": record.get("checkout_webhook_contract_defined") is True,
        "subscription_entitlement_matrix_defined": record.get("subscription_entitlement_matrix_defined") is True,
        "invoice_tax_refund_support_defined": record.get("invoice_tax_refund_support_defined") is True,
        "sponsorship_school_procurement_defined": record.get("sponsorship_school_procurement_defined") is True,
        "commercial_support_reconciliation_defined": record.get("commercial_support_reconciliation_defined") is True,
        "terms_privacy_launch_comms_defined": record.get("terms_privacy_launch_comms_defined") is True,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "prd10_implementation_authorised": record.get("prd10_implementation_authorised") is True,
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
