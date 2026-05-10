"""EduBoost V2 — Diagnostic Router"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.authorization import assert_can_access_learner
from app.core.database import get_db
from app.core.rate_limiter import check_ai_quota
from app.core.security import get_current_user
from app.domain.schemas import DiagnosticResult, DiagnosticSubmit
from app.security.dependencies import require_learner_read_for_current_user, require_active_consent_for_current_user
from app.security.dependencies import require_learner_write_for_current_user
from app.repositories.repositories import (
    DiagnosticRepository,
    GuardianRepository,
    IRTRepository,
    KnowledgeGapRepository,
    LearnerRepository,
)
from app.services.diagnostic import DiagnosticEngine
from app.services.caps_validator import CAPSAlignmentValidator
from app.core.metrics import ITEM_BANK_COVERAGE_RATIO
from app.modules.diagnostics.item_bank_service import ItemBankService
from app.repositories.item_bank_repository import ItemBankRepository

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])
_engine = DiagnosticEngine()
_caps_validator = CAPSAlignmentValidator()


class ReviewItemRequest(BaseModel):
    review_status: str = Field(..., pattern="^(draft|ai_generated|human_reviewed|approved|retired)$")
    quality_score: float | None = Field(default=None, ge=0.0, le=1.0)


def _require_item_bank_admin(current_user: dict) -> None:
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Item bank administration requires admin role",
        )


@router.get("/items/{learner_id}")
async def get_diagnostic_items(
    learner_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    learner = await LearnerRepository(db).get_by_id(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")
    require_learner_read_for_current_user(current_user, learner)
    await require_active_consent_for_current_user(db, current_user, str(learner_id))
    request.state.analytics = {
        "event": "diagnostic_started",
        "pseudonym_id": learner.pseudonym_id,
        "properties": {"learner_grade": learner.grade},
    }

    items = await IRTRepository(db).get_items_for_grade(learner.grade, limit=20)
    return [
        {
            "id": i.id,
            "question": i.question_text,
            "options": i.options,
            "subject": i.subject,
            "topic": i.topic,
            "skill": getattr(i, "skill", None) or i.topic,
            "difficulty": i.b_param,
            "discrimination": i.a_param,
            "caps_reference": getattr(i, "caps_reference", None)
            or _caps_validator.validate(i.grade, i.subject, i.topic).caps_reference,
            "review_status": getattr(getattr(i, "review_status", "draft"), "value", getattr(i, "review_status", "draft")),
        }
        for i in items
    ]


@router.post("/submit", response_model=DiagnosticResult)
async def submit_diagnostic(
    body: DiagnosticSubmit,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    learner = await LearnerRepository(db).get_by_id(body.learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")
    require_learner_write_for_current_user(current_user, body.learner_id)
    await require_active_consent_for_current_user(db, current_user, str(body.learner_id))
    guardian = await GuardianRepository(db).get_by_id(learner.guardian_id)
    tier = guardian.subscription_tier if guardian else "free"
    await check_ai_quota(learner.guardian_id, tier)

    items = await IRTRepository(db).get_items_for_grade(learner.grade)
    item_map = {i.id: i for i in items}

    correct_ids = {a.item_id for a in body.answers if item_map.get(a.item_id) and a.selected_option == item_map[a.item_id].correct_option}
    responses_dict = {a.item_id: a.selected_option for a in body.answers}

    analysis = _engine.run_gap_probe_cascade(
        learner_grade=learner.grade,
        items=items,
        correct_item_ids=correct_ids,
        starting_theta=learner.theta,
    )
    theta_after = analysis["theta"]

    # Persist session
    diag_repo = DiagnosticRepository(db)
    session = await diag_repo.create_session(body.learner_id, learner.theta)
    await diag_repo.complete_session(session.id, responses_dict, theta_after)

    # Update learner theta
    await LearnerRepository(db).update_theta(body.learner_id, theta_after)

    # Identify and persist gaps
    gaps = analysis["ranked_gaps"]
    gap_repo = KnowledgeGapRepository(db)
    for g in gaps:
        await gap_repo.upsert(body.learner_id, g["grade"], g["subject"], g["topic"], g["severity"])

    gap_labels = [f"{g['subject']}: {g['topic']}" for g in gaps]
    request.state.analytics = {
        "event": "diagnostic_completed",
        "pseudonym_id": learner.pseudonym_id,
        "properties": {"gap_count": len(gaps), "theta_after": theta_after},
    }

    return DiagnosticResult(
        session_id=session.id,
        theta_before=learner.theta,
        theta_after=theta_after,
        gaps_identified=gap_labels,
        standard_error=analysis["standard_error"],
        grade_equivalent=analysis["grade_equivalent"],
        ranked_gaps=gaps,
    )


@router.get("/coverage")
async def get_item_bank_coverage(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    _require_item_bank_admin(current_user)
    service = ItemBankService(ItemBankRepository(db))
    summary = await service.get_coverage_summary()
    for caps_ref, row in summary.items():
        ITEM_BANK_COVERAGE_RATIO.labels(caps_ref=caps_ref).set(row.get("coverage_ratio", 0.0))
    return summary


@router.get("/item-bank/items/{item_id}")
async def get_item_bank_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    _require_item_bank_admin(current_user)
    item = await ItemBankRepository(db).get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "item_id": str(item.item_id),
        "caps_ref": item.caps_ref,
        "grade": item.grade,
        "subject": getattr(item.subject, "value", item.subject),
        "term": item.term,
        "topic": item.topic,
        "subtopic": item.subtopic,
        "skill": item.skill,
        "stem": item.stem,
        "answer_key": item.answer_key,
        "options": item.options,
        "explanation": item.explanation,
        "distractor_rationale": item.distractor_rationale,
        "misconception_tags": item.misconception_tags,
        "difficulty_b": float(item.difficulty_b),
        "discrimination_a": float(item.discrimination_a),
        "guessing_c": float(item.guessing_c),
        "review_status": getattr(item.review_status, "value", item.review_status),
        "reviewer_id": str(item.reviewer_id) if item.reviewer_id else None,
        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
        "exposure_count": item.exposure_count,
        "max_exposure": item.max_exposure,
        "quality_score": float(item.quality_score) if item.quality_score is not None else None,
        "safety_passed": item.safety_passed,
    }


@router.post("/item-bank/items/{item_id}/review")
async def review_item_bank_item(
    item_id: UUID,
    body: ReviewItemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    _require_item_bank_admin(current_user)
    reviewer_id = UUID(str(current_user["sub"]))
    service = ItemBankService(ItemBankRepository(db))
    item = await service.mark_item_reviewed(
        item_id=item_id,
        new_status=body.review_status,
        reviewer_id=reviewer_id,
        quality_score=body.quality_score,
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "item_id": str(item.item_id),
        "review_status": getattr(item.review_status, "value", item.review_status),
        "reviewer_id": str(item.reviewer_id) if item.reviewer_id else None,
        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
    }
