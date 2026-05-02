"""EduBoost V2 — Learners Router"""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_db
from app.core.security import get_current_user, require_parent_or_admin
from app.domain.schemas import LearnerCreate, LearnerResponse
from app.repositories.repositories import LearnerRepository
from app.services.consent import ConsentService
from app.services.fourth_estate import FourthEstateService

router = APIRouter(prefix="/learners", tags=["learners"])


@router.post("/", response_model=LearnerResponse, status_code=status.HTTP_201_CREATED)
async def create_learner(
    body: LearnerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_parent_or_admin),
):
    repo = LearnerRepository(db)
    learner = await repo.create(
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

    repo = LearnerRepository(db)
    learner = await repo.get_by_id(learner_id)
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    return LearnerResponse.model_validate(learner)


@router.delete("/{learner_id}", status_code=status.HTTP_202_ACCEPTED)
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
    repo = LearnerRepository(db)
    learner = await repo.get_by_id(learner_id)
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

    if learner.guardian_id != current_user["sub"] and current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to erase this learner")

    learner_pseudonym = learner.pseudonym_id

    # Soft-delete immediately
    await repo.soft_delete(learner_id)

    # Revoke consent
    consent_svc = ConsentService(db)
    await consent_svc.revoke(learner_id)

    # Audit
    audit = FourthEstateService(db)
    await audit.erasure_requested(current_user["sub"], learner_pseudonym)

    # Physical purge runs in the background; audit keeps only an anonymised tombstone.
    background_tasks.add_task(_execute_physical_purge, learner_id, learner_pseudonym)

    return {"detail": f"Erasure of learner {learner_id} initiated. Physical purge within 30 days."}


async def _execute_physical_purge(learner_id: str, learner_pseudonym: str) -> None:
    async with AsyncSessionLocal() as session:
        try:
            await LearnerRepository(session).purge_personal_data(learner_id)
            await FourthEstateService(session).erasure_executed(learner_pseudonym)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
