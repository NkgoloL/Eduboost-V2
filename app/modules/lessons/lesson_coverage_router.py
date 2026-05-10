from __future__ import annotations

import statistics
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService, get_caps_topic_map_service
from app.repositories.lesson_repository import LessonRepository, get_lesson_repository

router = APIRouter(tags=["lesson-coverage"])


class QualityScoreDistribution(BaseModel):
    count: int
    mean: float | None = None
    min: float | None = None
    max: float | None = None
    p25: float | None = None
    p75: float | None = None
    below_threshold: int = Field(description="Lessons with quality_score < 0.7.")


class CapsRefCoverage(BaseModel):
    caps_ref: str
    grade: int
    subject: str
    term: int | None
    topic: str
    subtopic: str | None = None
    total_lessons: int
    approved_lessons: int
    pending_review_lessons: int
    rejected_lessons: int
    ai_generated_lessons: int
    quality_score_distribution: QualityScoreDistribution
    answer_key_verified_count: int
    answer_key_verification_rate_pct: float
    avg_generation_latency_ms: float | None
    coverage_status: str
    review_queue_depth: int
    provider_breakdown: dict[str, int] = Field(default_factory=dict)


class CoverageSummary(BaseModel):
    total_caps_refs_in_scope: int
    green_refs: int
    amber_refs: int
    red_refs: int
    uncovered_refs: int
    total_approved_lessons: int
    total_pending_review_lessons: int
    overall_review_queue_depth: int
    overall_answer_key_verification_rate_pct: float
    overall_avg_quality_score: float | None


class CoverageResponse(BaseModel):
    grade: int | None
    subject: str | None
    summary: CoverageSummary
    per_caps_ref: list[CapsRefCoverage]


def compute_quality_distribution(scores: list[float]) -> QualityScoreDistribution:
    if not scores:
        return QualityScoreDistribution(count=0, below_threshold=0)
    ordered = sorted(scores)
    n = len(ordered)
    return QualityScoreDistribution(
        count=n,
        mean=round(statistics.mean(scores), 3),
        min=round(min(scores), 3),
        max=round(max(scores), 3),
        p25=round(ordered[max(0, int(n * 0.25) - 1)], 3),
        p75=round(ordered[min(n - 1, int(n * 0.75))], 3),
        below_threshold=sum(1 for score in scores if score < 0.7),
    )


def compute_coverage_status(approved_count: int, total_count: int) -> str:
    if total_count == 0:
        return "uncovered"
    if approved_count == 0:
        return "red"
    if approved_count < 8:
        return "amber"
    return "green"


def _topic_rows(caps_service: CAPSTopicMapService, grade: int | None, subject: str | None) -> list[dict[str, Any]]:
    rows = []
    subject_code = None
    if subject:
        subject_code = "M" if subject.lower().startswith(("math", "m")) else subject
    for topic in caps_service.list_topics(grade=grade, subject_code=subject_code):
        ref_grade, _, ref_term, *_ = topic.caps_ref.split(".")
        rows.append({
            "caps_ref": topic.caps_ref,
            "grade": int(ref_grade),
            "subject": subject or caps_service.summary()["scopes"][0],
            "term": int(ref_term),
            "topic": topic.topic,
            "subtopic": None,
        })
        for subtopic in topic.subtopics:
            rows.append({
                "caps_ref": subtopic.caps_ref,
                "grade": int(ref_grade),
                "subject": subject or caps_service.summary()["scopes"][0],
                "term": int(ref_term),
                "topic": topic.topic,
                "subtopic": subtopic.subtopic,
            })
    return rows


@router.get("/coverage", response_model=CoverageResponse)
async def get_lesson_coverage(
    grade: int | None = Query(None, ge=1, le=12),
    subject: str | None = None,
    repo: LessonRepository = Depends(get_lesson_repository),
    caps_service: CAPSTopicMapService = Depends(get_caps_topic_map_service),
) -> CoverageResponse:
    per_ref: list[CapsRefCoverage] = []
    green = amber = red = uncovered = 0
    total_approved = total_pending = total_verified = total_lessons = 0
    quality_scores: list[float] = []

    for row in _topic_rows(caps_service, grade, subject):
        lessons = await repo.list_by_caps_ref(row["caps_ref"], include_all_statuses=True)
        approved = sum(1 for l in lessons if l.review_status == "approved")
        pending = sum(1 for l in lessons if l.review_status in {"ai_generated", "human_reviewed"})
        rejected = sum(1 for l in lessons if l.review_status == "rejected")
        generated = sum(1 for l in lessons if l.review_status == "ai_generated")
        verified = sum(1 for l in lessons if l.answer_key_verified)
        scores = [float(l.quality_score) for l in lessons if l.quality_score is not None]
        latency = [float(l.generation_latency_ms) for l in lessons if l.generation_latency_ms is not None]
        providers: dict[str, int] = {}
        for lesson in lessons:
            provider = lesson.provider or lesson.llm_provider or "unknown"
            providers[provider] = providers.get(provider, 0) + 1
        status = compute_coverage_status(approved, len(lessons))
        green += status == "green"
        amber += status == "amber"
        red += status == "red"
        uncovered += status == "uncovered"
        total_approved += approved
        total_pending += pending
        total_verified += verified
        total_lessons += len(lessons)
        quality_scores.extend(scores)
        per_ref.append(CapsRefCoverage(
            **row, total_lessons=len(lessons), approved_lessons=approved, pending_review_lessons=pending,
            rejected_lessons=rejected, ai_generated_lessons=generated,
            quality_score_distribution=compute_quality_distribution(scores),
            answer_key_verified_count=verified,
            answer_key_verification_rate_pct=round((verified / len(lessons)) * 100, 2) if lessons else 0.0,
            avg_generation_latency_ms=round(statistics.mean(latency), 2) if latency else None,
            coverage_status=status, review_queue_depth=pending, provider_breakdown=providers,
        ))

    summary = CoverageSummary(
        total_caps_refs_in_scope=len(per_ref), green_refs=green, amber_refs=amber, red_refs=red, uncovered_refs=uncovered,
        total_approved_lessons=total_approved, total_pending_review_lessons=total_pending, overall_review_queue_depth=total_pending,
        overall_answer_key_verification_rate_pct=round((total_verified / total_lessons) * 100, 2) if total_lessons else 0.0,
        overall_avg_quality_score=round(statistics.mean(quality_scores), 3) if quality_scores else None,
    )
    return CoverageResponse(grade=grade, subject=subject, summary=summary, per_caps_ref=per_ref)
