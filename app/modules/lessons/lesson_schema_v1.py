"""
app/modules/lessons/lesson_schema_v1.py
─────────────────────────────────────────────────────────────────────────────
L1-01 · L1-02 · Phase 1: Lesson Schema, Contract & CAPS Topic Map

Canonical lesson output contract for the EduBoost V2 AI lesson generation
pipeline.  Every AI-generated lesson MUST conform to this schema.

This module is the single source of truth for:
  - LessonCreate  — input from the lesson generator (pre-persistence)
  - LessonResponse — output to API consumers (post-persistence)
  - LESSON_JSON_SCHEMA — JSON Schema used by the LLM gateway validator
    and the deterministic mock provider (Phase 2 · L2-07)

Design invariants
  ─────────────────
  - No PII fields.  All learner references use pseudonym_id (UUID).
  - caps_ref is validated against the canonical CAPS topic map
    (caps_topic_map_service.py · L1-07) before persistence.
  - answer_key_verified starts False; set True only by the answer-key
    verification service (Phase 2 · L2-03).
  - quality_score starts None; computed by the quality scorer (Phase 2).
  - review_status starts "ai_generated"; updated by the review router
    (Phase 4 · L4-01).
  - created_at is set by the database server clock, never the application.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


# ─── Enums ───────────────────────────────────────────────────────────────────


class SubjectEnum(str, Enum):
    mathematics = "Mathematics"
    english = "English"
    isizulu = "isiZulu"
    afrikaans = "Afrikaans"
    life_skills = "Life Skills"
    natural_sciences = "Natural Sciences"
    natural_sciences_and_technology = "Natural Sciences and Technology"
    coding_and_robotics = "Coding and Robotics"
    home_language = "Home Language"
    sepedi_first_additional_language = "Sepedi First Additional Language"
    social_sciences = "Social Sciences"
    creative_arts = "Creative Arts"
    economic_management_sciences = "Economic Management Sciences"
    life_orientation = "Life Orientation"
    technology = "Technology"


class DifficultyLevel(str, Enum):
    foundational = "foundational"
    developing = "developing"
    on_level = "on_level"
    extending = "extending"


class SafetyClassification(str, Enum):
    safe = "safe"
    requires_review = "requires_review"
    rejected = "rejected"


class ReviewStatus(str, Enum):
    ai_generated = "ai_generated"
    human_reviewed = "human_reviewed"
    approved = "approved"
    rejected = "rejected"
    retired = "retired"


class LLMProvider(str, Enum):
    google = "google"
    groq = "groq"
    anthropic = "anthropic"
    mock = "mock"


class VariantType(str, Enum):
    """Lesson variant types — used by Phase 4 adaptive variants (L4-04)."""
    standard = "standard"
    visual = "visual"
    story = "story"
    step_by_step = "step_by_step"
    exam_style = "exam_style"
    real_world_sa = "real_world_sa"
    multilingual = "multilingual"


# ─── Nested component models ──────────────────────────────────────────────────


class WorkedExample(BaseModel):
    """A single worked example: question → step-by-step solution → answer."""
    question: str = Field(..., min_length=5, description="The worked example question text.")
    step_by_step_solution: list[str] = Field(
        ..., min_length=1, description="Ordered list of solution steps a learner can follow."
    )
    answer: str = Field(..., min_length=1, description="The final answer.")

    model_config = {"json_schema_extra": {"examples": [{
        "question": "What is 1 250 + 3 475?",
        "step_by_step_solution": [
            "Line up the digits: ones under ones, tens under tens.",
            "Add the ones: 0 + 5 = 5.",
            "Add the tens: 5 + 7 = 12. Write 2, carry 1.",
            "Add the hundreds: 2 + 4 + 1 = 7.",
            "Add the thousands: 1 + 3 = 4.",
            "Answer: 4 725.",
        ],
        "answer": "4 725",
    }]}}


class PracticeQuestion(BaseModel):
    """A single multiple-choice practice question with answer key entry."""
    question_id: str = Field(..., description="Short unique ID within this lesson, e.g. 'q1'.")
    question_text: str = Field(..., min_length=5)
    options: dict[str, str] = Field(
        ...,
        description="MCQ options keyed A–D, e.g. {'A': '4 500', 'B': '4 725', ...}.",
    )
    correct_option: str = Field(..., pattern=r"^[A-D]$", description="Correct option key.")
    explanation: str = Field(..., min_length=10, description="Why this option is correct.")
    misconception_tag: Optional[str] = Field(
        None, description="Tag identifying the misconception targeted by the distractors."
    )

    @field_validator("options")
    @classmethod
    def must_have_four_options(cls, v: dict[str, str]) -> dict[str, str]:
        if set(v.keys()) != {"A", "B", "C", "D"}:
            raise ValueError("options must have exactly the keys A, B, C, D")
        return v


class AnswerKeyEntry(BaseModel):
    """Verified answer for a single practice question."""
    question_id: str
    correct_option: str = Field(..., pattern=r"^[A-D]$")
    correct_answer_text: str


class RemediationHint(BaseModel):
    """Per-misconception hint card surfaced when a learner answers incorrectly."""
    misconception_tag: str = Field(
        ..., description="Machine-readable misconception identifier, e.g. 'place_value_confusion'."
    )
    hint_text: str = Field(..., min_length=10, description="Plain-language hint at Grade 4 reading level.")
    example: str = Field(..., description="Concrete example illustrating the correct approach.")


class TokenUsage(BaseModel):
    """Token accounting from the LLM provider response."""
    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)

    @model_validator(mode="after")
    def total_must_match(self) -> "TokenUsage":
        if self.total_tokens != self.prompt_tokens + self.completion_tokens:
            raise ValueError("total_tokens must equal prompt_tokens + completion_tokens")
        return self


# ─── Core lesson models ───────────────────────────────────────────────────────


class LessonCreate(BaseModel):
    """
    Input model: the complete lesson payload produced by the LLM gateway.
    All fields are validated before persistence.

    The lesson generator (L3-02) constructs this after the LLM call and
    after answer-key verification (L2-03).  The lesson_repository (L1-05)
    accepts this model and returns a LessonResponse.
    """

    # ── Identity & CAPS location ──────────────────────────────────────────
    caps_ref: str = Field(
        ...,
        pattern=r"^(?:R|\d+)\.[A-Z]+\.\d+(\.\d+)?(\.\d+)?$",
        description=(
            "CAPS reference code: Grade.Subject.Term[.TopicIndex[.SubtopicIndex]]. "
            "E.g. '4.M.1.1' = Grade 4, Maths, Term 1, Topic 1 (Whole Numbers)."
        ),
        examples=["4.M.1.1", "4.M.1.2", "4.M.2.1", "R.LS.1.1"],
    )
    grade: int = Field(..., ge=0, le=7, description="Grade level. Grade R is represented as 0.")
    subject: SubjectEnum
    term: int = Field(..., ge=1, le=4, description="CAPS term number.")
    topic: str = Field(..., min_length=3, description="Topic name from the CAPS topic map.")
    subtopic: str = Field(..., min_length=3, description="Subtopic name from the CAPS topic map.")

    # ── Pedagogical content ───────────────────────────────────────────────
    learning_objectives: list[str] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="1–3 specific, measurable outcomes the learner achieves from this lesson.",
    )
    explanation: str = Field(
        ...,
        min_length=50,
        description=(
            "Plain-language explanation at Grade 4 reading level, "
            "with South African context. No jargon."
        ),
    )
    worked_examples: list[WorkedExample] = Field(
        ...,
        min_length=2,
        description="Minimum 2 worked examples with step-by-step solutions.",
    )
    practice_questions: list[PracticeQuestion] = Field(
        ...,
        min_length=3,
        description="Minimum 3 MCQ practice questions with distractors targeting common misconceptions.",
    )
    answer_key: list[AnswerKeyEntry] = Field(
        ...,
        min_length=1,
        description="Explicit correct answers for all practice questions.",
    )
    remediation_hints: list[RemediationHint] = Field(
        default_factory=list,
        description="Per-misconception hint cards — one per distinct misconception_tag.",
    )

    # ── Quality & safety metadata ─────────────────────────────────────────
    difficulty_level: DifficultyLevel
    language_level: str = Field(
        ...,
        description=(
            "Flesch-Kincaid grade level as a string, e.g. '5.2'. "
            "Target: ≤ Grade 6 for Grade 4 content."
        ),
    )
    safety_classification: SafetyClassification = SafetyClassification.requires_review
    pii_check_passed: bool = Field(
        ..., description="Whether PII redaction check passed before sending to LLM."
    )
    answer_key_verified: bool = Field(
        default=False,
        description=(
            "Set True only by answer-key verification service (L2-03). "
            "Never set True by the generator itself."
        ),
    )
    quality_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="0.0–1.0 composite quality score. None until computed by quality scorer.",
    )

    # ── Generation provenance ─────────────────────────────────────────────
    prompt_template_version: str = Field(
        ...,
        description="Semantic version of the Jinja2 prompt template used, e.g. 'v1.0.0'.",
    )
    provider: LLMProvider
    model_version: str = Field(
        ..., description="Model name/version at generation time, e.g. 'llama-3.1-70b-versatile'."
    )
    generation_latency_ms: int = Field(..., ge=0, description="Wall-clock ms from request to output.")
    token_usage: TokenUsage
    variant_type: VariantType = VariantType.standard

    # ── Validators ────────────────────────────────────────────────────────
    @model_validator(mode="after")
    def answer_key_must_cover_all_questions(self) -> "LessonCreate":
        """Every practice question must have a corresponding answer_key entry."""
        question_ids = {q.question_id for q in self.practice_questions}
        answer_ids = {a.question_id for a in self.answer_key}
        missing = question_ids - answer_ids
        if missing:
            raise ValueError(
                f"answer_key is missing entries for question_id(s): {sorted(missing)}"
            )
        return self

    @model_validator(mode="after")
    def grade_must_match_caps_ref(self) -> "LessonCreate":
        """The grade prefix in caps_ref must match the grade field."""
        ref_grade_label = self.caps_ref.split(".")[0]
        ref_grade = 0 if ref_grade_label.upper() == "R" else int(ref_grade_label)
        if ref_grade != self.grade:
            raise ValueError(
                f"caps_ref grade prefix '{ref_grade_label}' does not match grade field '{self.grade}'"
            )
        return self

    model_config = {"use_enum_values": True, "protected_namespaces": ()}


class LessonResponse(LessonCreate):
    """
    Full lesson response returned by the API and lesson_repository.get_lesson().
    Adds database-assigned fields that are not present in LessonCreate.
    """

    lesson_id: UUID = Field(default_factory=uuid.uuid4)
    review_status: ReviewStatus = ReviewStatus.ai_generated
    reviewer_id: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Set by DB server clock. Application default used only in tests.",
    )

    model_config = {"from_attributes": True, "use_enum_values": True, "protected_namespaces": ()}


# ─── L1-02: JSON Schema (used by LLM gateway validator and mock provider) ────


def build_lesson_json_schema() -> dict[str, Any]:
    """
    Return the JSON Schema for a lesson payload (LessonCreate).
    Used by:
      - LLM gateway structured-output validator (Phase 2)
      - Deterministic mock LLM provider for tests (L2-07)
      - CI schema drift check
    """
    return LessonCreate.model_json_schema()


# Export the schema as a module-level constant for fast import.
LESSON_JSON_SCHEMA: dict[str, Any] = build_lesson_json_schema()


if __name__ == "__main__":
    # python -m app.modules.lessons.lesson_schema_v1
    print(json.dumps(LESSON_JSON_SCHEMA, indent=2))
