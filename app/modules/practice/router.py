from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.repositories.item_bank_repository import ItemBankRepository
from app.security.dependencies import require_active_consent_for_current_user, require_learner_write_for_current_user
from app.modules.practice.practice_generator import PracticeGenerator
from app.modules.practice.spaced_repetition_scheduler import SpacedRepetitionScheduler

router = APIRouter(prefix="/practice", tags=["practice"])
_SESSIONS: dict[str, dict] = {}


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
    session_id = str(uuid4())
    _SESSIONS[session_id] = {"learner_id": str(body.learner_id), "items": [str(i.item_id) for i in selected], "cursor": 0, "responses": []}
    return {"session_id": session_id, "item_count": len(selected)}


@router.get("/sessions/{session_id}/next-item")
async def next_practice_item(session_id: str):
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Practice session not found")
    if session["cursor"] >= len(session["items"]):
        return {"completed": True}
    item_id = session["items"][session["cursor"]]
    return {"completed": False, "item_id": item_id}


@router.post("/sessions/{session_id}/respond")
async def respond_practice(session_id: str, body: PracticeResponseRequest):
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Practice session not found")
    session["responses"].append(body.model_dump(mode="json"))
    session["cursor"] += 1
    schedule = SpacedRepetitionScheduler().update_schedule(correct=body.correct)
    return {"accepted": True, "next_review_at": schedule.next_review_at.isoformat(), "interval_days": schedule.interval_days}
