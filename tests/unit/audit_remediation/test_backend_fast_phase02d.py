from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def read(path: str) -> str:
    target = ROOT / path
    if not target.exists() and path.startswith(".github/workflows/"):
        archived = ROOT / "archive/github_workflows" / Path(path).name
        if archived.exists():
            target = archived
    return target.read_text(encoding="utf-8")


def test_staging_readiness_defaults_all_scope_verification_to_active_scopes() -> None:
    source = read("app/services/content_staging_readiness.py")
    assert "include_review_scopes: bool = False" in source
    assert "self.scope_registry.list_active_scopes()" in source


def test_review_scope_staging_seed_requires_explicit_opt_in() -> None:
    source = read("scripts/curriculum/seed_staging_review_scopes.py")
    assert "--include-all-review-scopes" in source
    assert "registry.list_active_scopes()" in source
    assert "include_all_review_scopes" in source


def test_mcp_dependency_is_declared_and_required() -> None:
    for path in [
        "requirements/base.in",
        "requirements/base.txt",
        "requirements/dev.in",
        "requirements/dev.txt",
        "requirements.txt",
        "requirements-dev.txt",
    ]:
        assert "mcp[cli]" in read(path)
    assert '"mcp": "mcp[cli]"' in read("scripts/audit_remediation/verify_backend_fast_runtime_dependencies.py")


def test_auth_refresh_workflow_uses_upload_artifact_v4() -> None:
    source = read(".github/workflows/auth-refresh-db-proof.yml")
    assert "actions/upload-artifact@v4" in source


def test_content_factory_schema_contract_declares_existing_orm_extensions() -> None:
    source = read("scripts/ci/content_factory_schema_contract.py")
    for value in ["revision_required", "published", "superseded"]:
        assert f'"{value}"' in source
    for name in ["ContentAnswerKeyVerification", "ContentReviewDecision", "ContentStateTransitionEvent"]:
        assert name in source
    for table in ["content_answer_key_verifications", "content_review_decisions", "content_state_transition_events"]:
        assert table in source


def test_phase02d_verifier_script_exists() -> None:
    source = read("scripts/audit_remediation/verify_backend_fast_phase02d.py")
    assert "backend-fast-staging-contracts" in source
    assert "mcp_dependency_declared" in source
