from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.repositories.item_bank_repository import ItemBankRepository

router = APIRouter(prefix="/admin/items", tags=["item-bias-review"])


class BiasReviewRequest(BaseModel):
    outcome: str = Field(..., pattern="^(approve|retire|needs_revision)$")
    notes: str | None = Field(default=None, max_length=2000)


def _require_admin(user: dict) -> None:
    if str(user.get("role", "")).lower() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")


@router.get("/bias-review-queue")
async def bias_review_queue(caps_ref: str | None = None, limit: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    _require_admin(current_user)
    repo = ItemBankRepository(db)
    refs = [caps_ref] if caps_ref else []
    items = []
    for ref in refs:
        items.extend(await repo.list_by_caps_ref(ref, limit=limit))
    flagged = [item for item in items if (item.quality_score is not None and float(item.quality_score) < 0.7) or not item.safety_passed]
    return [{"item_id": str(item.item_id), "caps_ref": item.caps_ref, "language": getattr(item.language, "value", item.language), "grade": item.grade, "quality_score": float(item.quality_score) if item.quality_score is not None else None} for item in flagged[:limit]]


@router.post("/{item_id}/bias-review")
async def record_bias_review(item_id: UUID, body: BiasReviewRequest, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    _require_admin(current_user)
    status_value = "retired" if body.outcome == "retire" else "human_reviewed"
    item = await ItemBankRepository(db).update_review_status(item_id, status_value, reviewer_id=UUID(str(current_user["sub"])))
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": str(item.item_id), "review_status": getattr(item.review_status, "value", item.review_status), "outcome": body.outcome, "notes": body.notes}
