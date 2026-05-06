from __future__ import annotations

from pydantic import BaseModel, Field


class LessonContent(BaseModel):
    title: str
    introduction: str
    main_content: str
    worked_example: str
    practice_question: str
    answer: str
    cultural_hook: str


class StudyPlanContent(BaseModel):
    week_label: str
    daily_topics: list[str] = Field(default_factory=list)
    priority_gaps: list[str] = Field(default_factory=list)


class DiagnosticFeedback(BaseModel):
    summary: str
    encouragement: str
    next_steps: list[str] = Field(default_factory=list)

