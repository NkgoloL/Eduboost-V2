import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_factory import (
    router,
    get_content_review_queue_service,
    get_content_reviewer_assignment_service,
)
from app.api_v2_deps.auth import require_admin, require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_content_factory_review_queue_and_workload():
    app = FastAPI()
    app.include_router(router)

    mock_queue_service = AsyncMock()
    mock_queue_page = MagicMock()
    mock_queue_page.items = []
    mock_queue_page.total = 0
    mock_queue_page.limit = 50
    mock_queue_page.offset = 0
    mock_queue_service.list_queue.return_value = mock_queue_page

    mock_assignment_service = AsyncMock()
    mock_workload = MagicMock()
    mock_workload.reviewer_id = "rev-1"
    mock_workload.assigned = 2
    mock_workload.in_review = 1
    mock_workload.overdue = 0
    mock_workload.total_open = 3
    mock_assignment_service.get_reviewer_workload.return_value = mock_workload

    app.dependency_overrides[require_admin] = lambda: {"role": "admin"}
    app.dependency_overrides[get_content_review_queue_service] = lambda: mock_queue_service
    app.dependency_overrides[get_content_reviewer_assignment_service] = lambda: mock_assignment_service
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_q = await client.get("/admin/content-factory/review-queue")
        assert resp_q.status_code == 200
        assert resp_q.json()["total"] == 0

        resp_w = await client.get("/admin/content-factory/reviewers/rev-1/workload")
        assert resp_w.status_code == 200
        assert resp_w.json()["reviewer_id"] == "rev-1"
