"""Study plan routes for EduBoost V2."""

from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.database import AsyncSessionLocal
from app.core.jobs import enqueue_job
from app.core.security import get_current_user
from app.domain.api_v2_models import JobAcceptedResponse, StudyPlanGenerateRequest
from app.repositories.learner_repository import LearnerRepository
from app.services.audit_service import AuditService
from app.services.study_plan_service_v2 import StudyPlanServiceV2
from app.services.telemetry import TelemetryService

router = APIRouter(prefix="/study-plans", tags=["V2 Study Plans"])


@router.post("/{learner_id}", response_model=JobAcceptedResponse, status_code=202)
@router.post("/generate/{learner_id}", response_model=JobAcceptedResponse, status_code=202)
async def generate_study_plan(
    learner_id: str,
    request: StudyPlanGenerateRequest,
    background_tasks: BackgroundTasks,
    _: dict = Depends(get_current_user),
):
    async def _run() -> dict:
        try:
            from app.repositories.study_plan_repository import StudyPlanRepository
            study_plan_repository = StudyPlanRepository()
        except Exception:  # noqa: BLE001
            study_plan_repository = None

        async with AsyncSessionLocal() as db:
            service = StudyPlanServiceV2(
                learner_repository=LearnerRepository(db),
                study_plan_repository=study_plan_repository,
            )
            plan = await service.generate_plan(learner_id, gap_ratio=request.gap_ratio)
            audit = AuditService(db)
            await audit.log_event(
                event_type="STUDY_PLAN_GENERATED",
                learner_id=learner_id,
                payload={"plan_id": plan["plan_id"]},
            )
            await TelemetryService().track_event_async(
                "study_plan_generated",
                pseudonym_id=f"learner:{learner_id}",
                properties={"gap_ratio": request.gap_ratio},
            )
            return plan

    job = await enqueue_job(
        background_tasks,
        operation="study_plan_generation",
        payload={"learner_id": learner_id, "gap_ratio": request.gap_ratio},
        handler=_run,
    )
    return JobAcceptedResponse(job_id=job["job_id"], operation=job["operation"], status=job["status"])
