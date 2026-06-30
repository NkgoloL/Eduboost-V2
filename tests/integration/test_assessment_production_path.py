"""Integration: assessment list + submit production path (HTTP, mocked persistence)."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api_v2 import app
from app.api_v2_routers import assessments as assessments_router
from app.core.security import get_current_user

pytestmark = pytest.mark.integration

ASSESSMENT_ID = "assessment-math-1"


class _FakeAssessmentService:
    def __init__(self) -> None:
        self.submit_calls: list[dict] = []

    async def list_assessments(self, limit: int = 50, offset: int = 0) -> dict:
        return {"assessments": [{"assessment_id": ASSESSMENT_ID, "title": "Fractions Quiz"}]}

    async def submit_attempt(
        self,
        assessment_id: str,
        learner_id: str,
        responses: list[dict],
        time_taken_seconds: int = 0,
    ) -> dict:
        self.submit_calls.append(
            {
                "assessment_id": assessment_id,
                "learner_id": learner_id,
                "responses": responses,
                "time_taken_seconds": time_taken_seconds,
            }
        )
        return {
            "attempt_id": "attempt-99",
            "assessment_id": assessment_id,
            "learner_id": learner_id,
            "correct_count": len(responses),
            "marks_obtained": len(responses),
            "score": 1.0,
            "total_marks": len(responses),
        }


@pytest.mark.asyncio
async def test_assessment_list_and_submit_happy_path(monkeypatch):
    fake_service = _FakeAssessmentService()
    monkeypatch.setattr(assessments_router, "AssessmentServiceV2", lambda: fake_service)
    monkeypatch.setattr(
        assessments_router,
        "require_active_consent_for_current_user",
        AsyncMock(return_value=None),
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        session_response = await client.post("/api/v2/auth/dev-session")
        assert session_response.status_code == 200
        session = session_response.json()["data"]
        token = session["access_token"]
        learner_id = session["learner"]["learner_id"]
        guardian_id = session.get("guardian_id") or session.get("user", {}).get("id") or "dev-guardian"

        app.dependency_overrides[get_current_user] = lambda: {
            "sub": guardian_id,
            "role": "parent",
            "guardian_learner_ids": [learner_id],
        }
        try:
            auth = {"Authorization": f"Bearer {token}"}

            list_response = await client.get("/api/v2/assessments", headers=auth)
            assert list_response.status_code == 200
            listed = list_response.json()["data"]["assessments"]
            assert listed[0]["assessment_id"] == ASSESSMENT_ID

            submit_response = await client.post(
                f"/api/v2/assessments/{ASSESSMENT_ID}/attempt",
                headers=auth,
                json={
                    "learner_id": learner_id,
                    "responses": [
                        {"item_id": "q1", "selected_option": "A"},
                        {"item_id": "q2", "selected_option": "B"},
                    ],
                    "time_taken_seconds": 120,
                },
            )
            assert submit_response.status_code == 200
            result = submit_response.json()["data"]
            assert result["attempt_id"] == "attempt-99"
            assert result["score"] == 1.0
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    assert len(fake_service.submit_calls) == 1
    assert fake_service.submit_calls[0]["assessment_id"] == ASSESSMENT_ID
    assert fake_service.submit_calls[0]["learner_id"] == learner_id
