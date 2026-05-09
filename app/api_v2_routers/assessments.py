"""Assessment routes for EduBoost V2."""

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
try:
    from app.domain.api_v2_models import AssessmentAttemptRequest
except ImportError:  # compatibility until shared model is restored
    from typing import Any

    from pydantic import BaseModel, Field

    class AssessmentAttemptResponseItem(BaseModel):
        item_id: str
        selected_option: str | None = None
        answer: str | None = None
        metadata: dict[str, Any] = Field(default_factory=dict)

    class AssessmentAttemptRequest(BaseModel):
        learner_id: str
        responses: list[AssessmentAttemptResponseItem] = Field(default_factory=list)
        time_taken_seconds: int = Field(default=0, ge=0)
from app.services.assessment_service_v2 import AssessmentServiceV2
from app.security.dependencies import require_learner_write_for_current_user

router = APIRouter(prefix="/api/v2/assessments", tags=["V2 Assessments"])


@router.get("")
async def list_assessments(limit: int = 50, offset: int = 0):
    return await AssessmentServiceV2().list_assessments(limit=limit, offset=offset)


@router.post("/{assessment_id}/attempt")
async def submit_attempt(
    assessment_id: str,
    request: AssessmentAttemptRequest,
    current_user: dict = Depends(get_current_user),
):
    require_learner_write_for_current_user(current_user, request.learner_id)
    return await AssessmentServiceV2().submit_attempt(
        assessment_id=assessment_id,
        learner_id=request.learner_id,
        responses=[item.model_dump() for item in request.responses],
        time_taken_seconds=request.time_taken_seconds,
    )
