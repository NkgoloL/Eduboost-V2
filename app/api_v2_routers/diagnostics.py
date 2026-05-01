"""Diagnostic routes for EduBoost V2."""

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.domain.api_v2_models import DiagnosticRunRequest
from app.services.audit_service import AuditService
from app.services.diagnostic_service_v2 import DiagnosticServiceV2
from app.services.quota_service import QuotaExceededError

router = APIRouter(prefix="/api/v2/diagnostics", tags=["V2 Diagnostics"])


@router.post("/{learner_id}")
async def run_diagnostic(learner_id: str, request: DiagnosticRunRequest, background_tasks: BackgroundTasks):
    try:
        result = await DiagnosticServiceV2().run_diagnostic(
            learner_id=learner_id,
            subject_code=request.subject_code,
            max_questions=request.max_questions,
        )
    except QuotaExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    background_tasks.add_task(
        AuditService().log_event,
        event_type="DIAGNOSTIC_COMPLETED",
        learner_id=learner_id,
        payload={"subject_code": request.subject_code},
    )
    return result
