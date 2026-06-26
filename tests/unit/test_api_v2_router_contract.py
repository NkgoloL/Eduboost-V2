from __future__ import annotations

import pytest

from app.api_v2 import API_PREFIXES, ROUTER_REGISTRY, app


@pytest.mark.unit
def test_router_registry_has_unique_names() -> None:
    names = [name for name, _router in ROUTER_REGISTRY]

    assert len(names) == len(set(names))
    assert "system" in names
    assert "diagnostics" in names
    assert "popia" in names


@pytest.mark.unit
def test_registered_router_fragments_are_exposed_under_each_v2_prefix() -> None:
    route_paths = {route.path for route in app.routes}
    expected_fragments = {
        "assessments": "/assessments",
        "auth": "/auth",
        "auth_extended": "/auth",
        "learners": "/learners",
        "lessons": "/lessons",
        "study_plans": "/study-plans",
        "diagnostics": "/diagnostics",
        "practice": "/practice",
        "gamification": "/gamification",
        "onboarding": "/onboarding",
        "parents": "/parents",
        "billing": "/billing",
        "consent": "/consent",
        "consent_renewal": "/consent",
        "content_factory": "/admin/content-factory",
        "admin_etl": "/admin/etl",
        "audit": "/audit",
        "popia": "/popia",
        "jobs": "/jobs",
        "system": "/system",
        "learner_content": "/learner/content",
        "curriculum_expansion": "/admin/curriculum-expansion",
        "ai_operations": "/admin/ai-operations",
        "generation": "/admin/generation",
        "content_review": "/content-review",
        "irt_quality": "/admin/irt-quality",
    }

    missing: list[str] = []
    for prefix in API_PREFIXES:
        for router_name, _router in ROUTER_REGISTRY:
            fragment = expected_fragments[router_name]
            expected_prefix = f"{prefix}{fragment}"
            if not any(path == expected_prefix or path.startswith(f"{expected_prefix}/") for path in route_paths):
                missing.append(f"{router_name}:{expected_prefix}")

    assert missing == []


@pytest.mark.unit
def test_legacy_prefixes_are_not_exposed_by_canonical_runtime() -> None:
    forbidden_prefixes = ("/api/v1", "/v1", "/api/legacy", "/legacy")
    route_paths = {route.path for route in app.routes}

    assert [
        path for path in route_paths if path.startswith(forbidden_prefixes)
    ] == []


@pytest.mark.unit
def test_content_factory_scope_openapi_contract_is_admin_only() -> None:
    schema = app.openapi()

    operations = schema["paths"]["/api/v2/admin/content-factory/scopes"]
    assert set(operations) == {"get"}
    assert operations["get"]["tags"] == ["admin-content-factory"]
    assert "/api/v2/admin/content-factory/scopes/{scope_id}/targets" in schema["paths"]
    assert "/api/v2/admin/content-factory/scopes/{scope_id}/coverage" in schema["paths"]
    assert "/api/v2/admin/content-factory/scopes/{scope_id}/coverage/{caps_ref}" in schema["paths"]
    assert (
        schema["paths"]["/api/v2/admin/content-factory/scopes/{scope_id}/coverage"]["get"]["tags"]
        == ["admin-content-factory"]
    )
    assert "/api/v2/admin/content-factory/runs" in schema["paths"]
    assert "/api/v2/admin/content-factory/artifacts/{artifact_id}/provenance" in schema["paths"]
    assert "/api/v2/admin/content-factory/review-queue" in schema["paths"]
    assert "/api/v2/admin/content-factory/scopes/{scope_id}/seed-staging" in schema["paths"]
    staging_paths = {
        "/api/v2/admin/content-factory/staging-verification/all-scopes",
        "/api/v2/admin/content-factory/staging-verification/runs",
        "/api/v2/admin/content-factory/staging-verification/runs/{run_id}",
        "/api/v2/admin/content-factory/scopes/{scope_id}/staging-verification",
        "/api/v2/admin/content-factory/scopes/{scope_id}/staging-readiness",
    }
    assert staging_paths <= set(schema["paths"])
    assert all(schema["paths"][path][next(iter(schema["paths"][path]))]["tags"] == ["admin-content-factory"] for path in staging_paths)
    assert not any(path.startswith("/api/v2/content-factory") and "staging" in path for path in schema["paths"])
    generation_paths = {
        "/api/v2/admin/content-factory/runs/{run_id}/plan-missing",
        "/api/v2/admin/content-factory/runs/{run_id}/execute",
        "/api/v2/admin/content-factory/tasks/{task_id}/execute",
        "/api/v2/admin/content-factory/tasks/{task_id}",
        "/api/v2/admin/content-factory/runs/{run_id}/execution-report",
    }
    assert generation_paths <= set(schema["paths"])
    assert all(schema["paths"][path][next(iter(schema["paths"][path]))]["tags"] == ["admin-content-factory"] for path in generation_paths)
    assert not any(path.startswith("/api/v2/content-factory") and "generation" in path for path in schema["paths"])
    review_paths = {
        "/api/v2/admin/content-factory/review-queue",
        "/api/v2/admin/content-factory/review-summary",
        "/api/v2/admin/content-factory/artifacts/{artifact_id}/review-bundle",
        "/api/v2/admin/content-factory/review-assignments",
        "/api/v2/admin/content-factory/review-assignments/bulk",
        "/api/v2/admin/content-factory/reviewers/{reviewer_id}/workload",
        "/api/v2/admin/content-factory/review/bulk-approve",
        "/api/v2/admin/content-factory/review/bulk-reject",
        "/api/v2/admin/content-factory/review/bulk-quarantine",
    }
    assert review_paths <= set(schema["paths"])
    assert all(schema["paths"][path][next(iter(schema["paths"][path]))]["tags"] == ["admin-content-factory"] for path in review_paths)
    assert not any(path.startswith("/api/v2/content-factory") and "review" in path for path in schema["paths"])
    production_promotion_paths = {
        "/api/v2/admin/content-factory/scopes/{scope_id}/production-gate",
        "/api/v2/admin/content-factory/scopes/{scope_id}/dry-run-promotion",
        "/api/v2/admin/content-factory/scopes/{scope_id}/promote-production",
        "/api/v2/admin/content-factory/promotion-events",
        "/api/v2/admin/content-factory/promotion-events/{promotion_event_id}",
        "/api/v2/admin/content-factory/promotion-events/{promotion_event_id}/items",
        "/api/v2/admin/content-factory/promotion-events/{promotion_event_id}/verify",
        "/api/v2/admin/content-factory/promotion-events/{promotion_event_id}/rollback",
        "/api/v2/admin/content-factory/scopes/{scope_id}/production-read-verification",
    }
    assert production_promotion_paths <= set(schema["paths"])
    assert all(schema["paths"][path][next(iter(schema["paths"][path]))]["tags"] == ["admin-content-factory"] for path in production_promotion_paths)
    assert not any(path.startswith("/api/v2/content-factory") and "promotion" in path for path in schema["paths"])
    learner_content_paths = {
        "/api/v2/learner/content/scopes/{scope_id}/summary",
        "/api/v2/learner/content/scopes/{scope_id}/diagnostic-items",
        "/api/v2/learner/content/scopes/{scope_id}/lessons",
        "/api/v2/learner/content/scopes/{scope_id}/caps/{caps_ref}/diagnostic-items",
        "/api/v2/learner/content/scopes/{scope_id}/caps/{caps_ref}/lessons",
    }
    assert learner_content_paths <= set(schema["paths"])
    assert all(schema["paths"][path][next(iter(schema["paths"][path]))]["tags"] == ["learner-content"] for path in learner_content_paths)
    assert not any(path.startswith("/api/v2/admin") and "learner-content" in path for path in schema["paths"])
    staging_preview_paths = {
        "/api/v2/admin/content-factory/staging-preview/scopes/{scope_id}",
        "/api/v2/admin/content-factory/staging-preview/scopes/{scope_id}/caps/{caps_ref}",
    }
    assert staging_preview_paths <= set(schema["paths"])
    assert all(schema["paths"][path][next(iter(schema["paths"][path]))]["tags"] == ["admin-content-factory"] for path in staging_preview_paths)
    assert all(path.startswith("/api/v2/admin/content-factory") for path in staging_preview_paths)
    production_preview_paths = {
        "/api/v2/admin/content-factory/production-preview/scopes/{scope_id}",
        "/api/v2/admin/content-factory/production-preview/scopes/{scope_id}/caps/{caps_ref}",
    }
    assert production_preview_paths <= set(schema["paths"])
    assert all(schema["paths"][path][next(iter(schema["paths"][path]))]["tags"] == ["admin-content-factory"] for path in production_preview_paths)
    assert all(path.startswith("/api/v2/admin/content-factory") for path in production_preview_paths)
    full_generation_paths = {
        "/api/v2/admin/content-factory/full-generation/plan",
        "/api/v2/admin/content-factory/full-generation/start",
        "/api/v2/admin/content-factory/full-generation/runs",
        "/api/v2/admin/content-factory/full-generation/runs/{run_id}",
        "/api/v2/admin/content-factory/full-generation/runs/{run_id}/report",
        "/api/v2/admin/content-factory/full-generation/runs/{run_id}/cancel",
        "/api/v2/admin/content-factory/full-generation/runs/{run_id}/resume",
    }
    assert full_generation_paths <= set(schema["paths"])
    assert all(schema["paths"][path][next(iter(schema["paths"][path]))]["tags"] == ["admin-content-factory"] for path in full_generation_paths)
    assert all(path.startswith("/api/v2/admin/content-factory") for path in full_generation_paths)
    assert "/api/v2/admin/etl/status" in schema["paths"]
    assert schema["paths"]["/api/v2/admin/etl/status"]["get"]["tags"] == ["admin-etl"]
    assert "/api/v2/content-factory/scopes" not in schema["paths"]
