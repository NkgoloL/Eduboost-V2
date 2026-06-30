"""
Item Schema — app/domain/item_schema.py
=========================================
Canonical Pydantic v2 models for the CAPS diagnostic item bank.
This is the single source of truth for the item schema (P1-01).

All Phase 2 services import from here — any schema change must be made
here first and then re-validated against all generated items.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ItemType(str, Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"


class ReviewStatus(str, Enum):
    DRAFT = "draft"
    AI_GENERATED = "ai_generated"
    HUMAN_REVIEWED = "human_reviewed"
    APPROVED = "approved"
    RETIRED = "retired"


class ItemSource(str, Enum):
    LLM_GENERATED = "llm_generated"
    HUMAN_AUTHORED = "human_authored"
    IMPORTED = "imported"


class SubjectCode(str, Enum):
    MATHEMATICS = "Mathematics"
    ENGLISH = "English"
    ISIZULU = "isiZulu"
    AFRIKAANS = "Afrikaans"
    LIFE_SKILLS = "Life Skills"
    NATURAL_SCIENCES = "Natural Sciences"


class LanguageCode(str, Enum):
    EN = "en"
    ZU = "zu"
    AF = "af"
    XH = "xh"


# ---------------------------------------------------------------------------
# MCQ option model
# ---------------------------------------------------------------------------


class MCQOption(BaseModel):
    label: str = Field(..., pattern=r"^[A-E]$", description="Single uppercase letter")
    text: str = Field(..., min_length=1, max_length=500)

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Core item model
# ---------------------------------------------------------------------------


class ItemCreate(BaseModel):
    """
    Full item schema used for creation, validation, and seed file I/O.
    Matches the SQLAlchemy DiagnosticItem column set exactly.
    """

    # Identity
    item_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    caps_ref: str = Field(
        ...,
        pattern=r"^\d+\.[A-Z]+\.\d+\.\d+$",
        description="CAPS reference e.g. 4.M.1.1",
        examples=["4.M.1.1", "4.M.1.2"],
    )
    grade: int = Field(..., ge=0, le=7)
    subject: SubjectCode
    term: int = Field(..., ge=1, le=4)
    topic: str = Field(..., min_length=2, max_length=200)
    subtopic: str = Field(..., min_length=2, max_length=200)
    skill: str = Field(..., min_length=2, max_length=200)

    # Question content
    stem: str = Field(..., min_length=10, max_length=2000)
    answer_key: str = Field(..., min_length=1, max_length=50)
    options: list[dict[str, Any]] | None = Field(None, description="MCQ options [{label, text}]")
    explanation: str = Field(..., min_length=1, max_length=3000)
    distractor_rationale: dict[str, str] | None = Field(
        None,
        description="Maps wrong option label → misconception explanation",
    )
    misconception_tags: list[str] = Field(default_factory=list)

    # Classification
    item_type: ItemType = ItemType.MCQ
    language: LanguageCode = LanguageCode.EN

    # IRT parameters
    difficulty_b: float = Field(
        0.0,
        ge=-3.0,
        le=3.0,
        description="IRT b-parameter (difficulty)",
    )
    discrimination_a: float = Field(
        1.0,
        ge=0.5,
        le=2.5,
        description="IRT a-parameter (discrimination)",
    )
    guessing_c: float = Field(
        0.25,
        ge=0.0,
        le=0.35,
        description="IRT c-parameter (guessing)",
    )

    # Review workflow
    review_status: ReviewStatus = ReviewStatus.DRAFT
    reviewer_id: uuid.UUID | None = None
    reviewed_at: datetime | None = None

    # Exposure tracking
    exposure_count: int = Field(0, ge=0)
    max_exposure: int = Field(50, ge=1)

    # Metadata
    source: ItemSource = ItemSource.LLM_GENERATED
    quality_score: float | None = Field(None, ge=0.0, le=1.0)
    safety_passed: bool = False
    created_at: datetime | None = None

    model_config = {"from_attributes": True, "use_enum_values": True}

    @field_validator("options", mode="before")
    @classmethod
    def parse_options(cls, v):
        if v is None:
            return v
        if isinstance(v, list):
            return v
        raise ValueError("options must be a list of dicts or None")

    @model_validator(mode="after")
    def validate_mcq_has_options(self) -> "ItemCreate":
        if self.item_type == ItemType.MCQ and not self.options:
            raise ValueError("MCQ items must have at least one option")
        return self


class ItemResponse(ItemCreate):
    """Read-only response model — adds computed fields."""

    created_at: datetime

    @property
    def is_eligible(self) -> bool:
        """True if item can be served in a diagnostic session."""
        return (
            self.review_status == ReviewStatus.APPROVED
            and self.safety_passed
            and self.exposure_count < self.max_exposure
        )
