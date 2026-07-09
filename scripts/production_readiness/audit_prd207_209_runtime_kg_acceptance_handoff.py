"""Audit PRD-2.7-2.9 runtime KG acceptance and handoff."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-2.7-2.9"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_207_209_runtime_kg_acceptance_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd2_runtime_kg_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/services/runtime_kg/acceptance.py",
    "app/services/runtime_kg/feature_flags.py",
    "app/services/runtime_kg/route_integration.py",
    "app/services/runtime_kg/repository.py",
    "app/api_v2_routers/diagnostics.py",
    "app/api_v2_routers/study_plans.py",
    "app/modules/lessons/service.py",
    "tests/unit/runtime_kg/test_runtime_kg_acceptance.py",
    "tests/unit/roadmap_reconciliation/test_prd207_209_runtime_kg_acceptance_handoff.py",
    "docs/engineering/prd2_runtime_kg_acceptance_handoff.md",
]
FALSE_BOUNDARIES = [
    "prd3_implementation_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "live_learner_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _route_projection_valid(root: Path) -> bool:
    diagnostics = (root / "app/api_v2_routers/diagnostics.py").read_text() if (root / "app/api_v2_routers/diagnostics.py").exists() else ""
    study = (root / "app/api_v2_routers/study_plans.py").read_text() if (root / "app/api_v2_routers/study_plans.py").exists() else ""
    lessons = (root / "app/modules/lessons/service.py").read_text() if (root / "app/modules/lessons/service.py").exists() else ""
    route = (root / "app/services/runtime_kg/route_integration.py").read_text() if (root / "app/services/runtime_kg/route_integration.py").exists() else ""
    return all([
        "build_runtime_kg_diagnostic_projection" in diagnostics,
        "runtime_kg_projection" in diagnostics,
        "build_runtime_kg_study_plan_payload" in study,
        "runtime_kg" in study,
        "build_lesson_context_with_runtime_kg" in lessons,
        "fallback_to_legacy" in route,
    ])


def _foundation_and_route_records_valid(root: Path) -> bool:
    foundation = _load_json(root / "docs/roadmap/production_readiness/prd_200_203_runtime_kg_persistence_foundation_record.json")
    route = _load_json(root / "docs/roadmap/production_readiness/prd_204_206_runtime_kg_route_projection_behaviour_record.json")
    return all([
        foundation.get("runtime_kg_persistence_foundation_recorded") is True,
        foundation.get("runtime_kg_models_added") is True,
        foundation.get("runtime_kg_migration_added") is True,
        foundation.get("idempotent_graph_loader_added") is True,
        route.get("runtime_kg_route_projection_behaviour_recorded") is True,
        route.get("diagnostic_route_projection_integrated") is True,
        route.get("study_plan_route_focus_integrated") is True,
        route.get("rollback_to_legacy_proven") is True,
    ])


def _acceptance_report_valid() -> bool:
    try:
        from app.services.runtime_kg.acceptance import build_runtime_kg_acceptance_report

        payload = build_runtime_kg_acceptance_report().to_payload()
    except Exception:
        return False
    return (
        payload.get("accepted") is True
        and payload.get("runtime_kg_enabled_by_default") is False
        and payload.get("next_authorised_item") == "PRD-3"
        and payload.get("prd3_implementation_authorised") is False
    )


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    flags_text = (root / "app/services/runtime_kg/feature_flags.py").read_text() if (root / "app/services/runtime_kg/feature_flags.py").exists() else ""
    acceptance_text = (root / "app/services/runtime_kg/acceptance.py").read_text() if (root / "app/services/runtime_kg/acceptance.py").exists() else ""
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    authority_valid = all([
        not missing_paths,
        _foundation_and_route_records_valid(root),
        _route_projection_valid(root),
        _acceptance_report_valid(),
        "enabled: bool = False" in flags_text,
        "RuntimeKGAcceptanceReport" in acceptance_text,
        record.get("runtime_kg_acceptance_helper_added") is True,
        record.get("runtime_kg_enabled_by_default") is False,
        false_boundaries_preserved,
        register.get("next_authorised_item") in {"PRD-2.7-2.9", "PRD-3", "PRD-3.0-3.4", "PRD-3.5-3.9", "PRD-4"},
        prod_register.get("next_authorised_item") in {"PRD-2.7-2.9", "PRD-3", "PRD-3.0-3.4", "PRD-3.5-3.9", "PRD-4"},
    ])
    recorded = record.get("runtime_kg_acceptance_recorded") is True
    final_evidence_recorded = record.get("runtime_kg_final_evidence_recorded") is True
    reconciliation_recorded = record.get("prd2_final_reconciliation_recorded") is True
    sequence_complete = record.get("prd2_sequence_complete") is True
    handoff = record.get("prd3_handoff_authorised") is True
    valid = all([
        authority_valid,
        recorded,
        final_evidence_recorded,
        reconciliation_recorded,
        sequence_complete,
        handoff,
        record.get("next_authorised_item") == "PRD-3",
        register.get("next_authorised_item") in {"PRD-3", "PRD-3.0-3.4", "PRD-3.5-3.9"},
        prod_register.get("next_authorised_item") in {"PRD-3", "PRD-3.0-3.4", "PRD-3.5-3.9"},
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-2.7", "PRD-2.8", "PRD-2.9"]),
        "missing_paths": missing_paths,
        "foundation_and_route_records_valid": _foundation_and_route_records_valid(root),
        "runtime_kg_route_projection_valid": _route_projection_valid(root),
        "runtime_kg_acceptance_report_valid": _acceptance_report_valid(),
        "runtime_kg_acceptance_recorded": recorded,
        "runtime_kg_final_evidence_recorded": final_evidence_recorded,
        "prd2_final_reconciliation_recorded": reconciliation_recorded,
        "prd2_sequence_complete": sequence_complete,
        "prd3_handoff_authorised": handoff,
        "runtime_kg_enabled_by_default": record.get("runtime_kg_enabled_by_default"),
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "prd3_implementation_authorised": record.get("prd3_implementation_authorised") is True,
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
