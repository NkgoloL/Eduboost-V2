import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.jobs import router
from app.api_v2_deps.auth import require_auth_context


@pytest.mark.asyncio
async def test_jobs_status_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "job-requester"
    app.dependency_overrides[require_auth_context] = lambda: auth_ctx

    with patch("app.api_v2_routers.jobs.get_job") as mock_get_job:
        # Test 404
        mock_get_job.return_value = None
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp_404 = await client.get("/jobs/job-nonexistent")
            assert resp_404.status_code == 404
            assert "Job not found" in resp_404.json()["detail"]

        # Test success
        mock_get_job.return_value = {
            "job_id": "job-123",
            "operation": "content_generation",
            "status": "completed",
            "payload": {},
            "result": {"count": 42},
            "error": None,
            "created_at": "2026-08-29T10:00:00Z",
            "updated_at": "2026-08-29T10:05:00Z",
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp_200 = await client.get("/jobs/job-123")
            assert resp_200.status_code == 200
            data = resp_200.json()
            payload = data.get("data") if "data" in data else data
            assert payload["job_id"] == "job-123"
            assert payload["operation"] == "content_generation"
            assert payload["status"] == "completed"
