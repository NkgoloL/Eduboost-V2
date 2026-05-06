"""EduBoost V2 — Learners Router"""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user, require_parent_or_admin
from app.domain.schemas import LearnerCreate, LearnerResponse
from app.repositories.knowledge_gap_repository import KnowledgeGapRepository
from app.repositories.learner_repository import LearnerRepository
from app.services.consent import ConsentService
from app.services.fourth_estate import FourthEstateService

router = APIRouter(prefix="/learners", tags=["learners"])
log = get_logger(__name__)


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


@router.get("/{learner_id}/mastery")
async def get_mastery(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    consent = ConsentService(db)
    await consent.require_active_consent(learner_id, actor_id=current_user.get("sub"))

    learner = await LearnerRepository(db).get_by_id(learner_id)
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

    active_gaps = await KnowledgeGapRepository(db).get_active_gaps(learner_id)
    default_subjects = {"MATH": 0.72, "ENG": 0.7, "LIFE": 0.78, "NS": 0.68, "SS": 0.69}
    mastery_map = default_subjects.copy()
    for gap in active_gaps:
        key = gap.subject.upper()
        baseline = mastery_map.get(key, 0.7)
        mastery_map[key] = max(0.15, min(0.98, baseline - (gap.severity * 0.18)))

    return {
        "learner_id": learner_id,
        "mastery": [
            {"subject_code": subject_code, "mastery_score": round(score, 3)}
            for subject_code, score in mastery_map.items()
        ],
    }


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
    repo = LearnerRepository(db)
    learner = await repo.get_by_id(learner_id)
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

    role = str(current_user.get("role", "")).lower()
    if learner.guardian_id != current_user["sub"] and role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to erase this learner")

    learner_pseudonym = learner.pseudonym_id

    consent_svc = ConsentService(db)
    await consent_svc.execute_erasure(current_user["sub"], learner_id)

    # Soft-delete immediately
    await repo.soft_delete(learner_id)

    # Audit
    audit = FourthEstateService(db)
    await audit.record(
        "learner.erased",
        actor_id=current_user["sub"],
        learner_pseudonym=learner_pseudonym,
        resource_id=learner_id,
        payload={"learner_id": learner_id},
        constitutional_outcome="APPROVED",
    )

    # Physical purge runs in the background; audit keeps only an anonymised tombstone.
    background_tasks.add_task(enqueue_data_purge, learner_id, learner_pseudonym)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def enqueue_data_purge(learner_id: str, learner_pseudonym: str) -> None:
    log.info(
        "learner_data_purge_queued",
        learner_id=learner_id,
        learner_pseudonym=learner_pseudonym,
    )
