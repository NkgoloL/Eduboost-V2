from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.domain.lesson import ReviewStatus, SafetyClassification
from app.repositories.lesson_repository import LessonRepository, get_lesson_repository

router = APIRouter(tags=["lesson-review"])
QUALITY_SCORE_REVIEW_THRESHOLD = 0.7


class UserRole(str, Enum):
    LEARNER = "learner"
    STUDENT = "student"
    TEACHER = "teacher"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class CurrentUser(BaseModel):
    user_id: UUID
    role: UserRole
    email: str | None = None


class ReviewDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


class LessonReviewRequest(BaseModel):
    decision: ReviewDecision
    reviewer_notes: str | None = Field(default=None, max_length=2000)


class QueuedLessonSummary(BaseModel):
    lesson_id: str
    caps_ref: str | None
    grade: int
    subject: str
    topic: str
    subtopic: str | None
    quality_score: float | None
    answer_key_verified: bool
    safety_classification: SafetyClassification
    review_status: ReviewStatus
    auto_queue_reason: list[str]
    created_at: datetime
    provider: str | None
    prompt_template_version: str | None


class ReviewQueueResponse(BaseModel):
    total_pending: int
    lessons: list[QueuedLessonSummary]


class ReviewActionResponse(BaseModel):
    lesson_id: str
    review_status: ReviewStatus
    reviewer_id: str
    reviewed_at: datetime
    message: str


def _coerce_user(raw: dict) -> CurrentUser:
    return CurrentUser(
        user_id=UUID(str(raw.get("sub") or raw.get("user_id") or raw.get("id"))),
        role=UserRole(str(raw.get("role", "learner")).lower()),
        email=raw.get("email"),
    )


def compute_auto_queue_reasons(
    quality_score: float | None,
    answer_key_verified: bool,
    safety_classification: SafetyClassification | str,
) -> list[str]:
    reasons: list[str] = []
    if quality_score is None or quality_score < QUALITY_SCORE_REVIEW_THRESHOLD:
        score = "N/A" if quality_score is None else f"{quality_score:.2f}"
        reasons.append(f"Quality score {score} is below the {QUALITY_SCORE_REVIEW_THRESHOLD} threshold.")
    if not answer_key_verified:
        reasons.append("Answer key has not been independently verified.")
    if str(safety_classification) in {"SafetyClassification.REQUIRES_REVIEW", "requires_review"}:
        reasons.append("Safety classifier flagged content as requiring human review.")
    return reasons


def should_auto_queue(quality_score: float | None, answer_key_verified: bool, safety_classification: SafetyClassification | str) -> bool:
    return bool(compute_auto_queue_reasons(quality_score, answer_key_verified, safety_classification))


async def require_reviewer(current_user: dict = Depends(get_current_user)) -> CurrentUser:
    user = _coerce_user(current_user)
    if user.role not in {UserRole.REVIEWER, UserRole.ADMIN}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Reviewer or admin role required.")
    return user


@router.get("/review/queue", response_model=ReviewQueueResponse)
async def get_review_queue(
    grade: int | None = Query(None, ge=1, le=12),
    subject: str | None = None,
    caps_ref: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: CurrentUser = Depends(require_reviewer),
    repo: LessonRepository = Depends(get_lesson_repository),
) -> ReviewQueueResponse:
    lessons = await repo.list_pending_review(grade=grade, subject=subject, caps_ref=caps_ref, limit=limit, offset=offset)
    summaries = [
        QueuedLessonSummary(
            lesson_id=str(l.id),
            caps_ref=l.caps_ref or l.caps_reference,
            grade=l.grade,
            subject=l.subject,
            topic=l.topic,
            subtopic=l.subtopic,
            quality_score=l.quality_score,
            answer_key_verified=l.answer_key_verified,
            safety_classification=SafetyClassification(l.safety_classification),
            review_status=ReviewStatus(l.review_status),
            auto_queue_reason=compute_auto_queue_reasons(l.quality_score, l.answer_key_verified, l.safety_classification),
            created_at=l.created_at,
            provider=l.provider or l.llm_provider,
            prompt_template_version=l.prompt_template_version,
        )
        for l in lessons
    ]
    return ReviewQueueResponse(total_pending=len(summaries), lessons=summaries)


@router.post("/{lesson_id}/review", response_model=ReviewActionResponse)
async def review_lesson(
    lesson_id: UUID,
    body: LessonReviewRequest,
    current_user: CurrentUser = Depends(require_reviewer),
    repo: LessonRepository = Depends(get_lesson_repository),
) -> ReviewActionResponse:
    updated = await repo.update_review_status(
        lesson_id, review_status=body.decision.value, reviewer_id=current_user.user_id, reviewer_notes=body.reviewer_notes
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return ReviewActionResponse(
        lesson_id=str(updated.id),
        review_status=ReviewStatus(updated.review_status),
        reviewer_id=str(current_user.user_id),
        reviewed_at=updated.reviewed_at or datetime.now(timezone.utc),
        message=f"Lesson {body.decision.value}.",
    )
