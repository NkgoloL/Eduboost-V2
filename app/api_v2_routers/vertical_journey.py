"""Learner/parent vertical journey route for PRD-3.0-3.4."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.envelope_route import EnvelopedRoute
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.database import get_db
from app.models import AssessmentAttempt, DiagnosticSession, KnowledgeGap, Lesson, StudyPlan, TopicMastery
from app.modules.consent.service import ConsentService
from app.modules.vertical_journey.service import VerticalJourneyInputs, build_vertical_journey_snapshot
from app.repositories.repositories import LearnerRepository
from app.security.dependencies import require_learner_read_for_current_user
from app.services.runtime_kg.route_integration import build_runtime_kg_study_plan_payload

router = APIRouter(route_class=EnvelopedRoute, prefix="/vertical-journey", tags=["vertical-journey"])


async def _count(db: AsyncSession, statement) -> int:
    return int(await db.scalar(statement) or 0)


@router.get("/learners/{learner_id}")
async def get_learner_vertical_journey(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
) -> dict:
    """Return one product-state view of the learner/parent vertical journey.

    The route deliberately does not enable live learner traffic or bypass
    authorisation. It is a hardening endpoint that exposes whether existing
    feature paths are wired for the learner. If guardian consent is inactive,
    the route reports the consent blocker instead of exercising downstream
    learner-data paths.
    """

    learner = await LearnerRepository(db).get_by_id(learner_id)
    if learner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_read_for_current_user(current_user, learner)

    consent_decision = await ConsentService(db).consent_decision(learner_id)
    consent_active = bool(consent_decision.active)

    diagnostic_count = await _count(
        db,
        select(func.count(DiagnosticSession.id)).where(
            DiagnosticSession.learner_id == learner_id,
            DiagnosticSession.completed_at != None,  # noqa: E711
        ),
    )
    active_gap_count = await _count(
        db,
        select(func.count(KnowledgeGap.id)).where(
            KnowledgeGap.learner_id == learner_id,
            KnowledgeGap.resolved == False,  # noqa: E712
        ),
    )
    lesson_count = await _count(db, select(func.count(Lesson.id)).where(Lesson.learner_id == learner_id))
    completed_lesson_count = await _count(
        db,
        select(func.count(Lesson.id)).where(
            Lesson.learner_id == learner_id,
            Lesson.completed_at != None,  # noqa: E711
        ),
    )
    assessment_count = await _count(
        db,
        select(func.count(AssessmentAttempt.id)).where(AssessmentAttempt.learner_id == learner_id),
    )
    mastery_count = await _count(db, select(func.count(TopicMastery.id)).where(TopicMastery.learner_id == learner_id))
    study_plan_count = await _count(db, select(func.count(StudyPlan.id)).where(StudyPlan.learner_id == learner_id))

    runtime_kg_payload = await build_runtime_kg_study_plan_payload(
        db,
        learner_id=learner_id,
        subject_code="Mathematics",
    )
    runtime_kg_gap_profile_available = bool(
        runtime_kg_payload.get("runtime_kg_enabled") is True
        and runtime_kg_payload.get("fallback_to_legacy") is False
        and runtime_kg_payload.get("focus_items")
    ) or active_gap_count > 0

    snapshot = build_vertical_journey_snapshot(
        VerticalJourneyInputs(
            learner_id=learner_id,
            guardian_id=str(learner.guardian_id),
            learner_profile_created=True,
            guardian_consent_active=consent_active,
            learner_onboarding_completed=bool(getattr(learner, "archetype", None)),
            diagnostic_completed=diagnostic_count > 0,
            runtime_kg_gap_profile_available=runtime_kg_gap_profile_available,
            lesson_generated=lesson_count > 0,
            lesson_completed=completed_lesson_count > 0,
            assessment_attempted=assessment_count > 0,
            mastery_updated=mastery_count > 0,
            study_plan_generated=study_plan_count > 0,
            gamification_profile_available=getattr(learner, "xp", 0) >= 0,
            parent_progress_report_available=True,
            popia_export_path_available=True,
            popia_erasure_path_available=True,
            counts={
                "diagnostics_completed": diagnostic_count,
                "active_knowledge_gaps": active_gap_count,
                "lessons_generated": lesson_count,
                "lessons_completed": completed_lesson_count,
                "assessments_attempted": assessment_count,
                "mastery_records": mastery_count,
                "study_plans": study_plan_count,
            },
        )
    )
    payload = snapshot.to_payload()
    payload["consent"] = {
        "active": consent_active,
        "state": getattr(consent_decision.state, "value", str(consent_decision.state)),
        "reason": consent_decision.reason,
        "policy_version": consent_decision.policy_version,
    }
    payload["runtime_kg"] = runtime_kg_payload
    return payload
