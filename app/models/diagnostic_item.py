"""
P1-04 + P1-05 — SQLAlchemy ORM models
======================================
P1-04 → DiagnosticItem  (app/models/diagnostic_item.py)
P1-05 → ItemExposure    (app/models/item_exposure.py)

Both models follow the existing EduBoost V2 ORM patterns:
  • Centralised import in app/models/__init__.py (add both entries there)
  • Async-compatible (used with SQLAlchemy async session from app/core/database.py)
  • Enums mirror app/domain/item_schema.py — single source of truth
  • Timestamps use server_default=func.now() consistent with existing models

Place these files at:
    app/models/diagnostic_item.py
    app/models/item_exposure.py

Then add to app/models/__init__.py:
    from app.models.diagnostic_item import DiagnosticItem
    from app.models.item_exposure import ItemExposure
"""

# =============================================================================
# app/models/diagnostic_item.py
# =============================================================================

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Import Base from the project's shared declarative base
# (app/core/database.py exports `Base = declarative_base()`)
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.item_exposure import ItemExposure


# ---------------------------------------------------------------------------
# Enum mirrors — keep in sync with app/domain/item_schema.py
# ---------------------------------------------------------------------------

class ItemTypeEnum(str, enum.Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"


class SubjectCodeEnum(str, enum.Enum):
    MATHEMATICS = "Mathematics"
    ENGLISH = "English"
    ISIZULU = "isiZulu"
    AFRIKAANS = "Afrikaans"
    LIFE_SKILLS = "Life Skills"
    NATURAL_SCIENCES = "Natural Sciences"


class LanguageEnum(str, enum.Enum):
    EN = "en"
    ZU = "zu"
    AF = "af"
    XH = "xh"


class ReviewStatusEnum(str, enum.Enum):
    DRAFT = "draft"
    AI_GENERATED = "ai_generated"
    HUMAN_REVIEWED = "human_reviewed"
    APPROVED = "approved"
    RETIRED = "retired"


class ItemSourceEnum(str, enum.Enum):
    LLM_GENERATED = "llm_generated"
    HUMAN_AUTHORED = "human_authored"
    IMPORTED = "imported"


class DifficultyBandEnum(str, enum.Enum):
    EASY = "easy"
    MODERATE = "moderate"
    ON_LEVEL = "on_level"
    CHALLENGING = "challenging"


# ---------------------------------------------------------------------------
# DiagnosticItem ORM model
# ---------------------------------------------------------------------------

class DiagnosticItem(Base):
    """
    ORM representation of the diagnostic_items table.

    This is the canonical item bank model.  Every column maps 1-to-1 with
    migration 0009.  Do not add business logic here — use the service layer.
    """

    __tablename__ = "diagnostic_items"
    __table_args__ = (
        CheckConstraint("grade >= 0 AND grade <= 12", name="ck_diagnostic_items_grade_range"),
        CheckConstraint("term >= 1 AND term <= 4", name="ck_diagnostic_items_term_range"),
        CheckConstraint(
            "difficulty_b >= -3.0 AND difficulty_b <= 3.0",
            name="ck_diagnostic_items_difficulty_b_range",
        ),
        CheckConstraint(
            "discrimination_a >= 0.5 AND discrimination_a <= 2.5",
            name="ck_diagnostic_items_discrimination_a_range",
        ),
        CheckConstraint(
            "guessing_c >= 0.0 AND guessing_c <= 0.35",
            name="ck_diagnostic_items_guessing_c_range",
        ),
        CheckConstraint(
            "quality_score IS NULL OR (quality_score >= 0.0 AND quality_score <= 1.0)",
            name="ck_diagnostic_items_quality_score_range",
        ),
        CheckConstraint(
            "exposure_count >= 0 AND max_exposure >= 1",
            name="ck_diagnostic_items_exposure_non_negative",
        ),
        CheckConstraint(
            "(review_status NOT IN ('human_reviewed', 'approved')) OR (reviewer_id IS NOT NULL)",
            name="ck_diagnostic_items_reviewer_consistency",
        ),
    )

    # --- Identity --------------------------------------------------------
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    # --- CAPS taxonomy ---------------------------------------------------
    caps_ref: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    grade: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    subject: Mapped[SubjectCodeEnum] = mapped_column(
        Enum(SubjectCodeEnum, name="subjectcode", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    term: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    subtopic: Mapped[str] = mapped_column(String(200), nullable=False)
    skill: Mapped[str] = mapped_column(String(200), nullable=False)

    # --- Question content ------------------------------------------------
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    answer_key: Mapped[str] = mapped_column(String(500), nullable=False)
    options: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    distractor_rationale: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    misconception_tags: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default="{}"
    )

    # --- Item characteristics --------------------------------------------
    item_type: Mapped[ItemTypeEnum] = mapped_column(
        Enum(ItemTypeEnum, name="itemtype", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default="mcq",
    )
    language: Mapped[LanguageEnum] = mapped_column(
        Enum(LanguageEnum, name="language", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default="en",
    )

    # --- IRT parameters --------------------------------------------------
    difficulty_b: Mapped[float] = mapped_column(
        Numeric(precision=6, scale=4), nullable=False, server_default="0.0"
    )
    discrimination_a: Mapped[float] = mapped_column(
        Numeric(precision=6, scale=4), nullable=False, server_default="1.0"
    )
    guessing_c: Mapped[float] = mapped_column(
        Numeric(precision=6, scale=4), nullable=False, server_default="0.25"
    )
    difficulty_band: Mapped[DifficultyBandEnum] = mapped_column(
        Enum(DifficultyBandEnum, name="difficultyband", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default="on_level",
    )

    # --- Review workflow -------------------------------------------------
    review_status: Mapped[ReviewStatusEnum] = mapped_column(
        Enum(ReviewStatusEnum, name="reviewstatus", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default="draft",
        index=True,
    )
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Exposure management ---------------------------------------------
    exposure_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    max_exposure: Mapped[int] = mapped_column(Integer, nullable=False, server_default="50")

    # --- Quality & safety ------------------------------------------------
    quality_score: Mapped[float | None] = mapped_column(
        Numeric(precision=5, scale=4), nullable=True
    )
    safety_passed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    # --- Provenance ------------------------------------------------------
    source: Mapped[ItemSourceEnum] = mapped_column(
        Enum(ItemSourceEnum, name="itemsource", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default="llm_generated",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # --- Relationships ---------------------------------------------------
    exposures: Mapped[list["ItemExposure"]] = relationship(
        "ItemExposure",
        back_populates="item",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # --- Helpers ---------------------------------------------------------
    @property
    def is_available_for_selection(self) -> bool:
        """True if this item can be served: approved and below exposure cap."""
        return (
            self.review_status == ReviewStatusEnum.APPROVED
            and self.exposure_count < self.max_exposure
        )

    @property
    def is_approved(self) -> bool:
        return self.review_status == ReviewStatusEnum.APPROVED

    def __repr__(self) -> str:
        return (
            f"<DiagnosticItem item_id={self.item_id!s:.8} "
            f"caps_ref={self.caps_ref!r} "
            f"status={self.review_status.value!r}>"
        )

