"""Audit PRD-8.0-8.4 performance, scale, and cost execution foundation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-8.0-8.4"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_800_804_performance_scale_cost_execution_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd8_performance_scale_cost_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/performance_scale_cost/readiness.py",
    "app/modules/performance_scale_cost/__init__.py",
    "app/api_v2_routers/performance_scale_cost.py",
    "tests/unit/modules/performance_scale_cost/test_performance_scale_cost_readiness.py",
    "tests/unit/roadmap_reconciliation/test_prd800_804_performance_scale_cost_execution_foundation.py",
    "docs/engineering/prd8_performance_scale_cost_execution_foundation.md",
]
FALSE_BOUNDARIES = [
    "prd9_implementation_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "live_learner_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]
ALLOWED_NEXT = {"PRD-8.0-8.4", "PRD-8.5-8.9", "PRD-9", "PRD-9.0-9.4", "PRD-9.5-9.9"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd7_handoff_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd705_709_observability_sre_final_handoff import audit as audit_prd705

        result = audit_prd705(root)
        if result.get("valid") is True:
            return True
    except Exception:
        pass

    record = root / "docs/roadmap/production_readiness/prd_705_709_observability_sre_final_handoff_record.json"
    if not record.exists():
        return False
    payload = json.loads(record.read_text())
    return all([
        payload.get("observability_final_assurance_evidence_recorded") is True,
        payload.get("prd7_sequence_complete") is True,
        payload.get("prd8_handoff_authorised") is True,
        payload.get("next_authorised_item") == "PRD-8",
    ])


def _performance_scale_cost_readiness_valid(root: Path) -> bool:
    try:
        from app.modules.performance_scale_cost import (
            PERFORMANCE_COST_EVIDENCE_AREAS,
            PerformanceScaleCostReadinessReport,
            build_blocked_performance_scale_cost_readiness_report,
            build_default_performance_scale_cost_readiness_report,
            default_performance_scale_cost_evidence_controls,
        )

        accepted = build_default_performance_scale_cost_readiness_report().to_payload()
        blocked = build_blocked_performance_scale_cost_readiness_report().to_payload()
        controls = default_performance_scale_cost_evidence_controls()
    except Exception:
        return False

    route = (root / "app/api_v2_routers/performance_scale_cost.py").read_text() if (root / "app/api_v2_routers/performance_scale_cost.py").exists() else ""
    init_text = (root / "app/modules/performance_scale_cost/__init__.py").read_text() if (root / "app/modules/performance_scale_cost/__init__.py").exists() else ""

    return all([
        accepted.get("prd_id") == PRD_ID,
        accepted.get("ready") is True,
        accepted.get("performance_execution_defined") is True,
        accepted.get("scale_execution_defined") is True,
        accepted.get("cost_execution_defined") is True,
        accepted.get("evidence_matrix_ready") is True,
        accepted.get("runtime_kg_query_performance_defined") is True,
        accepted.get("llm_cost_simulation_defined") is True,
        accepted.get("queue_backpressure_tests_defined") is True,
        accepted.get("frontend_performance_budget_defined") is True,
        accepted.get("prd9_implementation_authorised") is False,
        accepted.get("live_learner_traffic_authorised") is False,
        blocked.get("ready") is False,
        "performance_scale_cost_evidence_matrix_incomplete" in blocked.get("blockers", []),
        len(PERFORMANCE_COST_EVIDENCE_AREAS) >= 7,
        len(controls) == len(PERFORMANCE_COST_EVIDENCE_AREAS),
        all(control.ready for control in controls),
        "get_performance_scale_cost_readiness" in route,
        "build_default_performance_scale_cost_readiness_report" in route,
        "PerformanceScaleCostReadinessReport" in init_text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    previous_valid = _previous_prd7_handoff_valid(root)
    readiness_valid = _performance_scale_cost_readiness_valid(root)
    prod_next = prod_register.get("next_authorised_item")

    authority_valid = all([
        not missing_paths,
        previous_valid,
        readiness_valid,
        record.get("performance_scale_cost_readiness_helper_added") is True,
        record.get("performance_scale_cost_route_added") is True,
        record.get("load_test_readiness_defined") is True,
        record.get("runtime_kg_query_performance_defined") is True,
        record.get("database_index_review_defined") is True,
        record.get("llm_cost_simulation_defined") is True,
        record.get("queue_backpressure_defined") is True,
        record.get("frontend_performance_budget_defined") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_next in {"PRD-8", *ALLOWED_NEXT},
    ])

    foundation_recorded = record.get("performance_scale_cost_foundation_recorded") is True
    evidence_recorded = record.get("performance_scale_cost_evidence_recorded") is True

    valid = all([
        authority_valid,
        foundation_recorded,
        evidence_recorded,
        record.get("next_authorised_item") == "PRD-8.5-8.9",
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_register.get("next_authorised_item") in ALLOWED_NEXT,
    ])

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-8.0", "PRD-8.1", "PRD-8.2", "PRD-8.3", "PRD-8.4"]),
        "missing_paths": missing_paths,
        "previous_prd7_handoff_valid": previous_valid,
        "performance_scale_cost_readiness_valid": readiness_valid,
        "performance_scale_cost_foundation_recorded": foundation_recorded,
        "performance_scale_cost_evidence_recorded": evidence_recorded,
        "load_test_readiness_defined": record.get("load_test_readiness_defined") is True,
        "runtime_kg_query_performance_defined": record.get("runtime_kg_query_performance_defined") is True,
        "database_index_review_defined": record.get("database_index_review_defined") is True,
        "llm_cost_simulation_defined": record.get("llm_cost_simulation_defined") is True,
        "queue_backpressure_defined": record.get("queue_backpressure_defined") is True,
        "frontend_performance_budget_defined": record.get("frontend_performance_budget_defined") is True,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "prd9_implementation_authorised": record.get("prd9_implementation_authorised") is True,
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
