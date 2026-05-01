"""Typed request/response models for EduBoost V2 routers."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LessonGenerateRequest(BaseModel):
    learner_id: str
    subject_code: str
    topic: str
    grade_level: int = Field(default=4, ge=0, le=7)


class DiagnosticRunRequest(BaseModel):
    subject_code: str
    max_questions: int = Field(default=10, ge=1, le=50)


class StudyPlanGenerateRequest(BaseModel):
    gap_ratio: float = Field(default=0.4, ge=0.0, le=1.0)


class AssessmentResponseItem(BaseModel):
    question_id: str
    learner_answer: str


class AssessmentAttemptRequest(BaseModel):
    learner_id: str
    responses: list[AssessmentResponseItem]
    time_taken_seconds: int = Field(default=0, ge=0)
