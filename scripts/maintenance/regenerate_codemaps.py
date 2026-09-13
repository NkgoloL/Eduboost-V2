"""Regenerate the codemap ownership manifest from the current repository inventory."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.maintenance.verify_codemaps import rebuild_inventory

ROOT = Path(__file__).resolve().parents[2]
CODEMAP_DIR = ROOT / "docs/codemaps"
MANIFEST = CODEMAP_DIR / "codemap_coverage_manifest.json"


def owner_for(path: str, codemap_ids: set[str]) -> str:
    """Choose a deterministic primary codemap owner for a newly observed path."""
    if path.startswith("docs/codemaps/"):
        return "19_documentation_adrs_repository_governance_and_maintenance"
    if path.startswith(".github/workflows/") or path.startswith("tests/") or path.startswith("app/frontend/"):
        return "17_testing_ci_coverage_security_and_quality_gates"
    if path.startswith("scripts/production_readiness/") or path.startswith("scripts/roadmap_reconciliation/"):
        return "18_production_readiness_release_evidence_and_live_traffic"
    if path.startswith("scripts/maintenance/") or path.startswith("docs/documentation/"):
        return "19_documentation_adrs_repository_governance_and_maintenance"
    if path.startswith("docs/roadmap/production_readiness/") or path.startswith("docs/release-evidence/"):
        return "18_production_readiness_release_evidence_and_live_traffic"
    if path.startswith("docs/testing/") or path.startswith("docs/ci/"):
        return "17_testing_ci_coverage_security_and_quality_gates"
    if path.startswith("docs/security/") or path.startswith("app/security/"):
        return "03_authentication_authorization_and_session_security"
    if path.startswith("docs/architecture/") or path.startswith("docs/adr/"):
        return "19_documentation_adrs_repository_governance_and_maintenance"
    if path.startswith("docs/frontend/"):
        return "01_frontend_nextjs_pwa_and_client_flows"
    if path.startswith("docs/api/") or path in {"docs/openapi.json", "docs/openapi.yaml", "docs/route_inventory.md"}:
        return "02_api_routing_contracts_and_openapi"
    if path.startswith("docs/compliance/") or path.startswith("docs/popia/") or path.startswith("docs/privacy/"):
        return "04_consent_popia_audit_and_data_subject_rights"
    if path.startswith("docs/deployment/") or path.startswith("docs/operations/") or path.startswith("docs/disaster_recovery/"):
        return "15_infrastructure_deployment_backup_and_disaster_recovery"
    if path.startswith("docs/ai/") or path.startswith("docs/safety/"):
        return "12_llm_gateway_ai_operations_and_safety"
    if path.startswith("docs/curriculum/") or path.startswith("docs/caps/"):
        return "08_curriculum_caps_knowledge_graph_and_runtime_kg"
    if path.startswith("docs/diagnostics/") or path.startswith("docs/irt/") or path.startswith("docs/learning_science/"):
        return "06_diagnostics_irt_item_bank_and_mastery"
    if path.startswith("docs/product/") or path.startswith("docs/beta/"):
        return "05_learner_parent_onboarding_and_vertical_journeys"
    if path.startswith("app/api_v2_routers/") or path.startswith("app/api_v2_deps/"):
        return "02_api_routing_contracts_and_openapi"
    if path.startswith("app/modules/controlled_beta/") or path.startswith("app/modules/production_release/"):
        return "18_production_readiness_release_evidence_and_live_traffic"
    if path.startswith("app/modules/"):
        return "07_lessons_tutor_study_plans_practice_and_gamification"
    if path.startswith("app/services/etl/") or path.startswith("app/services/semantic_retrieval/") or path.startswith("tools/etl/"):
        return "16_etl_ingestion_semantic_retrieval_and_mcp_tools"
    if path.startswith("app/services/curriculum/") or path.startswith("app/domain/knowledge_graph"):
        return "08_curriculum_caps_knowledge_graph_and_runtime_kg"
    if path.startswith("app/services/content_") or path.startswith("app/api_v2_routers/content_"):
        return "09_content_factory_review_quality_and_promotion"
    if path.startswith("app/services/llm") or path.startswith("app/services/ai_"):
        return "12_llm_gateway_ai_operations_and_safety"
    if path.startswith("app/services/consent") or path.startswith("app/services/data_subject") or path.startswith("app/services/audit"):
        return "04_consent_popia_audit_and_data_subject_rights"
    if path.startswith("app/services/diagnostic") or path.startswith("app/modules/diagnostics"):
        return "06_diagnostics_irt_item_bank_and_mastery"
    if path.startswith("app/services/learner") or path.startswith("app/services/parent") or path.startswith("app/modules/vertical"):
        return "05_learner_parent_onboarding_and_vertical_journeys"
    if path.startswith("app/services") or path.startswith("app/core") or path.startswith("app/middleware"):
        return "00_application_bootstrap_and_request_lifecycle"
    if path.startswith("app/repositories") or path.startswith("app/models") or path.startswith("alembic") or path.startswith("supabase"):
        return "10_persistence_repositories_models_migrations_and_transactions"
    if path.startswith("docker") or path.startswith("deployment") or path.startswith("k8s") or path.startswith("nginx"):
        return "15_infrastructure_deployment_backup_and_disaster_recovery"
    return "19_documentation_adrs_repository_governance_and_maintenance"


def main() -> int:
    manifest: dict[str, Any] = json.loads(MANIFEST.read_text(encoding="utf-8"))
    policy = manifest["inventory_policy"]
    inventory = rebuild_inventory(ROOT, CODEMAP_DIR, policy)
    codemaps = manifest["codemaps"]
    codemap_ids = {item["id"] for item in codemaps}
    existing = {item["path"]: item["primary_owner"] for item in manifest.get("assignments", [])}
    assignments = [{"path": path, "primary_owner": existing.get(path, owner_for(path, codemap_ids)), "kind": next((item["kind"] for item in manifest["assignments"] if item["path"] == path), "maintained-file")} for path in sorted(inventory)]
    counts = Counter(item["primary_owner"] for item in assignments)
    manifest["assignments"] = assignments
    for item in codemaps:
        item["assigned_file_count"] = counts[item["id"]]
    manifest["generated_at"] = "2026-09-13"
    manifest["summary"] = {
        "canonical_codemaps": len(codemaps),
        "execution_traces": sum((CODEMAP_DIR / Path(item["path"]).name).read_text(encoding="utf-8").count("## Trace ID:") for item in codemaps),
        "source_anchors": sum(len((CODEMAP_DIR / Path(item["path"]).name).read_text(encoding="utf-8").split("**Path:LineNumber:**")) - 1 for item in codemaps),
        "inventoried_files": len(assignments),
        "assigned_files": len(assignments),
        "unassigned_files": 0,
        "duplicate_primary_assignments": 0,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
