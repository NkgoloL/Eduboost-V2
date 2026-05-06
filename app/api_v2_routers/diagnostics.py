"""EduBoost V2 — Diagnostic Router"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import check_ai_quota
from app.core.security import get_current_user
from app.domain.schemas import DiagnosticResult, DiagnosticSubmit
from app.repositories.learner_repository import LearnerRepository
from app.repositories.diagnostic_repository import DiagnosticRepository
from app.repositories.auth_repository import GuardianRepository
from app.repositories.irt_repository import IRTRepository
from app.repositories.knowledge_gap_repository import KnowledgeGapRepository
from app.services.consent import ConsentService
from app.services.diagnostic import DiagnosticEngine

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])
_engine = DiagnosticEngine()


@router.get("/items/{learner_id}")
async def get_diagnostic_items(
    learner_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    await ConsentService(db).require_active_consent(learner_id)
    learner = await LearnerRepository(db).get_by_id(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")
    request.state.analytics = {
        "event": "diagnostic_started",
        "pseudonym_id": learner.pseudonym_id,
        "properties": {"learner_grade": learner.grade},
    }

    items = await IRTRepository(db).get_items_for_grade(learner.grade, limit=20)
    return [
        {"id": i.id, "question": i.question_text, "options": i.options, "subject": i.subject, "topic": i.topic}
        for i in items
    ]


@router.post("/submit", response_model=DiagnosticResult)
async def submit_diagnostic(
    body: DiagnosticSubmit,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    await ConsentService(db).require_active_consent(body.learner_id)
    learner = await LearnerRepository(db).get_by_id(body.learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")
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
