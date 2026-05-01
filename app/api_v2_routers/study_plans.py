"""Study plan routes for EduBoost V2."""

from fastapi import APIRouter, BackgroundTasks

from app.domain.api_v2_models import StudyPlanGenerateRequest
from app.services.audit_service import AuditService
from app.services.study_plan_service_v2 import StudyPlanServiceV2

router = APIRouter(prefix="/api/v2/study-plans", tags=["V2 Study Plans"])


@router.post("/{learner_id}")
async def generate_study_plan(learner_id: str, request: StudyPlanGenerateRequest, background_tasks: BackgroundTasks):
    plan = await StudyPlanServiceV2().generate_plan(learner_id, gap_ratio=request.gap_ratio)
    background_tasks.add_task(
        AuditService().log_event,
        event_type="STUDY_PLAN_GENERATED",
        learner_id=learner_id,
        payload={"plan_id": plan["plan_id"]},
    )
    return plan
