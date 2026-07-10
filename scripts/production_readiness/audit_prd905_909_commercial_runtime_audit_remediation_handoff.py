"""Audit PRD-9.5-9.9 commercial runtime audit remediation and handoff."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-9.5-9.9"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_905_909_commercial_runtime_audit_remediation_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd9_commercial_launch_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
CROSSWALK = ROOT / "docs/roadmap/production_readiness/prd9_audit_2026_07_09_remediation_crosswalk.json"
SECURITY_PLAN = ROOT / "docs/roadmap/production_readiness/prd9_security_dependency_remediation_plan.json"
LICENSING_REGISTER = ROOT / "docs/roadmap/production_readiness/third_party_content_licensing_register.json"
REQUIRED_PATHS = [
    "app/modules/commercial_launch/remediation.py",
    "app/api_v2_routers/commercial_launch.py",
    "app/repositories/auth_repository.py",
    "app/repositories/assessment_repository.py",
    "app/services/assessment_service_v2.py",
    "tests/unit/test_prd9_runtime_repository_remediation.py",
    "tests/unit/modules/commercial_launch/test_commercial_runtime_audit_remediation.py",
    "tests/unit/roadmap_reconciliation/test_prd905_909_commercial_runtime_audit_remediation_handoff.py",
    "docs/engineering/prd9_commercial_runtime_audit_remediation_handoff.md",
    "docs/roadmap/production_readiness/prd9_audit_2026_07_09_remediation_crosswalk.json",
    "docs/roadmap/production_readiness/prd9_security_dependency_remediation_plan.json",
    "docs/roadmap/production_readiness/third_party_content_licensing_register.json",
    "LICENSE",
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
ALLOWED_NEXT = {"PRD-9.5-9.9", "PRD-10", "PRD-10.0-10.4", "PRD-10.5-10.9", "PRD-11", "PRD-11.0-11.4", "PRD-11.5-11.9"}

# `.agents` is a workspace mount in this environment, not tracked repo content.
HYGIENE_REMOVED = [
    "coverage.xml",
    "backups-local-test",
    "backups-matrix-test",
    "logs",
    "docs/generated",
    "temp",
    "data/siyavula_grade7_pw.html",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd9_foundation_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd900_904_billing_commercial_launch_readiness_foundation import audit as audit_prd900

        result = audit_prd900(root)
        return result.get("valid") is True or all([
            result.get("authority_valid") is True,
            result.get("commercial_launch_foundation_recorded") is True,
            result.get("commercial_launch_evidence_recorded") is True,
        ])
    except Exception:
        return False


def _commercial_remediation_helper_valid(root: Path) -> bool:
    try:
        from app.modules.commercial_launch import (
            build_blocked_commercial_runtime_audit_remediation_report,
            build_default_commercial_runtime_audit_remediation_report,
        )

        ready = build_default_commercial_runtime_audit_remediation_report().to_payload()
        blocked = build_blocked_commercial_runtime_audit_remediation_report().to_payload()
    except Exception:
        return False

    route_text = (root / "app/api_v2_routers/commercial_launch.py").read_text() if (root / "app/api_v2_routers/commercial_launch.py").exists() else ""
    return all([
        ready.get("prd_id") == PRD_ID,
        ready.get("accepted") is True,
        ready.get("runtime_blockers_remediated") is True,
        ready.get("audit_2026_07_09_reconciled") is True,
        ready.get("billing_launch_authorised") is False,
        ready.get("live_payment_processing_authorised") is False,
        ready.get("prd10_implementation_authorised") is False,
        blocked.get("accepted") is False,
        "commercial_runtime_audit_remediation_incomplete" in blocked.get("blockers", []),
        "get_commercial_runtime_audit_remediation" in route_text,
    ])


def _runtime_code_contracts_valid(root: Path) -> bool:
    auth_text = (root / "app/repositories/auth_repository.py").read_text()
    assessment_repo_text = (root / "app/repositories/assessment_repository.py").read_text()
    assessment_service_text = (root / "app/services/assessment_service_v2.py").read_text()
    router_text = (root / "app/api_v2_routers/assessments.py").read_text()
    stripe_text = (root / "app/core/stripe_client.py").read_text()
    return all([
        "def __init__(self, db: AsyncSession | None = None)" in auth_text,
        "async def update_subscription" in auth_text,
        "async def get_by_stripe_customer_id" in auth_text,
        "async def get_by_id" in auth_text,
        "GuardianRepository(db)" in stripe_text,
        "async def list_assessments" in assessment_repo_text,
        "async def get_assessment" in assessment_repo_text,
        "async def create_attempt" in assessment_repo_text,
        "def with_db" in assessment_service_text,
        "service = AssessmentServiceV2()" in router_text,
        "service.with_db(db)" in router_text,
    ])


def _dependency_remediation_valid(root: Path) -> bool:
    base_in = (root / "requirements/base.in").read_text()
    dev_in = (root / "requirements/dev.in").read_text()
    dev_txt = (root / "requirements/dev.txt").read_text() if (root / "requirements/dev.txt").exists() else ""
    security_plan = _load_json(root / SECURITY_PLAN.relative_to(ROOT))
    return all([
        "aiohttp==3.13.5" in base_in,
        "beautifulsoup4==4.12.3" in base_in,
        "aiohttp==3.13.5" in dev_in,
        "beautifulsoup4==4.12.3" in dev_in,
        "aiohttp==3.13.5" in dev_txt,
        "beautifulsoup4==4.12.3" in dev_txt,
        "cryptography==49.0.0" in base_in,
        security_plan.get("cryptography_bumped_in_requirements") is True,
        (security_plan.get("python_jose_to_pyjwt_required_before") == "PRD-10 live learner traffic authorisation" or security_plan.get("python_jose_to_pyjwt_completed_in") == "PRD-10.0-10.4"),
        security_plan.get("secrets_baseline_reduction_required_before") == "PRD-10 live learner traffic authorisation",
        security_plan.get("gitleaks_allowlist_tightened") is True,
        "^docs/release-evidence/.*" in (root / ".gitleaks.toml").read_text(),
    ])


def _hygiene_valid(root: Path) -> bool:
    gitignore = (root / ".gitignore").read_text() if (root / ".gitignore").exists() else ""
    licensing = _load_json(root / LICENSING_REGISTER.relative_to(ROOT))
    return all([
        all(not (root / rel).exists() for rel in HYGIENE_REMOVED),
        "coverage.xml" in gitignore,
        "backups-local-test/" in gitignore,
        "docs/generated/" in gitignore,
        licensing.get("status") == "raw_siyavula_html_removed_pending_licensing_review",
    ])


def _crosswalk_valid(root: Path) -> bool:
    crosswalk = _load_json(root / CROSSWALK.relative_to(ROOT))
    items = {item.get("finding"): item.get("disposition") for item in crosswalk.get("items", [])}
    return all([
        crosswalk.get("status", "").startswith("reconciled_by_PRD-9.5-9.9"),
        items.get("dual_repository_layer_subscription_runtime_failure") == "fixed_in_PRD-9.5",
        items.get("assessment_service_repository_contract_mismatch") == "fixed_in_PRD-9.6",
        items.get("aiohttp_beautifulsoup4_dev_dependency_drift") == "requirements_repaired_in_PRD-9.8",
        items.get("raw_siyavula_html_licensing_review") == "raw_file_removed_and_licensing_register_recorded",
        items.get("large_detect_secrets_baseline_noise") == "gitleaks_allowlist_tightened_and_baseline_reduction_registered_as_PRD-10_blocker",
        items.get("missing_proprietary_license_file") == "proprietary_LICENSE_file_added",
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    previous_valid = _previous_prd9_foundation_valid(root)
    helper_valid = _commercial_remediation_helper_valid(root)
    runtime_contracts_valid = _runtime_code_contracts_valid(root)
    dependency_valid = _dependency_remediation_valid(root)
    hygiene_valid = _hygiene_valid(root)
    crosswalk_valid = _crosswalk_valid(root)

    authority_valid = all([
        not missing_paths,
        previous_valid,
        helper_valid,
        runtime_contracts_valid,
        dependency_valid,
        hygiene_valid,
        crosswalk_valid,
        record.get("commercial_runtime_blockers_remediated") is True,
        record.get("subscription_runtime_contract_fixed") is True,
        record.get("assessment_runtime_contract_fixed") is True,
        record.get("audit_2026_07_09_runtime_findings_reconciled") is True,
        record.get("dev_dependency_bootstrap_repaired") is True,
        record.get("security_dependency_baseline_recorded") is True,
        record.get("repository_hygiene_repaired") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_register.get("next_authorised_item") in ALLOWED_NEXT,
    ])

    final_recorded = record.get("commercial_final_evidence_recorded") is True
    reconciliation_recorded = record.get("prd9_final_reconciliation_recorded") is True
    sequence_complete = record.get("prd9_sequence_complete") is True
    handoff_authorised = record.get("prd10_handoff_authorised") is True
    valid = all([
        authority_valid,
        final_recorded,
        reconciliation_recorded,
        sequence_complete,
        handoff_authorised,
        record.get("next_authorised_item") == "PRD-10",
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_register.get("next_authorised_item") in ALLOWED_NEXT,
    ])

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "missing_paths": missing_paths,
        "previous_prd9_foundation_valid": previous_valid,
        "commercial_remediation_helper_valid": helper_valid,
        "runtime_code_contracts_valid": runtime_contracts_valid,
        "dependency_remediation_valid": dependency_valid,
        "repository_hygiene_valid": hygiene_valid,
        "audit_crosswalk_valid": crosswalk_valid,
        "commercial_runtime_blockers_remediated": record.get("commercial_runtime_blockers_remediated") is True,
        "commercial_final_evidence_recorded": final_recorded,
        "prd9_final_reconciliation_recorded": reconciliation_recorded,
        "prd9_sequence_complete": sequence_complete,
        "prd10_handoff_authorised": handoff_authorised,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        **{key: record.get(key) is True for key in FALSE_BOUNDARIES},
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
    raise SystemExit(0 if (result.get("authority_valid") if args.authority_only else result.get("valid")) else 1)
