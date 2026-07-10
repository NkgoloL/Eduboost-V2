"""Audit PRD-10.0-10.4 controlled beta/live traffic preflight foundation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-10.0-10.4"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1000_1004_controlled_beta_live_traffic_preflight_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd10_controlled_beta_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PYJWT_REPORT = ROOT / "docs/security/jwt_pyjwt_migration_report.json"
REQUIRED_PATHS = [
    "app/core/jwt_compat.py",
    "app/modules/controlled_beta/preflight.py",
    "app/modules/controlled_beta/__init__.py",
    "app/api_v2_routers/controlled_beta.py",
    "docs/engineering/prd10_controlled_beta_live_traffic_preflight_foundation.md",
    "docs/security/jwt_pyjwt_migration_report.json",
    "docs/roadmap/production_readiness/prd10_controlled_beta_register.json",
    "docs/roadmap/production_readiness/prd_1000_1004_controlled_beta_live_traffic_preflight_foundation_record.json",
    "tests/unit/modules/controlled_beta/test_controlled_beta_preflight.py",
    "tests/unit/test_prd10_pyjwt_migration.py",
    "tests/unit/roadmap_reconciliation/test_prd1000_1004_controlled_beta_live_traffic_preflight_foundation.py",
]
FALSE_BOUNDARIES = [
    "prd11_implementation_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "live_learner_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]
ALLOWED_NEXT = {"PRD-10.0-10.4", "PRD-10.5-10.9", "PRD-11"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd9_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd905_909_commercial_runtime_audit_remediation_handoff import audit as audit_prd905
        result = audit_prd905(root)
        return result.get("valid") is True or all([
            result.get("authority_valid") is True,
            result.get("commercial_runtime_blockers_remediated") is True,
            result.get("prd10_handoff_authorised") is True,
        ])
    except Exception:
        return False


def _pyjwt_migration_valid(root: Path) -> bool:
    app_files = [
        "app/api_v2_deps/auth.py",
        "app/core/dependencies.py",
        "app/core/exceptions.py",
        "app/core/security.py",
        "app/core/token_config.py",
        "app/services/jwt_keyring.py",
    ]
    app_text = "\n".join((root / path).read_text() for path in app_files if (root / path).exists())
    req_text = "\n".join((root / path).read_text() for path in ["requirements/base.in", "requirements/base.txt", "requirements/dev.txt", "requirements/constraints.snapshot.txt"] if (root / path).exists())
    report = _load_json(root / PYJWT_REPORT.relative_to(ROOT))
    runtime_dep_script = (root / "scripts/audit_remediation/verify_backend_fast_runtime_dependencies.py").read_text()
    env_script = (root / "scripts/audit_remediation/verify_backend_fast_environment.py").read_text()
    return all([
        "from jose" not in app_text,
        "import jose" not in app_text,
        "python-jose" not in req_text.lower(),
        "pyjwt[crypto]==2.12.1" in (root / "requirements/base.in").read_text().lower(),
        "import jwt as _pyjwt" in (root / "app/core/jwt_compat.py").read_text(),
        "decode_options(options)" in (root / "app/services/jwt_keyring.py").read_text(),
        "decode_options()" in (root / "app/core/token_config.py").read_text(),
        report.get("status") == "python_jose_removed_pyjwt_active",
        report.get("legacy_library_removed_from_requirements") == "python-jose",
        report.get("live_learner_traffic_authorised") is False,
        '"jwt": "PyJWT"' in runtime_dep_script,
        '("jwt", "JWT/token tests", "requirements/base.txt")' in env_script,
    ])


def _preflight_helper_valid(root: Path) -> bool:
    try:
        from app.modules.controlled_beta import (
            build_blocked_controlled_beta_preflight_report,
            build_default_controlled_beta_preflight_report,
        )
        ready = build_default_controlled_beta_preflight_report().to_payload()
        blocked = build_blocked_controlled_beta_preflight_report().to_payload()
    except Exception:
        return False
    route_text = (root / "app/api_v2_routers/controlled_beta.py").read_text() if (root / "app/api_v2_routers/controlled_beta.py").exists() else ""
    api_text = (root / "app/api_v2.py").read_text() if (root / "app/api_v2.py").exists() else ""
    slim_text = (root / "app/api_v2_routers/api_v2.py").read_text() if (root / "app/api_v2_routers/api_v2.py").exists() else ""
    return all([
        ready.get("prd_id") == PRD_ID,
        ready.get("accepted") is True,
        ready.get("controlled_beta_preflight_defined") is True,
        ready.get("pyjwt_auth_regression_gate_defined") is True,
        ready.get("cohort_consent_eligibility_gate_defined") is True,
        ready.get("dry_run_kill_switch_rollback_defined") is True,
        ready.get("support_monitoring_incident_go_no_go_defined") is True,
        ready.get("live_learner_traffic_authorised") is False,
        ready.get("public_beta_authorised") is False,
        ready.get("production_release_authorised") is False,
        blocked.get("accepted") is False,
        "controlled_beta_preflight_incomplete" in blocked.get("blockers", []),
        "get_controlled_beta_preflight" in route_text,
        "controlled_beta.router" in api_text,
        "controlled_beta.router" in slim_text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    previous_valid = _previous_prd9_valid(root)
    pyjwt_valid = _pyjwt_migration_valid(root)
    preflight_valid = _preflight_helper_valid(root)
    authority_valid = all([
        not missing_paths,
        previous_valid,
        pyjwt_valid,
        preflight_valid,
        record.get("controlled_beta_preflight_foundation_recorded") is True,
        record.get("pyjwt_migration_completed") is True,
        record.get("auth_token_regression_gate_recorded") is True,
        record.get("controlled_beta_cohort_gate_recorded") is True,
        record.get("guardian_consent_eligibility_gate_recorded") is True,
        record.get("dry_run_kill_switch_rollback_gate_recorded") is True,
        record.get("support_monitoring_incident_go_no_go_gate_recorded") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod.get("next_authorised_item") in ALLOWED_NEXT,
    ])
    evidence_recorded = record.get("controlled_beta_preflight_evidence_recorded") is True
    valid = all([
        authority_valid,
        evidence_recorded,
        record.get("next_authorised_item") == "PRD-10.5-10.9",
        register.get("next_authorised_item") == "PRD-10.5-10.9",
        prod.get("next_authorised_item") == "PRD-10.5-10.9",
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "missing_paths": missing_paths,
        "previous_prd9_handoff_valid": previous_valid,
        "pyjwt_migration_valid": pyjwt_valid,
        "controlled_beta_preflight_valid": preflight_valid,
        "controlled_beta_preflight_foundation_recorded": record.get("controlled_beta_preflight_foundation_recorded") is True,
        "controlled_beta_preflight_evidence_recorded": evidence_recorded,
        "auth_token_regression_gate_recorded": record.get("auth_token_regression_gate_recorded") is True,
        "cohort_consent_eligibility_gate_recorded": record.get("controlled_beta_cohort_gate_recorded") is True and record.get("guardian_consent_eligibility_gate_recorded") is True,
        "dry_run_kill_switch_rollback_gate_recorded": record.get("dry_run_kill_switch_rollback_gate_recorded") is True,
        "support_monitoring_incident_go_no_go_gate_recorded": record.get("support_monitoring_incident_go_no_go_gate_recorded") is True,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod.get("next_authorised_item"),
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
