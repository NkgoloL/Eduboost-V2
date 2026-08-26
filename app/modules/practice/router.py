from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.practice.service import PracticeService
from app.security.dependencies import actor_id_from_current_user, require_active_consent_for_current_user, require_learner_write_for_current_user

router = APIRouter(prefix="/practice", tags=["practice"])


def get_practice_service(db: AsyncSession = Depends(get_db)) -> PracticeService:
    return PracticeService.from_session(db)


class PracticeSessionRequest(BaseModel):
    learner_id: UUID
    gap_topics: list[str] = Field(default_factory=list)
    theta: float = 0.0


class PracticeResponseRequest(BaseModel):
    item_id: UUID
    correct: bool
    response: str | None = None


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_practice_session(
    body: PracticeSessionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: PracticeService = Depends(get_practice_service),
):
    require_learner_write_for_current_user(current_user, str(body.learner_id))
    await require_active_consent_for_current_user(db, current_user, str(body.learner_id))

    session_id, item_count = await service.create_session(
        learner_id=str(body.learner_id),
        owner_subject=actor_id_from_current_user(current_user),
        gap_topics=body.gap_topics,
        theta=body.theta,
    )
    await db.commit()

    return {"session_id": session_id, "item_count": item_count}


@router.get("/sessions/{session_id}/next-item")
async def next_practice_item(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: PracticeService = Depends(get_practice_service),
):
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Practice session not found")

    # Authorization: Verify session owner
    owner_subject = session.owner_subject
    current_subject = actor_id_from_current_user(current_user)
    if not owner_subject or owner_subject != current_subject:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Practice session is not available to this user")

    # Authorization: Verify learner write access and consent
    require_learner_write_for_current_user(current_user, session.learner_id)
    await require_active_consent_for_current_user(db, current_user, session.learner_id)

    # Return next item or completion status
    if session.cursor >= len(session.items):
        return {"completed": True}
    item_id = session.items[session.cursor]
    return {"completed": False, "item_id": item_id}


@router.post("/sessions/{session_id}/respond")
async def respond_practice(
    session_id: str,
    body: PracticeResponseRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: PracticeService = Depends(get_practice_service),
):
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Practice session not found")

    # Authorization: Verify session owner
    owner_subject = session.owner_subject
    current_subject = actor_id_from_current_user(current_user)
    if not owner_subject or owner_subject != current_subject:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Practice session is not available to this user")

    # Authorization: Verify learner write access and consent before advancing
    require_learner_write_for_current_user(current_user, session.learner_id)
    await require_active_consent_for_current_user(db, current_user, session.learner_id)

    res = await service.record_response(session, body.model_dump(mode="json"), correct=body.correct)
    await db.commit()
    return res
