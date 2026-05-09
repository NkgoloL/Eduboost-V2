from __future__ import annotations

import pytest

from app.domain.api_v2_models import AssessmentAttemptRequest, AssessmentAttemptResponseItem


@pytest.mark.unit
def test_assessment_attempt_request_accepts_response_items() -> None:
    request = AssessmentAttemptRequest(
        learner_id="learner-1",
        responses=[
            AssessmentAttemptResponseItem(item_id="item-1", selected_option="A"),
            {"item_id": "item-2", "answer": "42"},
        ],
        time_taken_seconds=90,
    )

    assert request.learner_id == "learner-1"
    assert request.responses[0].item_id == "item-1"
    assert request.responses[1].answer == "42"
    assert request.time_taken_seconds == 90


@pytest.mark.unit
def test_assessment_router_uses_shared_attempt_model() -> None:
    from app.api_v2_routers import assessments as assessments_router

    assert assessments_router.AssessmentAttemptRequest is AssessmentAttemptRequest
