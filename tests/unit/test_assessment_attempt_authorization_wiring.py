"""Tests for assessment attempt authorization wiring."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import HTTPException

from app.api_v2_routers import assessments as assessments_router

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_assessment_attempt_uses_phase2_write_authorization() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "assessments.py").read_text(encoding="utf-8")
    block = source.split("async def submit_attempt", maxsplit=1)[1]
    assert "current_user: dict = Depends(get_current_user)" in block
    assert "require_learner_write_for_current_user(current_user, request.learner_id)" in block
    assert block.index("require_learner_write_for_current_user") < block.index("return await AssessmentServiceV2()")


class FakeResponse:
    def model_dump(self) -> dict[str, Any]:
        return {"item_id": "item-1", "selected_option": "A"}


class FakeAssessmentService:
    async def submit_attempt(self, assessment_id: str, learner_id: str, responses: list[dict], time_taken_seconds: int):
        return {
            "assessment_id": assessment_id,
            "learner_id": learner_id,
            "responses": responses,
            "time_taken_seconds": time_taken_seconds,
        }


@pytest.mark.asyncio
@pytest.mark.unit
async def test_assessment_attempt_allows_authorized_guardian(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(assessments_router, "AssessmentServiceV2", FakeAssessmentService)

    request = SimpleNamespace(
        learner_id="learner-1",
        responses=[FakeResponse()],
        time_taken_seconds=120,
    )

    result = await assessments_router.submit_attempt(
        "assessment-1",
        request,
        current_user={"sub": "guardian-1", "role": "parent", "guardian_learner_ids": ["learner-1"]},
    )

    assert result["learner_id"] == "learner-1"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_assessment_attempt_rejects_unrelated_guardian(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(assessments_router, "AssessmentServiceV2", FakeAssessmentService)

    request = SimpleNamespace(
        learner_id="learner-1",
        responses=[FakeResponse()],
        time_taken_seconds=120,
    )

    with pytest.raises(HTTPException) as exc_info:
        await assessments_router.submit_attempt(
            "assessment-1",
            request,
            current_user={"sub": "guardian-2", "role": "parent", "guardian_learner_ids": ["learner-2"]},
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == "object_forbidden"


@pytest.mark.unit
def test_assessment_router_has_fallback_attempt_model() -> None:
    assert hasattr(assessments_router, "AssessmentAttemptRequest")
    model = assessments_router.AssessmentAttemptRequest(
        learner_id="learner-1",
        responses=[{"item_id": "item-1", "selected_option": "A"}],
        time_taken_seconds=30,
    )
    assert model.learner_id == "learner-1"
    assert model.responses[0].model_dump()["item_id"] == "item-1"
