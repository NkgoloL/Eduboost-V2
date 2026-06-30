"""Contract tests for assessments router route delegation."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api_v2_routers import assessments
from app.core.security import get_current_user


LEARNER_ID = str(uuid.uuid4())
ACTOR = {"sub": "guardian-1", "role": "parent", "guardian_learner_ids": [LEARNER_ID]}


@dataclass
class FakeAssessmentService:
    list_calls: list[dict[str, Any]] = field(default_factory=list)
    submit_calls: list[dict[str, Any]] = field(default_factory=list)

    async def list_assessments(self, limit: int = 50, offset: int = 0) -> dict:
        self.list_calls.append({"limit": limit, "offset": offset})
        return {"assessments": [{"assessment_id": "a1", "title": "Math Quiz"}]}

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
            "attempt_id": "attempt-1",
            "assessment_id": assessment_id,
            "learner_id": learner_id,
            "score": 1.0,
        }


def _client(service: FakeAssessmentService) -> TestClient:
    app = FastAPI()
    app.include_router(assessments.router, prefix="/api/v2")
    app.dependency_overrides[get_current_user] = lambda: ACTOR

    async def _allow_consent(*_args, **_kwargs):
        return None

    assessments.require_active_consent_for_current_user = _allow_consent  # type: ignore[method-assign]
    assessments.AssessmentServiceV2 = lambda: service  # type: ignore[misc,assignment]
    return TestClient(app, raise_server_exceptions=True)


def _unwrap(payload: dict[str, Any]) -> Any:
    return payload.get("data", payload)


@pytest.mark.unit
def test_list_assessments_delegates_to_service():
    service = FakeAssessmentService()
    client = _client(service)

    response = client.get("/api/v2/assessments?limit=10&offset=5")
    assert response.status_code == 200
    body = _unwrap(response.json())
    assert body["assessments"][0]["assessment_id"] == "a1"
    assert service.list_calls == [{"limit": 10, "offset": 5}]


@pytest.mark.unit
def test_submit_attempt_delegates_with_authz_and_consent(monkeypatch: pytest.MonkeyPatch):
    service = FakeAssessmentService()
    consent = AsyncMock(return_value=None)
    monkeypatch.setattr(assessments, "require_active_consent_for_current_user", consent)
    monkeypatch.setattr(assessments, "AssessmentServiceV2", lambda: service)

    app = FastAPI()
    app.include_router(assessments.router, prefix="/api/v2")
    app.dependency_overrides[get_current_user] = lambda: ACTOR
    client = TestClient(app, raise_server_exceptions=True)

    response = client.post(
        "/api/v2/assessments/quiz-1/attempt",
        json={
            "learner_id": LEARNER_ID,
            "responses": [{"item_id": "q1", "selected_option": "A"}],
            "time_taken_seconds": 90,
        },
    )
    assert response.status_code == 200
    body = _unwrap(response.json())
    assert body["attempt_id"] == "attempt-1"
    assert service.submit_calls[0]["assessment_id"] == "quiz-1"
    assert service.submit_calls[0]["learner_id"] == LEARNER_ID
    consent.assert_awaited_once()
