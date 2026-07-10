"""Audit PRD-10.5-10.9 controlled beta final live-traffic handoff."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-10.5-10.9"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1005_1009_controlled_beta_final_live_traffic_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd10_controlled_beta_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/controlled_beta/authorisation.py",
    "app/modules/controlled_beta/__init__.py",
    "app/api_v2_routers/controlled_beta.py",
    "docs/engineering/prd10_controlled_beta_final_live_traffic_handoff.md",
    "docs/roadmap/production_readiness/prd10_controlled_beta_register.json",
    "docs/roadmap/production_readiness/prd_1005_1009_controlled_beta_final_live_traffic_handoff_record.json",
    "tests/unit/modules/controlled_beta/test_controlled_beta_final_authorisation.py",
    "tests/unit/roadmap_reconciliation/test_prd1005_1009_controlled_beta_final_live_traffic_handoff.py",
]
LOCKED_FALSE_BOUNDARIES = [
    "prd11_implementation_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]
ALLOWED_NEXT = {"PRD-10.5-10.9", "PRD-11", "PRD-11.0-11.4", "PRD-11.5-11.9"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_preflight_valid(root: Path) -> bool:
    record = _load_json(root / "docs/roadmap/production_readiness/prd_1000_1004_controlled_beta_live_traffic_preflight_foundation_record.json")
    register = _load_json(root / "docs/roadmap/production_readiness/prd10_controlled_beta_register.json")
    prod = _load_json(root / "docs/roadmap/production_readiness/production_readiness_register.json")
    current_truth = prod.get("current_truth", {}) if isinstance(prod.get("current_truth"), dict) else {}
    return all([
        record.get("controlled_beta_preflight_foundation_recorded") is True,
        record.get("controlled_beta_preflight_evidence_recorded") is True,
        record.get("pyjwt_migration_completed") is True,
        register.get("controlled_beta_preflight_evidence_recorded") is True,
        current_truth.get("prd10_controlled_beta_preflight_evidence_recorded") is True,
    ])


def _final_helper_valid(root: Path) -> bool:
    try:
        from app.modules.controlled_beta import (
            build_blocked_controlled_beta_final_authorisation_report,
            build_default_controlled_beta_final_authorisation_report,
        )
        ready = build_default_controlled_beta_final_authorisation_report().to_payload()
        blocked = build_blocked_controlled_beta_final_authorisation_report().to_payload()
    except Exception:
        return False
    route_text = (root / "app/api_v2_routers/controlled_beta.py").read_text() if (root / "app/api_v2_routers/controlled_beta.py").exists() else ""
    return all([
        ready.get("prd_id") == PRD_ID,
        ready.get("accepted") is True,
        ready.get("controlled_beta_final_evidence_accepted") is True,
        ready.get("cohort_guardian_consent_learner_eligibility_accepted") is True,
        ready.get("auth_token_regression_accepted") is True,
        ready.get("dry_run_kill_switch_rollback_accepted") is True,
        ready.get("support_monitoring_incident_go_no_go_accepted") is True,
        ready.get("controlled_beta_live_traffic_authorised") is True,
        ready.get("live_learner_traffic_authorised") is True,
        ready.get("prd11_handoff_authorised") is True,
        ready.get("public_beta_authorised") is False,
        ready.get("production_release_authorised") is False,
        ready.get("billing_launch_authorised") is False,
        blocked.get("accepted") is False,
        blocked.get("live_learner_traffic_authorised") is False,
        "get_controlled_beta_final_authorisation" in route_text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    prod_boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    current_truth = prod.get("current_truth", {}) if isinstance(prod.get("current_truth"), dict) else {}
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    previous_valid = _previous_preflight_valid(root)
    final_helper_valid = _final_helper_valid(root)
    locked_boundaries_preserved = all(record.get(key) is False for key in LOCKED_FALSE_BOUNDARIES)
    live_decision_safe = (
        record.get("live_learner_traffic_authorised") is False
        or (
            record.get("live_learner_traffic_authorised") is True
            and record.get("controlled_beta_final_evidence_recorded") is True
            and record.get("controlled_beta_live_traffic_authorised") is True
        )
    )
    authority_valid = all([
        not missing_paths,
        previous_valid,
        final_helper_valid,
        record.get("controlled_beta_final_authority_recorded") is True,
        record.get("cohort_guardian_consent_learner_eligibility_evidence_accepted") is True,
        record.get("auth_token_regression_evidence_accepted") is True,
        record.get("dry_run_kill_switch_rollback_evidence_accepted") is True,
        record.get("support_monitoring_incident_go_no_go_evidence_accepted") is True,
        record.get("live_learner_traffic_authorisation_decision_recorded") is True,
        locked_boundaries_preserved,
        live_decision_safe,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod.get("next_authorised_item") in ALLOWED_NEXT,
    ])
    evidence_recorded = record.get("controlled_beta_final_evidence_recorded") is True
    valid = all([
        authority_valid,
        evidence_recorded,
        record.get("controlled_beta_live_traffic_authorised") is True,
        record.get("live_learner_traffic_authorised") is True,
        record.get("prd10_final_reconciliation_recorded") is True,
        record.get("prd10_sequence_complete") is True,
        record.get("prd11_handoff_authorised") is True,
        record.get("next_authorised_item") in ALLOWED_NEXT,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        register.get("live_learner_traffic_authorised") is True,
        register.get("prd10_sequence_complete") is True,
        prod.get("next_authorised_item") in ALLOWED_NEXT,
        prod_boundaries.get("live_learner_traffic_authorised") is True,
        prod_boundaries.get("public_beta_authorised") is False,
        prod_boundaries.get("production_release_authorised") is False,
        current_truth.get("prd10_closed") is True,
        current_truth.get("prd10_handoff_authorised") is True,
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "missing_paths": missing_paths,
        "previous_prd10_preflight_valid": previous_valid,
        "controlled_beta_final_authorisation_valid": final_helper_valid,
        "controlled_beta_final_authority_recorded": record.get("controlled_beta_final_authority_recorded") is True,
        "controlled_beta_final_evidence_recorded": evidence_recorded,
        "cohort_guardian_consent_learner_eligibility_evidence_accepted": record.get("cohort_guardian_consent_learner_eligibility_evidence_accepted") is True,
        "auth_token_regression_evidence_accepted": record.get("auth_token_regression_evidence_accepted") is True,
        "dry_run_kill_switch_rollback_evidence_accepted": record.get("dry_run_kill_switch_rollback_evidence_accepted") is True,
        "support_monitoring_incident_go_no_go_evidence_accepted": record.get("support_monitoring_incident_go_no_go_evidence_accepted") is True,
        "controlled_beta_live_traffic_authorised": record.get("controlled_beta_live_traffic_authorised") is True,
        "live_learner_traffic_authorised": record.get("live_learner_traffic_authorised") is True,
        "public_beta_authorised": record.get("public_beta_authorised") is True,
        "production_release_authorised": record.get("production_release_authorised") is True,
        "billing_launch_authorised": record.get("billing_launch_authorised") is True,
        "live_payment_processing_authorised": record.get("live_payment_processing_authorised") is True,
        "prd10_final_reconciliation_recorded": record.get("prd10_final_reconciliation_recorded") is True,
        "prd10_sequence_complete": record.get("prd10_sequence_complete") is True,
        "prd11_handoff_authorised": record.get("prd11_handoff_authorised") is True,
        "prd11_implementation_authorised": record.get("prd11_implementation_authorised") is True,
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
