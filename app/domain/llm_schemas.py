from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class LessonTrustLabel(BaseModel):
    ai_generated: bool = True
    caps_linked: bool = False
    answer_checked: bool = False
    teacher_reviewed: bool = False
    safety_checked: bool = False
    curriculum_version: str | None = None


class LessonContent(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    introduction: str = Field(min_length=2)
    main_content: str = Field(min_length=2)
    worked_example: str = Field(min_length=2)
    practice_question: str = Field(min_length=2)
    answer: str = Field(min_length=1)
    cultural_hook: str = Field(min_length=2)
    caps_reference: str | None = None
    caps_topic: str | None = None
    caps_subtopic: str | None = None
    lesson_variant: Literal["standard", "visual", "story", "step_by_step", "exam_style", "real_world_sa"] = "standard"
    language_level: Literal["foundation", "intermediate", "senior"] | None = None
    safety_classification: Literal["safe", "needs_review", "blocked"] = "safe"
    alignment_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    trust_label: LessonTrustLabel = Field(default_factory=LessonTrustLabel)

    @field_validator("caps_reference")
    @classmethod
    def caps_reference_must_use_canonical_prefix(cls, value: str | None) -> str | None:
        if value is not None and not value.startswith("CAPS:"):
            raise ValueError("caps_reference must use the canonical CAPS:<version>:... format")
        return value

    @model_validator(mode="after")
    def trust_label_matches_fields(self) -> "LessonContent":
        if self.caps_reference:
            self.trust_label.caps_linked = True
        if self.answer.strip():
            self.trust_label.answer_checked = True
        if self.safety_classification == "safe":
            self.trust_label.safety_checked = True
        return self


class StudyPlanContent(BaseModel):
    week_label: str
    daily_topics: list[str] = Field(default_factory=list)
    priority_gaps: list[str] = Field(default_factory=list)


class DiagnosticFeedback(BaseModel):
    summary: str
    encouragement: str
    next_steps: list[str] = Field(default_factory=list)


class DiagnosticItemContract(BaseModel):
    item_id: str = Field(min_length=1)
    subject: str = Field(min_length=2)
    grade: int = Field(ge=0, le=12)
    topic: str = Field(min_length=2)
    skill: str = Field(min_length=2)
    difficulty: float = Field(ge=-4.0, le=4.0)
    discrimination: float = Field(gt=0.0, le=4.0)
    correct_answer: str = Field(pattern="^[A-D]$")
    distractors: dict[str, str]
    explanation: str = Field(min_length=2)
    caps_reference: str = Field(min_length=8)
    review_status: Literal["draft", "ai_generated", "human_reviewed", "approved", "retired"] = "draft"
    misconception_tag: str | None = None

    @model_validator(mode="after")
    def validate_options(self) -> "DiagnosticItemContract":
        expected = {"A", "B", "C", "D"}
        if set(self.distractors) != expected:
            raise ValueError("distractors must contain exactly A, B, C and D")
        if self.correct_answer not in self.distractors:
            raise ValueError("correct_answer must exist in distractors")
        if not self.caps_reference.startswith("CAPS:"):
            raise ValueError("caps_reference must use canonical CAPS:<version>:... format")
        return self
