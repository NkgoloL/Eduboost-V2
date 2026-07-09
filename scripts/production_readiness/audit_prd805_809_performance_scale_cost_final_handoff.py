"""Audit PRD-8.5-8.9 performance/scale/cost final assurance and handoff."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-8.5-8.9"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_805_809_performance_scale_cost_final_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd8_performance_scale_cost_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/performance_scale_cost/assurance.py",
    "app/modules/performance_scale_cost/__init__.py",
    "app/api_v2_routers/performance_scale_cost.py",
    "tests/unit/modules/performance_scale_cost/test_performance_scale_cost_final_assurance.py",
    "tests/unit/roadmap_reconciliation/test_prd805_809_performance_scale_cost_final_handoff.py",
    "docs/engineering/prd8_performance_scale_cost_final_handoff.md",
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
ALLOWED_NEXT = {"PRD-8.5-8.9", "PRD-9", "PRD-9.0-9.4", "PRD-9.5-9.9"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd8_foundation_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd800_804_performance_scale_cost_execution_foundation import audit as audit_prd800

        result = audit_prd800(root)
        if result.get("valid") is True:
            return True
    except Exception:
        pass

    record = root / "docs/roadmap/production_readiness/prd_800_804_performance_scale_cost_execution_foundation_record.json"
    if not record.exists():
        return False
    payload = json.loads(record.read_text())
    return all([
        payload.get("performance_scale_cost_foundation_recorded") is True,
        payload.get("performance_scale_cost_evidence_recorded") is True,
        payload.get("next_authorised_item") == "PRD-8.5-8.9",
    ])


def _performance_final_assurance_valid(root: Path) -> bool:
    try:
        from app.modules.performance_scale_cost import (
            FINAL_ASSURANCE_CRITERIA,
            PerformanceScaleCostFinalAssuranceReport,
            build_blocked_performance_scale_cost_final_assurance_report,
            build_default_performance_scale_cost_final_assurance_report,
            default_performance_scale_cost_final_evidence_items,
        )

        accepted = build_default_performance_scale_cost_final_assurance_report().to_payload()
        blocked = build_blocked_performance_scale_cost_final_assurance_report().to_payload()
        evidence_items = default_performance_scale_cost_final_evidence_items()
    except Exception:
        return False

    route = (root / "app/api_v2_routers/performance_scale_cost.py").read_text() if (root / "app/api_v2_routers/performance_scale_cost.py").exists() else ""
    init_text = (root / "app/modules/performance_scale_cost/__init__.py").read_text() if (root / "app/modules/performance_scale_cost/__init__.py").exists() else ""

    return all([
        accepted.get("prd_id") == PRD_ID,
        accepted.get("source_readiness_prd_id") == "PRD-8.0-8.4",
        accepted.get("accepted") is True,
        accepted.get("load_test_evidence_accepted") is True,
        accepted.get("runtime_kg_query_performance_evidence_accepted") is True,
        accepted.get("database_index_review_evidence_accepted") is True,
        accepted.get("llm_cost_guardrail_evidence_accepted") is True,
        accepted.get("queue_backpressure_capacity_evidence_accepted") is True,
        accepted.get("frontend_performance_budget_evidence_accepted") is True,
        accepted.get("scale_cost_reconciliation_recorded") is True,
        accepted.get("performance_signoff_recorded") is True,
        accepted.get("prd8_final_reconciliation_recorded") is True,
        accepted.get("prd9_implementation_authorised") is False,
        accepted.get("billing_launch_authorised") is False,
        accepted.get("live_payment_processing_authorised") is False,
        accepted.get("live_learner_traffic_authorised") is False,
        blocked.get("accepted") is False,
        "final_performance_scale_cost_evidence_matrix_incomplete" in blocked.get("blockers", []),
        len(FINAL_ASSURANCE_CRITERIA) >= 7,
        len(evidence_items) >= 8,
        all(item.accepted for item in evidence_items),
        "get_performance_scale_cost_final_assurance" in route,
        "build_default_performance_scale_cost_final_assurance_report" in route,
        "PerformanceScaleCostFinalAssuranceReport" in init_text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    previous_valid = _previous_prd8_foundation_valid(root)
    final_helper_valid = _performance_final_assurance_valid(root)

    prod_next = prod_register.get("next_authorised_item")
    authority_valid = all([
        not missing_paths,
        previous_valid,
        final_helper_valid,
        record.get("performance_final_assurance_helper_added") is True,
        record.get("performance_final_assurance_route_added") is True,
        record.get("load_test_evidence_defined") is True,
        record.get("runtime_kg_query_performance_evidence_defined") is True,
        record.get("database_index_review_evidence_defined") is True,
        record.get("llm_cost_guardrail_evidence_defined") is True,
        record.get("queue_backpressure_capacity_evidence_defined") is True,
        record.get("frontend_performance_budget_evidence_defined") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
    ])

    final_evidence_recorded = record.get("performance_final_assurance_evidence_recorded") is True
    scale_cost_reconciliation = record.get("scale_cost_reconciliation_recorded") is True
    signoff_recorded = record.get("performance_signoff_recorded") is True
    reconciliation_recorded = record.get("prd8_final_reconciliation_recorded") is True
    sequence_complete = record.get("prd8_sequence_complete") is True
    handoff = record.get("prd9_handoff_authorised") is True

    valid = all([
        authority_valid,
        final_evidence_recorded,
        scale_cost_reconciliation,
        signoff_recorded,
        reconciliation_recorded,
        sequence_complete,
        handoff,
        record.get("next_authorised_item") == "PRD-9",
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_register.get("next_authorised_item") in ALLOWED_NEXT,
    ])

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-8.5", "PRD-8.6", "PRD-8.7", "PRD-8.8", "PRD-8.9"]),
        "missing_paths": missing_paths,
        "previous_prd8_foundation_valid": previous_valid,
        "performance_final_assurance_valid": final_helper_valid,
        "performance_final_assurance_evidence_recorded": final_evidence_recorded,
        "scale_cost_reconciliation_recorded": scale_cost_reconciliation,
        "performance_signoff_recorded": signoff_recorded,
        "prd8_final_reconciliation_recorded": reconciliation_recorded,
        "prd8_sequence_complete": sequence_complete,
        "prd9_handoff_authorised": handoff,
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
