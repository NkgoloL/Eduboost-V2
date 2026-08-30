import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.lessons import router, get_lesson_service
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db
from app.domain.schemas import LessonResponse


@pytest.mark.asyncio
async def test_lessons_get_and_sync_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    auth_ctx.roles = ["parent"]

    session = AsyncMock()
    mock_service = MagicMock()
    mock_service.complete_lesson = AsyncMock()
    mock_service.record_feedback = AsyncMock()
    mock_service.get_lesson_by_id = AsyncMock(
        return_value={
            "id": "lsn-1",
            "grade": 4,
            "subject": "Mathematics",
            "topic": "Addition",
            "language": "en",
            "content": "Lesson content text here",
            "archetype": "visual",
            "served_from_cache": True,
            "cache_hit": True,
            "caps_aligned": True,
            "created_at": "2026-08-29T10:00:00Z",
        }
    )

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_lesson_service] = lambda: mock_service

    with patch("app.api_v2_routers.lessons.require_lesson_read_access_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.lessons.require_lesson_write_access_for_current_user", new=AsyncMock()):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Get lesson by id
            resp_get = await client.get("/lessons/lsn-1")
            assert resp_get.status_code == 200
            data_get = resp_get.json()
            payload_get = data_get.get("data") if "data" in data_get else data_get
            assert payload_get["id"] == "lsn-1"
            assert payload_get["subject"] == "Mathematics"

            # 2. Sync lessons complete and feedback
            resp_sync = await client.post(
                "/lessons/sync",
                json={
                    "responses": [
                        {"lesson_id": "lsn-1", "event_type": "complete"},
                        {"lesson_id": "lsn-2", "event_type": "feedback", "score": 5},
                    ]
                },
            )
            assert resp_sync.status_code == 200
            data_sync = resp_sync.json()
            payload_sync = data_sync.get("data") if "data" in data_sync else data_sync
            assert payload_sync["processed"] == 2
