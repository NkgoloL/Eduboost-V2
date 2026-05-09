"""
P1-01 — Canonical CAPS Diagnostic Item Schema
==============================================
Pydantic v2 models that define the source-of-truth item contract.

Every downstream consumer — the Alembic migration, the ORM model,
the LLM generator, the validator, and the seed script — imports from
here so the schema is defined in exactly one place.

Place this file at:  app/domain/item_schema.py
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ItemType(str, Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"


class SubjectCode(str, Enum):
    MATHEMATICS = "Mathematics"
    ENGLISH = "English"
    ISIZULU = "isiZulu"
    AFRIKAANS = "Afrikaans"
    LIFE_SKILLS = "Life Skills"
    NATURAL_SCIENCES = "Natural Sciences"


class Language(str, Enum):
    EN = "en"
    ZU = "zu"
    AF = "af"
    XH = "xh"


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


class DifficultyBand(str, Enum):
    """Human-friendly difficulty bands used during generation.
    Mapped to IRT b-parameter ranges at calibration time."""

    EASY = "easy"            # b < -1.0
    MODERATE = "moderate"   # -1.0 <= b < 0.0
    ON_LEVEL = "on_level"   # 0.0 <= b < +1.0
    CHALLENGING = "challenging"  # b >= +1.0


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class MCQOption(BaseModel):
    """A single MCQ distractor or correct option."""

    label: str = Field(..., description="Single letter: A, B, C, D …")
    text: str = Field(..., min_length=1, description="Option text shown to learner")

    @field_validator("label")
    @classmethod
    def label_must_be_single_uppercase(cls, v: str) -> str:
        if len(v) != 1 or not v.isupper():
            raise ValueError("label must be a single uppercase letter, e.g. 'A'")
        return v


class DistractorRationale(BaseModel):
    """Maps each wrong option label to the misconception it probes."""

    label: str = Field(..., description="Distractor option label, e.g. 'B'")
    rationale: str = Field(..., min_length=10, description="Why a learner might choose this wrong answer")
    misconception: str = Field(..., description="Short misconception tag, e.g. 'place_value_confusion'")


# ---------------------------------------------------------------------------
# Core item models
# ---------------------------------------------------------------------------


class ItemBase(BaseModel):
    """Fields shared by create, update, and read schemas."""

    # CAPS taxonomy
    caps_ref: str = Field(
        ...,
        description="Structured CAPS reference: Grade.SubjectCode.Term.TopicIdx.SubtopicIdx  e.g. 4.M.1.1.1",
        pattern=r"^\d+\.[A-Z]+\.\d+\.\d+(\.\d+)?$",
    )
    grade: int = Field(..., ge=0, le=12, description="Grade level (0=R, 1–12)")
    subject: SubjectCode
    term: int = Field(..., ge=1, le=4, description="CAPS term (1–4)")
    topic: str = Field(..., min_length=2, description="e.g. 'Whole Numbers'")
    subtopic: str = Field(..., min_length=2, description="e.g. 'Ordering and Comparing 4-digit Numbers'")
    skill: str = Field(..., min_length=2, description="e.g. 'place_value_ordering'")

    # Question content
    stem: str = Field(..., min_length=10, description="Question text — plain language, grade-appropriate, SA context")
    answer_key: str = Field(..., min_length=1, description="Single correct answer: option label (MCQ) or exact text")
    options: list[MCQOption] | None = Field(
        default=None,
        description="MCQ: list of options (min 4). None for non-MCQ types.",
    )
    explanation: str = Field(..., min_length=20, description="Why the answer is correct — written for the learner")
    distractor_rationale: list[DistractorRationale] | None = Field(
        default=None,
        description="MCQ: why each wrong option is tempting",
    )
    misconception_tags: list[str] = Field(
        default_factory=list,
        description="e.g. ['place_value_confusion', 'carries_error']",
    )

    # Item characteristics
    item_type: ItemType = Field(default=ItemType.MCQ)
    language: Language = Field(default=Language.EN)

    # IRT parameters (pre-calibration estimates; refined after live sessions)
    difficulty_b: float = Field(
        default=0.0,
        ge=-3.0,
        le=3.0,
        description="IRT b-parameter (difficulty): –3 to +3; 0 = average Grade 4",
    )
    discrimination_a: float = Field(
        default=1.0,
        ge=0.5,
        le=2.5,
        description="IRT a-parameter (discrimination): 0.5–2.5; 1.0 default pre-calibration",
    )
    guessing_c: float = Field(
        default=0.25,
        ge=0.0,
        le=0.35,
        description="IRT c-parameter (guessing probability): 0.0–0.35; 0.25 for 4-option MCQ",
    )

    # Exposure management
    max_exposure: int = Field(
        default=50,
        ge=1,
        description="Maximum times this item may be served before being rested",
    )

    # Provenance
    source: ItemSource = Field(default=ItemSource.LLM_GENERATED)
    safety_passed: bool = Field(
        default=False,
        description="True once AI safety check confirms no harmful content / PII",
    )
    difficulty_band: DifficultyBand = Field(
        default=DifficultyBand.ON_LEVEL,
        description="Human-friendly band used during generation; must match b-parameter",
    )

    @model_validator(mode="after")
    def validate_mcq_options(self) -> "ItemBase":
        if self.item_type == ItemType.MCQ:
            if not self.options or len(self.options) < 4:
                raise ValueError("MCQ items require at least 4 options")
            option_labels = {o.label for o in self.options}
            if self.answer_key not in option_labels:
                raise ValueError(
                    f"answer_key '{self.answer_key}' must match one of the option labels: {sorted(option_labels)}"
                )
        return self

    @field_validator("misconception_tags")
    @classmethod
    def tags_must_be_snake_case(cls, v: list[str]) -> list[str]:
        for tag in v:
            if " " in tag:
                raise ValueError(f"misconception tag '{tag}' must use underscores, not spaces")
        return v


class ItemCreate(ItemBase):
    """Schema accepted by the LLM generator and the seed importer.
    item_id is generated server-side; review fields start at defaults.
    """

    pass  # All required fields are in ItemBase


class ItemRead(ItemBase):
    """Schema returned by the item bank API (reviewer role only)."""

    item_id: UUID = Field(default_factory=uuid4)
    review_status: ReviewStatus = Field(default=ReviewStatus.DRAFT)
    reviewer_id: UUID | None = Field(default=None)
    reviewed_at: datetime | None = Field(default=None)
    exposure_count: int = Field(default=0, ge=0)
    quality_score: float | None = Field(default=None, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class ItemUpdate(BaseModel):
    """Partial update — used by the human review endpoint (P4-06)."""

    review_status: ReviewStatus | None = None
    reviewer_id: UUID | None = None
    reviewed_at: datetime | None = None
    quality_score: float | None = Field(default=None, ge=0.0, le=1.0)
    safety_passed: bool | None = None
    difficulty_b: float | None = Field(default=None, ge=-3.0, le=3.0)
    discrimination_a: float | None = Field(default=None, ge=0.5, le=2.5)
    guessing_c: float | None = Field(default=None, ge=0.0, le=0.35)
    max_exposure: int | None = Field(default=None, ge=1)
    misconception_tags: list[str] | None = None


# ---------------------------------------------------------------------------
# JSON Schema export helper
# ---------------------------------------------------------------------------


def export_json_schema(output_path: str | Path | None = None) -> dict[str, Any]:
    """
    Generate and optionally persist the canonical JSON Schema for ItemCreate.

    Usage (CI schema freeze check):
        python -c "from app.domain.item_schema import export_json_schema; export_json_schema('data/caps/item_schema.json')"
    """
    schema = ItemCreate.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["title"] = "EduBoost CAPS Diagnostic Item"
    schema["description"] = (
        "Canonical schema for a CAPS-aligned diagnostic item. "
        "All generated, imported, and human-authored items must conform to this schema. "
        "Schema version: 1.0.0 — frozen at P1-01."
    )
    schema["version"] = "1.0.0"

    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(schema, fh, indent=2, ensure_ascii=False)
        print(f"[item_schema] JSON Schema written to {output_path}")

    return schema


if __name__ == "__main__":
    # Quick smoke-test: run `python app/domain/item_schema.py`
    schema = export_json_schema("data/caps/item_schema.json")
    print(json.dumps(schema, indent=2))
