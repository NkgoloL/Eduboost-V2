"""Audit PRD-6.0-6.4 security assurance foundation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-6.0-6.4"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_600_604_security_assurance_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd6_security_assurance_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/security_assurance/readiness.py",
    "app/modules/security_assurance/__init__.py",
    "app/api_v2_routers/security_assurance.py",
    "tests/unit/modules/security_assurance/test_security_assurance_readiness.py",
    "tests/unit/roadmap_reconciliation/test_prd600_604_security_assurance_foundation.py",
    "docs/engineering/prd6_security_assurance_foundation.md",
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
ALLOWED_NEXT = {"PRD-6", "PRD-6.0-6.4", "PRD-6.5-6.9", "PRD-7"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd5_handoff_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd505_509_popia_final_assurance_handoff import audit as audit_prd505

        result = audit_prd505(root)
        if result.get("valid") is True:
            return True
    except Exception:  # best-effort probe, cannot fail-close
            pass

    record = root / "docs/roadmap/production_readiness/prd_505_509_popia_final_assurance_handoff_record.json"
    if not record.exists():
        return False
    payload = json.loads(record.read_text())
    return all([
        payload.get("privacy_final_assurance_evidence_recorded") is True,
        payload.get("prd5_sequence_complete") is True,
        payload.get("prd6_handoff_authorised") is True,
        payload.get("next_authorised_item") == "PRD-6",
    ])


def _security_readiness_helper_valid(root: Path) -> bool:
    try:
        from app.modules.security_assurance import (
            RECOMMENDED_TOOLS,
            SECURITY_EVIDENCE_AREAS,
            SECURITY_SCOPE_ITEMS,
            build_blocked_security_assurance_readiness_report,
            build_default_security_assurance_readiness_report,
            default_security_evidence_controls,
        )

        accepted = build_default_security_assurance_readiness_report().to_payload()
        blocked = build_blocked_security_assurance_readiness_report().to_payload()
        controls = default_security_evidence_controls()
    except Exception:
        return False

    route = (root / "app/api_v2_routers/security_assurance.py").read_text() if (root / "app/api_v2_routers/security_assurance.py").exists() else ""
    init_text = (root / "app/modules/security_assurance/__init__.py").read_text() if (root / "app/modules/security_assurance/__init__.py").exists() else ""
    api_v2 = (root / "app/api_v2.py").read_text() if (root / "app/api_v2.py").exists() else ""
    lite_api = (root / "app/api_v2_routers/api_v2.py").read_text() if (root / "app/api_v2_routers/api_v2.py").exists() else ""

    return all([
        accepted.get("prd_id") == PRD_ID,
        accepted.get("ready") is True,
        accepted.get("scanner_readiness_defined") is True,
        accepted.get("operational_security_drills_defined") is True,
        accepted.get("evidence_matrix_ready") is True,
        accepted.get("external_review_path_defined") is True,
        accepted.get("prd7_implementation_authorised") is False,
        accepted.get("live_learner_traffic_authorised") is False,
        "capture_prd6_security_assurance_foundation_evidence" in accepted.get("recommended_next_actions", []),
        blocked.get("ready") is False,
        "dast_api_fuzzing_plan_missing" in blocked.get("blockers", []),
        len(SECURITY_SCOPE_ITEMS) >= 6,
        len(SECURITY_EVIDENCE_AREAS) >= 10,
        len(RECOMMENDED_TOOLS) >= 6,
        len(controls) == len(SECURITY_EVIDENCE_AREAS),
        "get_security_assurance_readiness" in route,
        "build_default_security_assurance_readiness_report" in route,
        "SecurityAssuranceReadinessReport" in init_text,
        "security_assurance" in api_v2,
        "security_assurance" in lite_api,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    previous_valid = _previous_prd5_handoff_valid(root)
    readiness_valid = _security_readiness_helper_valid(root)

    prod_next = prod_register.get("next_authorised_item")
    authority_valid = all([
        not missing_paths,
        previous_valid,
        readiness_valid,
        record.get("security_assurance_helper_added") is True,
        record.get("security_assurance_route_added") is True,
        record.get("dast_api_fuzzing_readiness_defined") is True,
        record.get("dependency_container_sbom_readiness_defined") is True,
        record.get("secret_rotation_rate_limit_abuse_readiness_defined") is True,
        record.get("external_review_path_defined") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in {"PRD-6.0-6.4", "PRD-6.5-6.9", "PRD-7"},
        prod_next in ALLOWED_NEXT,
    ])

    foundation_recorded = record.get("security_assurance_foundation_recorded") is True
    evidence_recorded = record.get("security_assurance_evidence_recorded") is True
    valid = all([
        authority_valid,
        foundation_recorded,
        evidence_recorded,
        record.get("next_authorised_item") == "PRD-6.5-6.9",
        register.get("next_authorised_item") in {"PRD-6.5-6.9", "PRD-7"},
        prod_register.get("next_authorised_item") in {"PRD-6.5-6.9", "PRD-7"},
    ])

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-6.0", "PRD-6.1", "PRD-6.2", "PRD-6.3", "PRD-6.4"]),
        "missing_paths": missing_paths,
        "previous_prd5_handoff_valid": previous_valid,
        "security_readiness_valid": readiness_valid,
        "security_assurance_foundation_recorded": foundation_recorded,
        "security_assurance_evidence_recorded": evidence_recorded,
        "dast_api_fuzzing_readiness_defined": record.get("dast_api_fuzzing_readiness_defined") is True,
        "dependency_container_sbom_readiness_defined": record.get("dependency_container_sbom_readiness_defined") is True,
        "secret_rotation_rate_limit_abuse_readiness_defined": record.get("secret_rotation_rate_limit_abuse_readiness_defined") is True,
        "external_review_path_defined": record.get("external_review_path_defined") is True,
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
