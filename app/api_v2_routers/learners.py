"""EduBoost V2 — Learners Router"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.envelope_route import EnvelopedRoute
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.api_v2_deps.auth import AuthContext, require_auth_context, require_parent_or_admin
from app.core.security import get_current_user  # noqa: F401
from app.domain.schemas import LearnerCreate, LearnerResponse
from app.services.learner_service import LearnerService
from app.security.dependencies import require_active_consent_for_current_user, require_learner_read_for_current_user
from app.services.popia_service import POPIADataRightsService

router = APIRouter(route_class=EnvelopedRoute, prefix="/learners", tags=["learners"])
log = get_logger(__name__)


@router.post("/", response_model=LearnerResponse, status_code=status.HTTP_201_CREATED)
async def create_learner(
    body: LearnerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_parent_or_admin),
):
    svc = LearnerService(db)
    learner = await svc.create_learner(
        guardian_id=current_user.user_id,
        display_name=body.display_name,
        grade=body.grade,
        language=body.language,
    )
    return LearnerResponse.model_validate(learner)


@router.get("/{learner_id}", response_model=LearnerResponse)
async def get_learner(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
):
    svc = LearnerService(db)
    learner = await svc.get_learner_summary(learner_id)
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_read_for_current_user(current_user, learner)
    await require_active_consent_for_current_user(db, current_user, learner_id)
    return LearnerResponse.model_validate(learner)


@router.get("/{learner_id}/mastery")
async def get_mastery(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
):
    svc = LearnerService(db)
    learner = await svc.get_learner_summary(learner_id)
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_read_for_current_user(current_user, learner)
    await require_active_consent_for_current_user(db, current_user, learner_id)

    return await svc.get_mastery(learner_id, actor_id=current_user.user_id)


@router.get("/{learner_id}/mastery/summary")
async def get_mastery_summary(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
):
    svc = LearnerService(db)
    learner = await svc.get_learner_summary(learner_id)
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_read_for_current_user(current_user, learner)
    await require_active_consent_for_current_user(db, current_user, learner_id)
    return await svc.get_subject_mastery_summary(learner_id)


@router.get("/{learner_id}/mastery/{caps_ref}")
async def get_topic_mastery(
    learner_id: str,
    caps_ref: str,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
):
    svc = LearnerService(db)
    learner = await svc.get_learner_summary(learner_id)
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_read_for_current_user(current_user, learner)
    await require_active_consent_for_current_user(db, current_user, learner_id)
    return await svc.get_topic_mastery(learner_id, caps_ref)


@router.delete("/{learner_id}", status_code=status.HTTP_202_ACCEPTED)
async def request_erasure(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_parent_or_admin),
):
    """Create a canonical POPIA erasure request for a learner.

    Legacy DELETE semantics are preserved as an erasure request entry point,
    but the route no longer bypasses the POPIA state machine or audit controls.
    """
    return await POPIADataRightsService(db).request_erasure(learner_id=learner_id, current_user=current_user)


async def enqueue_data_purge(learner_id: str, learner_pseudonym: str) -> None:
    log.info(
        "learner_data_purge_queued",
        learner_id=learner_id,
        learner_pseudonym=learner_pseudonym,
    )
