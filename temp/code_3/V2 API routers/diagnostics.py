"""EduBoost V2 — Diagnostic Router"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.schemas import DiagnosticResult, DiagnosticSubmit
from app.repositories.repositories import DiagnosticRepository, IRTRepository, KnowledgeGapRepository, LearnerRepository
from app.services.consent import ConsentService
from app.services.diagnostic import DiagnosticEngine

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])
_engine = DiagnosticEngine()


@router.get("/items/{learner_id}")
async def get_diagnostic_items(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    await ConsentService(db).require_active_consent(learner_id)
    learner = await LearnerRepository(db).get_by_id(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")

    items = await IRTRepository(db).get_items_for_grade(learner.grade, limit=20)
    return [
        {"id": i.id, "question": i.question_text, "options": i.options, "subject": i.subject, "topic": i.topic}
        for i in items
    ]


@router.post("/submit", response_model=DiagnosticResult)
async def submit_diagnostic(
    body: DiagnosticSubmit,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    await ConsentService(db).require_active_consent(body.learner_id)
    learner = await LearnerRepository(db).get_by_id(body.learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")

    items = await IRTRepository(db).get_items_for_grade(learner.grade)
    item_map = {i.id: i for i in items}

    correct_ids = {a.item_id for a in body.answers if item_map.get(a.item_id) and a.selected_option == item_map[a.item_id].correct_option}
    responses_dict = {a.item_id: a.selected_option for a in body.answers}

    theta_after = _engine.compute_theta(learner.theta, items, correct_ids)

    # Persist session
    diag_repo = DiagnosticRepository(db)
    session = await diag_repo.create_session(body.learner_id, learner.theta)
    await diag_repo.complete_session(session.id, responses_dict, theta_after)

    # Update learner theta
    await LearnerRepository(db).update_theta(body.learner_id, theta_after)

    # Identify and persist gaps
    gaps = _engine.identify_gaps(items, correct_ids)
    gap_repo = KnowledgeGapRepository(db)
    for g in gaps:
        await gap_repo.upsert(body.learner_id, g["grade"], g["subject"], g["topic"], g["severity"])

    gap_labels = [f"{g['subject']}: {g['topic']}" for g in gaps]

    return DiagnosticResult(
        session_id=session.id,
        theta_before=learner.theta,
        theta_after=theta_after,
        gaps_identified=gap_labels,
    )
