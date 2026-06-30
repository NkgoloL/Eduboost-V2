"""Auto-apply ``@pytest.mark.governance`` for doc/evidence meta-tests.

Governance tests validate repository documents, CI manifests, and release
artifacts. They are valuable in nightly/release workflows but are excluded
from the PR fast gate (``make test-fast``).
"""
from __future__ import annotations

from pathlib import Path

import pytest

# Filename fragments that indicate governance-style tests.
_GOVERNANCE_MARKERS = (
    "_evidence",
    "evidence_",
    "cluster_",
    "staging_smoke",
    "staging_release",
    "staging_acceptance",
    "production_readiness",
    "release_owner",
    "release_evidence",
    "release_hygiene",
    "release_approval",
    "release_artifact",
    "release_audit",
    "release_candidate",
    "release_change",
    "release_handoff",
    "release_record",
    "release_state",
    "release_go_no_go",
    "beta_release",
    "beta_evidence",
    "beta_blocker",
    "beta_no_go",
    "beta_signoff",
    "sealed_",
    "terminal_evidence",
    "terminal_handoff",
    "terminal_pr_evidence",
    "terminal_review",
    "final_release",
    "final_gate_refresh",
    "final_evidence",
    "final_pr_",
    "final_acceptance",
    "final_archive",
    "final_audit_handoff",
    "final_beta_operator",
    "final_closure",
    "final_merge_signoff",
    "final_project_closeout",
    "final_reviewer",
    "post_closeout",
    "post_beta_evidence",
    "post_merge_evidence",
    "post_deploy_staging",
    "post_terminal",
    "pr_closeout_evidence",
    "pr_merge_evidence",
    "pr_ready_final",
    "project_release_closure",
    "signoff",
    "closeout_packet",
    "handoff_freeze",
    "handoff_closure",
    "todo_implementation_plan",
    "verify_repo_state",
    "roadmap_production_hardening",
    "roadmap_after_production",
    "testing_release_quality",
    "security_posture_threat",
    "transaction_boundary_guardrails",
    "transaction_rollback_rollup",
    "route_tx_",
    "tx_route_",
    "remediation_safety_contract",
    "recommended_operating_model",
    "openapi_ci_contract",
    "architecture_boundary_contract",
    "database_backup_contract",
    "database_restore_command",
    "backup_redis_dr",
    "ci_authority",
    "ci_run_evidence",
    "ci_evidence_acceptance",
    "approval_evidence",
    "runtime_release_evidence_contract",
    "live_db_tx_evidence",
    "auth_refresh_db_evidence",
    "privacy_boundary_evidence",
    "persistence_resilience_evidence",
    "observability_ops_evidence",
    "test_learning_evidence",
    "frontend_evidence_index",
    "data_resilience_evidence",
    "caps_ai_safety_evidence",
    "staging_operations_release",
    "pyproject_release_evidence",
    "pytest_release_evidence",
    "capture_pytest_release",
    "check_pytest_release",
    "generate_release_evidence",
    "generate_database_restore_evidence",
    "generate_database_backup_manifest",
    "sealed_evidence_access",
    "sealed_reviewer_closeout",
    "terminal_evidence_seal",
    "terminal_handoff_closure",
    "merge_control_evidence",
    "warning_cleanup_contract",
)

# Runtime/API contract tests that must stay in the fast gate despite name overlap.
_GOVERNANCE_EXCLUDES = (
    "_router_contract",
    "_repository_contract",
    "_service_full",
    "_services_full",
    "sprint2_",
    "sprint3_",
    "authorization_wiring",
    "consent_gate_wiring",
    "vertical_journey_contract",
    "api_envelope",
    "safety_contract",
    "llm_gateway",
    "etl_pipeline",
    "diagnostic_transactional",
    "content_factory_services",
    "lesson_generator",
    "v2_repositories",
    "popia_router",
    "auth_router",
    "auth_lifecycle",
    "assessment_attempt",
    "api_v2_router_contract",
    "envelope_error_contract",
    "llm_provider_fallback_contract",
    "caps_alignment_contract",
    "mastery_repository_contract",
    "learner_repository_contract",
    "consent_repository_contract",
    "assessment_repository_contract",
    "audit_event_contracts",
    "auth_db_lifecycle_proof_contracts",
    "popia_lifecycle_response_contracts",
    "runtime_integration_proof_contracts",
)


def is_governance_test_path(path: str | Path) -> bool:
    name = Path(path).name
    if any(token in name for token in _GOVERNANCE_EXCLUDES):
        return False
    return any(token in name for token in _GOVERNANCE_MARKERS)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        if "governance" in item.keywords:
            continue
        if is_governance_test_path(item.path):
            item.add_marker(pytest.mark.governance)
