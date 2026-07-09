"""Audit PRD-6.5-6.9 security final assurance and handoff."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-6.5-6.9"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_605_609_security_final_assurance_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd6_security_assurance_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/security_assurance/assurance.py",
    "app/modules/security_assurance/__init__.py",
    "app/api_v2_routers/security_assurance.py",
    "tests/unit/modules/security_assurance/test_security_final_assurance.py",
    "tests/unit/roadmap_reconciliation/test_prd605_609_security_final_assurance_handoff.py",
    "docs/engineering/prd6_security_final_assurance_handoff.md",
]
FALSE_BOUNDARIES = [
    "prd7_implementation_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "live_learner_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]
ALLOWED_NEXT = {"PRD-6.5-6.9", "PRD-7", "PRD-7.0-7.4", "PRD-7.5-7.9", "PRD-8"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd6_foundation_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd600_604_security_assurance_foundation import audit as audit_prd600

        result = audit_prd600(root)
        if result.get("valid") is True:
            return True
    except Exception:
        pass

    record = root / "docs/roadmap/production_readiness/prd_600_604_security_assurance_foundation_record.json"
    if not record.exists():
        return False
    payload = json.loads(record.read_text())
    return all([
        payload.get("security_assurance_foundation_recorded") is True,
        payload.get("security_assurance_evidence_recorded") is True,
        payload.get("next_authorised_item") == "PRD-6.5-6.9",
    ])


def _security_final_assurance_valid(root: Path) -> bool:
    try:
        from app.modules.security_assurance import (
            FINAL_ASSURANCE_CRITERIA,
            SecurityFinalAssuranceReport,
            build_blocked_security_final_assurance_report,
            build_default_security_final_assurance_report,
            default_security_final_evidence_items,
        )

        accepted = build_default_security_final_assurance_report().to_payload()
        blocked = build_blocked_security_final_assurance_report().to_payload()
        evidence_items = default_security_final_evidence_items()
    except Exception:
        return False

    route = (root / "app/api_v2_routers/security_assurance.py").read_text() if (root / "app/api_v2_routers/security_assurance.py").exists() else ""
    init_text = (root / "app/modules/security_assurance/__init__.py").read_text() if (root / "app/modules/security_assurance/__init__.py").exists() else ""

    return all([
        accepted.get("prd_id") == PRD_ID,
        accepted.get("source_readiness_prd_id") == "PRD-6.0-6.4",
        accepted.get("accepted") is True,
        accepted.get("dast_api_fuzzing_evidence_accepted") is True,
        accepted.get("dependency_container_sbom_evidence_accepted") is True,
        accepted.get("secret_rotation_rate_limit_abuse_evidence_accepted") is True,
        accepted.get("critical_endpoint_authz_negative_tests_accepted") is True,
        accepted.get("external_review_evidence_accepted") is True,
        accepted.get("external_or_independent_review_recorded") is True,
        accepted.get("security_signoff_recorded") is True,
        accepted.get("prd6_final_reconciliation_recorded") is True,
        accepted.get("prd7_implementation_authorised") is False,
        accepted.get("live_learner_traffic_authorised") is False,
        blocked.get("accepted") is False,
        "final_security_evidence_matrix_incomplete" in blocked.get("blockers", []),
        len(FINAL_ASSURANCE_CRITERIA) >= 6,
        len(evidence_items) >= 10,
        all(item.accepted for item in evidence_items),
        "get_security_final_assurance" in route,
        "build_default_security_final_assurance_report" in route,
        "SecurityFinalAssuranceReport" in init_text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    previous_valid = _previous_prd6_foundation_valid(root)
    final_helper_valid = _security_final_assurance_valid(root)

    prod_next = prod_register.get("next_authorised_item")
    authority_valid = all([
        not missing_paths,
        previous_valid,
        final_helper_valid,
        record.get("security_final_assurance_helper_added") is True,
        record.get("security_final_assurance_route_added") is True,
        record.get("dast_api_fuzzing_evidence_defined") is True,
        record.get("dependency_container_sbom_evidence_defined") is True,
        record.get("secret_rotation_rate_limit_abuse_evidence_defined") is True,
        record.get("external_or_independent_review_path_defined") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
    ])

    final_evidence_recorded = record.get("security_final_assurance_evidence_recorded") is True
    external_review_recorded = record.get("external_or_independent_review_recorded") is True
    signoff_recorded = record.get("security_signoff_recorded") is True
    reconciliation_recorded = record.get("prd6_final_reconciliation_recorded") is True
    sequence_complete = record.get("prd6_sequence_complete") is True
    handoff = record.get("prd7_handoff_authorised") is True

    valid = all([
        authority_valid,
        final_evidence_recorded,
        external_review_recorded,
        signoff_recorded,
        reconciliation_recorded,
        sequence_complete,
        handoff,
        record.get("next_authorised_item") == "PRD-7",
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_register.get("next_authorised_item") in ALLOWED_NEXT,
    ])

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-6.5", "PRD-6.6", "PRD-6.7", "PRD-6.8", "PRD-6.9"]),
        "missing_paths": missing_paths,
        "previous_prd6_foundation_valid": previous_valid,
        "security_final_assurance_valid": final_helper_valid,
        "security_final_assurance_evidence_recorded": final_evidence_recorded,
        "external_or_independent_review_recorded": external_review_recorded,
        "security_signoff_recorded": signoff_recorded,
        "prd6_final_reconciliation_recorded": reconciliation_recorded,
        "prd6_sequence_complete": sequence_complete,
        "prd7_handoff_authorised": handoff,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "prd7_implementation_authorised": record.get("prd7_implementation_authorised") is True,
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
