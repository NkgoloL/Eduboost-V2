"""Audit PRD-2.4-2.6 runtime KG route projection behaviour."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-2.4-2.6"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_204_206_runtime_kg_route_projection_behaviour_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd2_runtime_kg_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/services/runtime_kg/route_integration.py",
    "app/services/runtime_kg/repository.py",
    "app/api_v2_routers/diagnostics.py",
    "app/api_v2_routers/study_plans.py",
    "app/domain/schemas.py",
    "tests/unit/runtime_kg/test_runtime_kg_route_projection_behaviour.py",
    "tests/unit/roadmap_reconciliation/test_prd204_206_runtime_kg_route_projection_behaviour.py",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _run_foundation_verifier() -> dict[str, Any]:
    """Return stable PRD-2.0-2.3 handoff proof without re-entering older verifier chains."""

    record = _load_json(ROOT / "docs/roadmap/production_readiness/prd_200_203_runtime_kg_persistence_foundation_record.json")
    register = _load_json(REGISTER)
    archival_valid = (
        record.get("runtime_kg_persistence_foundation_recorded") is True
        and record.get("runtime_kg_models_added") is True
        and record.get("runtime_kg_migration_added") is True
        and record.get("idempotent_graph_loader_added") is True
        and record.get("prd2_4_2_6_authorised") is True
        and str(register.get("next_authorised_item", "")).startswith("PRD-2")
    )
    return {"valid": archival_valid, "archival_foundation_record_used": archival_valid}


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    foundation = _run_foundation_verifier()
    route_text = (root / "app/services/runtime_kg/route_integration.py").read_text() if (root / "app/services/runtime_kg/route_integration.py").exists() else ""
    diagnostics_text = (root / "app/api_v2_routers/diagnostics.py").read_text()
    study_text = (root / "app/api_v2_routers/study_plans.py").read_text()
    schemas_text = (root / "app/domain/schemas.py").read_text()
    repo_text = (root / "app/services/runtime_kg/repository.py").read_text()
    flags_text = (root / "app/services/runtime_kg/feature_flags.py").read_text()
    authority_valid = (
        not missing_paths
        and bool(foundation.get("valid"))
        and register.get("next_authorised_item") in {"PRD-2.4-2.6", "PRD-2.7-2.9"}
        and prod_register.get("next_authorised_item") in {"PRD-2.4-2.6", "PRD-2.7-2.9"}
        and "build_runtime_kg_diagnostic_projection" in diagnostics_text
        and "runtime_kg_projection" in schemas_text
        and "build_runtime_kg_study_plan_payload" in study_text
        and "project_and_persist_evidence" in repo_text
        and "record_rollback" in repo_text
        and "fallback_to_legacy" in route_text
        and "enabled: bool = False" in flags_text
        and record.get("runtime_kg_enabled_by_default") is False
        and record.get("routes_modified") is True
        and record.get("prd3_implementation_authorised") is False
    )
    recorded = record.get("runtime_kg_route_projection_behaviour_recorded") is True
    valid = authority_valid and recorded and register.get("next_authorised_item") == "PRD-2.7-2.9"
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-2.4", "PRD-2.5", "PRD-2.6"]),
        "missing_paths": missing_paths,
        "prd2_foundation_valid": bool(foundation.get("valid")),
        "runtime_kg_route_projection_behaviour_recorded": recorded,
        "diagnostic_route_projection_integrated": record.get("diagnostic_route_projection_integrated") is True,
        "lesson_route_context_hook_preserved": record.get("lesson_route_context_hook_preserved") is True,
        "study_plan_route_focus_integrated": record.get("study_plan_route_focus_integrated") is True,
        "rollback_to_legacy_proven": record.get("rollback_to_legacy_proven") is True,
        "runtime_kg_enabled_by_default": record.get("runtime_kg_enabled_by_default"),
        "routes_modified": record.get("routes_modified"),
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "prd2_7_2_9_authorised": record.get("prd2_7_2_9_authorised") is True,
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
