"""Comprehensive endpoint unit tests for the Admin Content Factory Router."""
from __future__ import annotations

import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_factory import (
    router,
    get_content_factory_service,
    get_staging_readiness_service,
    get_content_staging_seed_executor,
    get_production_promotion_gate,
    get_production_promotion_executor,
    get_production_read_verification_service,
    get_content_review_queue_service,
    get_content_reviewer_assignment_service,
    get_content_bulk_review_service,
)
from app.api_v2_deps.auth import require_admin, require_auth_context, AuthContext
from app.core.database import get_db


def _create_test_app(
    factory_service: Any | None = None,
    seed_executor: Any | None = None,
    promotion_executor: Any | None = None,
    review_queue_service: Any | None = None,
) -> FastAPI:
    app = FastAPI()
    app.include_router(router)

    async def override_admin():
        return AuthContext(
            user_id=str(uuid.uuid4()),
            role="admin",
            email="admin@eduboost.co.za",
            token_type="access",
            raw_claims={"role": "admin", "permissions": ["admin:all"]},
            jti=str(uuid.uuid4()),
        )

    async def override_db():
        return AsyncMock()

    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[require_auth_context] = override_admin
    app.dependency_overrides[get_db] = override_db

    if factory_service is not None:
        app.dependency_overrides[get_content_factory_service] = lambda: factory_service
    if seed_executor is not None:
        app.dependency_overrides[get_content_staging_seed_executor] = lambda: seed_executor
    if promotion_executor is not None:
        app.dependency_overrides[get_production_promotion_executor] = lambda: promotion_executor
    if review_queue_service is not None:
        app.dependency_overrides[get_content_review_queue_service] = lambda: review_queue_service

    return app


# ---------------------------------------------------------------------------
# Content Factory Health & Scopes Endpoints Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_content_factory_health():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["route_scope"] == "admin"


@pytest.mark.asyncio
async def test_content_factory_etl_status():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/etl/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "available"
        assert "pipeline_package" in data


@pytest.mark.asyncio
async def test_content_factory_list_scopes():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/scopes")
        assert resp.status_code == 200
        scopes = resp.json()
        assert isinstance(scopes, list)
        assert len(scopes) > 0


@pytest.mark.asyncio
async def test_content_factory_get_scope_not_found():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/scopes/non_existent_scope_123")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_get_scope_targets_not_found():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/scopes/non_existent_scope_123/targets")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_scope_coverage_not_found():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/scopes/non_existent_scope_123/coverage")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_validate_artifact_missing_fields():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/admin/content-factory/validate-artifact",
            json={
                "artifact_json": {},
                "caps_ref": "4.M.1.1",
                "sources": [],
                "artifact_type": "lesson_content",
            },
        )
        assert resp.status_code in (200, 422)


# ---------------------------------------------------------------------------
# Artifacts, Staging & Production Endpoints Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_content_factory_get_artifact_not_found():
    mock_service = AsyncMock()
    mock_service.get_artifact.side_effect = LookupError("Artifact not found")
    app = _create_test_app(factory_service=mock_service)
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/admin/content-factory/artifacts/{fake_id}")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_get_artifact_provenance_not_found():
    mock_service = AsyncMock()
    mock_service.get_artifact.side_effect = LookupError("Artifact not found")
    app = _create_test_app(factory_service=mock_service)
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/admin/content-factory/artifacts/{fake_id}/provenance")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_get_review_bundle_not_found():
    mock_rq = AsyncMock()
    mock_rq.get_artifact_review_bundle.side_effect = LookupError("Review bundle not found")
    app = _create_test_app(review_queue_service=mock_rq)
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/admin/content-factory/artifacts/{fake_id}/review-bundle")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_get_seed_run_not_found():
    mock_seed = AsyncMock()
    mock_seed.get_seed_run.side_effect = LookupError("Seed run not found")
    app = _create_test_app(seed_executor=mock_seed)
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/admin/content-factory/seed-runs/{fake_id}")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_get_promotion_event_not_found():
    mock_promo = AsyncMock()
    mock_promo.get_promotion_event.side_effect = LookupError("Promotion event not found")
    app = _create_test_app(promotion_executor=mock_promo)
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/admin/content-factory/promotion-events/{fake_id}")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_runs_endpoints():
    app = _create_test_app()
    fake_run_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Get run not found
        resp = await client.get(f"/admin/content-factory/runs/{fake_run_id}")
        assert resp.status_code in (200, 404)

        # Plan missing tasks
        resp = await client.post(f"/admin/content-factory/runs/{fake_run_id}/plan-missing")
        assert resp.status_code in (200, 404)

        # Execute run
        resp = await client.post(f"/admin/content-factory/runs/{fake_run_id}/execute")
        assert resp.status_code in (200, 404, 409)

        # Cancel run
        resp = await client.post(f"/admin/content-factory/runs/{fake_run_id}/cancel")
        assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_content_factory_tasks_endpoints():
    app = _create_test_app()
    fake_task_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Get task
        resp = await client.get(f"/admin/content-factory/tasks/{fake_task_id}")
        assert resp.status_code in (200, 404)

        # Execute task
        resp = await client.post(f"/admin/content-factory/tasks/{fake_task_id}/execute")
        assert resp.status_code in (200, 404, 409)


@pytest.mark.asyncio
async def test_content_factory_review_actions_endpoints():
    app = _create_test_app()
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Submit review
        resp = await client.post(f"/admin/content-factory/artifacts/{fake_id}/submit-review")
        assert resp.status_code in (200, 404, 409)

        # Bulk approve
        resp = await client.post(
            "/admin/content-factory/review/bulk-approve",
            json={"artifact_ids": [str(fake_id)], "notes": "LGTM"},
        )
        assert resp.status_code in (200, 404, 409)

        # Review queue
        resp = await client.get("/admin/content-factory/review-queue")
        assert resp.status_code in (200, 404)

