from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.repositories.item_bank_repository import ItemBankRepository
from app.repositories.practice_session_repository import PracticeSessionRepository
from app.security.dependencies import actor_id_from_current_user, require_active_consent_for_current_user, require_learner_write_for_current_user
from app.modules.practice.practice_generator import PracticeGenerator
from app.modules.practice.spaced_repetition_scheduler import SpacedRepetitionScheduler

router = APIRouter(prefix="/practice", tags=["practice"])


class PracticeSessionRequest(BaseModel):
    learner_id: UUID
    gap_topics: list[str] = Field(default_factory=list)
    theta: float = 0.0


class PracticeResponseRequest(BaseModel):
    item_id: UUID
    correct: bool
    response: str | None = None


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_practice_session(body: PracticeSessionRequest, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    require_learner_write_for_current_user(current_user, str(body.learner_id))
    await require_active_consent_for_current_user(db, current_user, str(body.learner_id))
    repo = ItemBankRepository(db)
    items = []
    for caps_ref in body.gap_topics:
        items.extend(await repo.list_by_caps_ref(caps_ref, limit=100))
    selected = PracticeGenerator().select_items(items, gap_topics=body.gap_topics, theta=body.theta, per_gap=5)

    # Create durable session in database
    session_repo = PracticeSessionRepository(db)
    session = await session_repo.create(
        learner_id=str(body.learner_id),
        owner_subject=actor_id_from_current_user(current_user),
        items=[str(i.item_id) for i in selected],
        gap_topics=body.gap_topics,
        theta=body.theta,
    )
    await db.commit()

    return {"session_id": session.id, "item_count": len(selected)}


@router.get("/sessions/{session_id}/next-item")
async def next_practice_item(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Fetch from durable storage
    session_repo = PracticeSessionRepository(db)
    session = await session_repo.get_by_id(session_id)
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
):
    # Fetch from durable storage
    session_repo = PracticeSessionRepository(db)
    session = await session_repo.get_by_id(session_id)
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

    # Record response and advance cursor
    new_responses = session.responses + [body.model_dump(mode="json")]
    new_cursor = session.cursor + 1
    await session_repo.update_cursor_and_responses(session_id, new_cursor, new_responses)
    await db.commit()

    # Calculate next review timing and return status
    schedule = SpacedRepetitionScheduler().update_schedule(correct=body.correct)
    if new_cursor >= len(session.items):
        await session_repo.mark_completed(session_id)
        await db.commit()
        return {"completed": True, "next_review_at": schedule.next_review_at.isoformat(), "interval_days": schedule.interval_days}
    return {"accepted": True, "next_review_at": schedule.next_review_at.isoformat(), "interval_days": schedule.interval_days}
