"""Audit PRD-11.0-11.4 production release/deployment preflight foundation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-11.0-11.4"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100_1104_production_release_deployment_preflight_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/production_release/readiness.py",
    "app/modules/production_release/__init__.py",
    "app/api_v2_routers/production_release.py",
    "docs/engineering/prd11_production_release_deployment_preflight_foundation.md",
    "docs/roadmap/production_readiness/prd11_production_release_register.json",
    "docs/roadmap/production_readiness/prd_1100_1104_production_release_deployment_preflight_foundation_record.json",
    "tests/unit/modules/production_release/test_production_release_preflight.py",
    "tests/unit/roadmap_reconciliation/test_prd1100_1104_production_release_deployment_preflight_foundation.py",
]
FALSE_BOUNDARIES = [
    "prd12_implementation_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]
ALLOWED_NEXT = {"PRD-11.0R", "PRD-11.0R.RUNTIME-RESTORE", "PRD-11.0-11.4", "PRD-11.5-11.9"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd10_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd1005_1009_controlled_beta_final_live_traffic_handoff import audit as audit_prd1005
        result = audit_prd1005(root)
        return result.get("valid") is True or all([
            result.get("authority_valid") is True,
            result.get("controlled_beta_final_evidence_recorded") is True,
            result.get("prd11_handoff_authorised") is True,
            result.get("live_learner_traffic_authorised") is True,
        ])
    except Exception:
        return False



def _runtime_baseline_evidence_unblocked(root: Path) -> bool:
    prod = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    current_truth = prod.get("current_truth", {}) if isinstance(prod.get("current_truth"), dict) else {}
    return all([
        current_truth.get("prd11_0r_true_state_runtime_baseline_evidence_recorded") is True,
        current_truth.get("prd11_0r_runtime_baseline_green") is True,
        current_truth.get("controlled_beta_activation_operational_hold") is False,
        current_truth.get("production_release_evidence_blocked_until_runtime_baseline_green") is False,
    ])

def _preflight_helper_valid(root: Path) -> bool:
    try:
        from app.modules.production_release import (
            build_blocked_production_release_preflight_report,
            build_default_production_release_preflight_report,
        )
        ready = build_default_production_release_preflight_report().to_payload()
        blocked = build_blocked_production_release_preflight_report().to_payload()
    except Exception:
        return False
    route_text = (root / "app/api_v2_routers/production_release.py").read_text() if (root / "app/api_v2_routers/production_release.py").exists() else ""
    api_text = (root / "app/api_v2.py").read_text() if (root / "app/api_v2.py").exists() else ""
    slim_text = (root / "app/api_v2_routers/api_v2.py").read_text() if (root / "app/api_v2_routers/api_v2.py").exists() else ""
    return all([
        ready.get("prd_id") == PRD_ID,
        ready.get("accepted") is True,
        ready.get("production_release_preflight_defined") is True,
        ready.get("release_candidate_artifact_gate_defined") is True,
        ready.get("release_tag_freeze_gate_defined") is True,
        ready.get("deployment_environment_preflight_defined") is True,
        ready.get("database_migration_rollback_gate_defined") is True,
        ready.get("controlled_beta_to_production_go_no_go_defined") is True,
        ready.get("support_monitoring_incident_release_comms_defined") is True,
        ready.get("production_release_dry_run_gate_defined") is True,
        ready.get("controlled_beta_live_traffic_authorised") is True,
        ready.get("live_learner_traffic_authorised") is True,
        ready.get("production_release_authorised") is False,
        ready.get("deployment_authorised") is False,
        ready.get("release_tag_authorised") is False,
        ready.get("public_beta_authorised") is False,
        ready.get("billing_launch_authorised") is False,
        ready.get("live_payment_processing_authorised") is False,
        blocked.get("accepted") is False,
        "get_production_release_preflight" in route_text,
        "production_release.router" in api_text,
        "production_release.router" in slim_text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    prod_boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    current_truth = prod.get("current_truth", {}) if isinstance(prod.get("current_truth"), dict) else {}
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    previous_valid = _previous_prd10_valid(root)
    preflight_valid = _preflight_helper_valid(root)
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    controlled_beta_preserved = record.get("controlled_beta_live_traffic_authorised") is True and record.get("live_learner_traffic_authorised") is True
    authority_valid = all([
        not missing_paths,
        previous_valid,
        preflight_valid,
        record.get("prd11_production_release_preflight_foundation_recorded") is True,
        record.get("release_gate_definition_recorded") is True,
        record.get("release_candidate_artifact_gate_recorded") is True,
        record.get("release_tag_freeze_gate_recorded") is True,
        record.get("deployment_environment_preflight_recorded") is True,
        record.get("secrets_config_preflight_recorded") is True,
        record.get("database_migration_rollback_gate_recorded") is True,
        record.get("controlled_beta_to_production_go_no_go_gate_recorded") is True,
        record.get("support_monitoring_incident_release_comms_gate_recorded") is True,
        record.get("production_release_dry_run_gate_recorded") is True,
        controlled_beta_preserved,
        false_boundaries_preserved,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod.get("next_authorised_item") in ALLOWED_NEXT,
        prod_boundaries.get("production_release_authorised") is False,
        prod_boundaries.get("deployment_authorised") is False,
        prod_boundaries.get("release_tag_authorised") is False,
        prod_boundaries.get("public_beta_authorised") is False,
    ])
    evidence_recorded = record.get("production_release_preflight_evidence_recorded") is True
    runtime_baseline_evidence_unblocked = _runtime_baseline_evidence_unblocked(root)
    valid = all([
        authority_valid,
        runtime_baseline_evidence_unblocked,
        evidence_recorded,
        record.get("next_authorised_item") == "PRD-11.5-11.9",
        register.get("next_authorised_item") == "PRD-11.5-11.9",
        prod.get("next_authorised_item") == "PRD-11.5-11.9",
        current_truth.get("prd11_production_release_preflight_evidence_recorded") is True,
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "missing_paths": missing_paths,
        "previous_prd10_handoff_valid": previous_valid,
        "production_release_preflight_valid": preflight_valid,
        "prd11_production_release_preflight_foundation_recorded": record.get("prd11_production_release_preflight_foundation_recorded") is True,
        "production_release_preflight_evidence_recorded": evidence_recorded,
        "runtime_baseline_evidence_unblocked": _runtime_baseline_evidence_unblocked(root),
        "release_gate_definition_recorded": record.get("release_gate_definition_recorded") is True,
        "release_candidate_artifact_gate_recorded": record.get("release_candidate_artifact_gate_recorded") is True,
        "deployment_environment_preflight_recorded": record.get("deployment_environment_preflight_recorded") is True,
        "database_migration_rollback_gate_recorded": record.get("database_migration_rollback_gate_recorded") is True,
        "controlled_beta_to_production_go_no_go_gate_recorded": record.get("controlled_beta_to_production_go_no_go_gate_recorded") is True,
        "support_monitoring_incident_release_comms_gate_recorded": record.get("support_monitoring_incident_release_comms_gate_recorded") is True,
        "production_release_dry_run_gate_recorded": record.get("production_release_dry_run_gate_recorded") is True,
        "controlled_beta_live_traffic_authorised": record.get("controlled_beta_live_traffic_authorised") is True,
        "live_learner_traffic_authorised": record.get("live_learner_traffic_authorised") is True,
        "production_release_authorised": record.get("production_release_authorised") is True,
        "deployment_authorised": record.get("deployment_authorised") is True,
        "release_tag_authorised": record.get("release_tag_authorised") is True,
        "public_beta_authorised": record.get("public_beta_authorised") is True,
        "billing_launch_authorised": record.get("billing_launch_authorised") is True,
        "live_payment_processing_authorised": record.get("live_payment_processing_authorised") is True,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod.get("next_authorised_item"),
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
