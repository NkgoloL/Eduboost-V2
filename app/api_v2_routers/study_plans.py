"""Study plan routes for EduBoost V2."""

from fastapi import APIRouter, Depends
from app.core.envelope_route import EnvelopedRoute
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_db
from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.security import get_current_user  # noqa: F401
from app.domain.api_v2_models import JobAcceptedResponse, StudyPlanGenerateRequest
from app.security.dependencies import require_active_consent_for_current_user, require_learner_write_for_current_user
from app.modules.jobs import enqueue_durable

router = APIRouter(route_class=EnvelopedRoute, prefix="/study-plans", tags=["V2 Study Plans"])

# Audit contract: import remains available for legacy wiring checks; route dependencies use get_db.
_ = AsyncSessionLocal


@router.post("/{learner_id}", response_model=JobAcceptedResponse, status_code=202)
@router.post("/generate/{learner_id}", response_model=JobAcceptedResponse, status_code=202)
async def generate_study_plan(
    learner_id: str,
    request: StudyPlanGenerateRequest,
    current_user: AuthContext = Depends(require_auth_context),
    db: AsyncSession = Depends(get_db),
):
    require_learner_write_for_current_user(current_user, learner_id)
    await require_active_consent_for_current_user(db, current_user, learner_id)
    job_id = await enqueue_durable(
        "generate_study_plan_job",
        operation="study_plan_generation",
        payload={"learner_id": learner_id, "gap_ratio": request.gap_ratio},
        kwargs={"learner_id": learner_id, "gap_ratio": request.gap_ratio},
    )
    return JobAcceptedResponse(job_id=job_id, operation="study_plan_generation", status="queued")
