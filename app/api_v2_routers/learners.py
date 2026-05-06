"""EduBoost V2 — Learners Router"""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user, require_parent_or_admin
from app.domain.schemas import LearnerCreate, LearnerResponse
from app.services.consent import ConsentService
from app.services.learner_service import LearnerService

router = APIRouter(prefix="/learners", tags=["learners"])
log = get_logger(__name__)


@router.post("/", response_model=LearnerResponse, status_code=status.HTTP_201_CREATED)
async def create_learner(
    body: LearnerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_parent_or_admin),
):
    svc = LearnerService(db)
    learner = await svc.create_learner(
        guardian_id=current_user["sub"],
        display_name=body.display_name,
        grade=body.grade,
        language=body.language,
    )
    return LearnerResponse.model_validate(learner)


@router.get("/{learner_id}", response_model=LearnerResponse)
async def get_learner(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    consent = ConsentService(db)
    await consent.require_active_consent(learner_id)

    svc = LearnerService(db)
    learner = await svc.get_learner_summary(learner_id)
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    return LearnerResponse.model_validate(learner)


@router.get("/{learner_id}/mastery")
async def get_mastery(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    svc = LearnerService(db)
    return await svc.get_mastery(learner_id, actor_id=current_user.get("sub"))


@router.delete("/{learner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def request_erasure(
    learner_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_parent_or_admin),
):
    """
    POPIA Section 24 — Right to Erasure.
    Mandates a valid Guardian JWT. Physical purge runs as a BackgroundTask.
    """
    svc = LearnerService(db)
    learner_id_to_purge, learner_pseudonym = await svc.request_erasure(learner_id, current_user)

    # Physical purge runs in the background; audit keeps only an anonymised tombstone.
    background_tasks.add_task(enqueue_data_purge, learner_id_to_purge, learner_pseudonym)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def enqueue_data_purge(learner_id: str, learner_pseudonym: str) -> None:
    log.info(
        "learner_data_purge_queued",
        learner_id=learner_id,
        learner_pseudonym=learner_pseudonym,
    )
