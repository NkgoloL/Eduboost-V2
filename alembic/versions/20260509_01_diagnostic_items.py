"""
P1-02 — Alembic migration 0009: diagnostic_items table
=======================================================
Place this file at:
    alembic/versions/0009_add_diagnostic_items_table.py

Depends on: 0008 (lesson completion tracking — the current head).

Run:
    alembic upgrade head          # applies this migration
    alembic downgrade -1          # rolls back this migration

Rollback notes:
    This migration only adds new tables and indexes; it makes no changes to
    existing tables.  Downgrade is safe at any point before items are seeded.
    Once items are seeded (P3-12), take a snapshot before downgrading.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# ---------------------------------------------------------------------------
# Revision identifiers — used by Alembic
# ---------------------------------------------------------------------------
revision = "20260509_01"
down_revision = "20260507_1500"
branch_labels = None
depends_on = None

# ---------------------------------------------------------------------------
# Enum type names (must match app/domain/item_schema.py)
# ---------------------------------------------------------------------------
_ITEM_TYPE_ENUM = postgresql.ENUM(
    "mcq", "short_answer", "true_false", "fill_blank",
    name="itemtype",
    create_type=False,
)
_SUBJECT_CODE_ENUM = postgresql.ENUM(
    "Mathematics", "English", "isiZulu", "Afrikaans", "Life Skills", "Natural Sciences",
    name="subjectcode",
    create_type=False,
)
_LANGUAGE_ENUM = postgresql.ENUM(
    "en", "zu", "af", "xh",
    name="language",
    create_type=False,
)
_REVIEW_STATUS_ENUM = postgresql.ENUM(
    "draft", "ai_generated", "human_reviewed", "approved", "retired",
    name="reviewstatus",
    create_type=False,
)
_ITEM_SOURCE_ENUM = postgresql.ENUM(
    "llm_generated", "human_authored", "imported",
    name="itemsource",
    create_type=False,
)
_DIFFICULTY_BAND_ENUM = postgresql.ENUM(
    "easy", "moderate", "on_level", "challenging",
    name="difficultyband",
    create_type=False,
)


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Create enum types (CREATE TYPE … IF NOT EXISTS via checkfirst)
    # ------------------------------------------------------------------
    for enum in (
        _ITEM_TYPE_ENUM,
        _SUBJECT_CODE_ENUM,
        _LANGUAGE_ENUM,
        _REVIEW_STATUS_ENUM,
        _ITEM_SOURCE_ENUM,
        _DIFFICULTY_BAND_ENUM,
    ):
        enum.create(op.get_bind(), checkfirst=True)

    # ------------------------------------------------------------------
    # 2. diagnostic_items — the canonical item bank table
    # ------------------------------------------------------------------
    op.create_table(
        "diagnostic_items",

        # --- Identity --------------------------------------------------
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            comment="Stable identifier — never reassigned, never reused after retirement",
        ),

        # --- CAPS taxonomy --------------------------------------------
        sa.Column(
            "caps_ref",
            sa.String(40),
            nullable=False,
            comment="Structured CAPS reference, e.g. 4.M.1.1.1",
        ),
        sa.Column("grade", sa.SmallInteger, nullable=False),
        sa.Column(
            "subject",
            postgresql.ENUM(
                "Mathematics", "English", "isiZulu", "Afrikaans",
                "Life Skills", "Natural Sciences",
                name="subjectcode", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("term", sa.SmallInteger, nullable=False),
        sa.Column("topic", sa.String(200), nullable=False),
        sa.Column("subtopic", sa.String(200), nullable=False),
        sa.Column("skill", sa.String(200), nullable=False),

        # --- Question content -----------------------------------------
        sa.Column("stem", sa.Text, nullable=False),
        sa.Column("answer_key", sa.String(500), nullable=False),
        sa.Column(
            "options",
            postgresql.JSONB,
            nullable=True,
            comment="[{label, text}] for MCQ; NULL for other types",
        ),
        sa.Column("explanation", sa.Text, nullable=False),
        sa.Column(
            "distractor_rationale",
            postgresql.JSONB,
            nullable=True,
            comment="[{label, rationale, misconception}] for MCQ; NULL otherwise",
        ),
        sa.Column(
            "misconception_tags",
            postgresql.ARRAY(sa.Text),
            nullable=False,
            server_default="{}",
        ),

        # --- Item characteristics -------------------------------------
        sa.Column(
            "item_type",
            postgresql.ENUM(
                "mcq", "short_answer", "true_false", "fill_blank",
                name="itemtype", create_type=False,
            ),
            nullable=False,
            server_default="mcq",
        ),
        sa.Column(
            "language",
            postgresql.ENUM("en", "zu", "af", "xh", name="language", create_type=False),
            nullable=False,
            server_default="en",
        ),

        # --- IRT parameters -------------------------------------------
        sa.Column(
            "difficulty_b",
            sa.Numeric(precision=6, scale=4),
            nullable=False,
            server_default="0.0",
            comment="IRT b-param (difficulty): –3.0 to +3.0",
        ),
        sa.Column(
            "discrimination_a",
            sa.Numeric(precision=6, scale=4),
            nullable=False,
            server_default="1.0",
            comment="IRT a-param (discrimination): 0.5 to 2.5",
        ),
        sa.Column(
            "guessing_c",
            sa.Numeric(precision=6, scale=4),
            nullable=False,
            server_default="0.25",
            comment="IRT c-param (guessing): 0.0 to 0.35",
        ),
        sa.Column(
            "difficulty_band",
            postgresql.ENUM(
                "easy", "moderate", "on_level", "challenging",
                name="difficultyband", create_type=False,
            ),
            nullable=False,
            server_default="on_level",
        ),

        # --- Review workflow ------------------------------------------
        sa.Column(
            "review_status",
            postgresql.ENUM(
                "draft", "ai_generated", "human_reviewed", "approved", "retired",
                name="reviewstatus", create_type=False,
            ),
            nullable=False,
            server_default="draft",
        ),
        sa.Column(
            "reviewer_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment="FK to guardians(id) for the reviewer; NULL until reviewed",
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),

        # --- Exposure management --------------------------------------
        sa.Column(
            "exposure_count",
            sa.Integer,
            nullable=False,
            server_default="0",
            comment="Total times served across all sessions",
        ),
        sa.Column(
            "max_exposure",
            sa.Integer,
            nullable=False,
            server_default="50",
            comment="Cap on exposures; item excluded from selection once reached",
        ),

        # --- Quality & safety -----------------------------------------
        sa.Column(
            "quality_score",
            sa.Numeric(precision=5, scale=4),
            nullable=True,
            comment="0.0–1.0 composite quality score; NULL until reviewed",
        ),
        sa.Column(
            "safety_passed",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="True once AI safety check passed",
        ),

        # --- Provenance -----------------------------------------------
        sa.Column(
            "source",
            postgresql.ENUM(
                "llm_generated", "human_authored", "imported",
                name="itemsource", create_type=False,
            ),
            nullable=False,
            server_default="llm_generated",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
        ),
    )

    # ------------------------------------------------------------------
    # 3. Constraints on diagnostic_items
    # ------------------------------------------------------------------
    # IRT bounds enforced at DB level (belt-and-suspenders with Pydantic)
    op.create_check_constraint(
        "ck_diagnostic_items_grade_range",
        "diagnostic_items",
        "grade >= 0 AND grade <= 12",
    )
    op.create_check_constraint(
        "ck_diagnostic_items_term_range",
        "diagnostic_items",
        "term >= 1 AND term <= 4",
    )
    op.create_check_constraint(
        "ck_diagnostic_items_difficulty_b_range",
        "diagnostic_items",
        "difficulty_b >= -3.0 AND difficulty_b <= 3.0",
    )
    op.create_check_constraint(
        "ck_diagnostic_items_discrimination_a_range",
        "diagnostic_items",
        "discrimination_a >= 0.5 AND discrimination_a <= 2.5",
    )
    op.create_check_constraint(
        "ck_diagnostic_items_guessing_c_range",
        "diagnostic_items",
        "guessing_c >= 0.0 AND guessing_c <= 0.35",
    )
    op.create_check_constraint(
        "ck_diagnostic_items_quality_score_range",
        "diagnostic_items",
        "quality_score IS NULL OR (quality_score >= 0.0 AND quality_score <= 1.0)",
    )
    op.create_check_constraint(
        "ck_diagnostic_items_exposure_non_negative",
        "diagnostic_items",
        "exposure_count >= 0 AND max_exposure >= 1",
    )
    op.create_check_constraint(
        "ck_diagnostic_items_reviewer_consistency",
        "diagnostic_items",
        # reviewer_id must be set when review_status is human_reviewed or approved
        "(review_status NOT IN ('human_reviewed', 'approved')) OR (reviewer_id IS NOT NULL)",
    )

    # ------------------------------------------------------------------
    # 4. Indexes on diagnostic_items
    # ------------------------------------------------------------------
    # Primary lookup: item bank queries by CAPS ref + review status
    op.create_index(
        "ix_diagnostic_items_caps_ref",
        "diagnostic_items",
        ["caps_ref"],
    )
    op.create_index(
        "ix_diagnostic_items_review_status",
        "diagnostic_items",
        ["review_status"],
    )
    # IRT engine selection: approved items for a given grade/subject/term
    op.create_index(
        "ix_diagnostic_items_grade_subject_term",
        "diagnostic_items",
        ["grade", "subject", "term"],
    )
    # Exposure cap enforcement: items not yet at max_exposure
    op.create_index(
        "ix_diagnostic_items_exposure_cap",
        "diagnostic_items",
        ["exposure_count", "max_exposure"],
    )
    # Coverage dashboard: approved items per caps_ref
    op.create_index(
        "ix_diagnostic_items_caps_ref_approved",
        "diagnostic_items",
        ["caps_ref", "review_status"],
        postgresql_where=sa.text("review_status = 'approved'"),
    )
    # IRT engine: select approved, unexposed items ordered by difficulty
    op.create_index(
        "ix_diagnostic_items_irt_selection",
        "diagnostic_items",
        ["caps_ref", "difficulty_b"],
        postgresql_where=sa.text("review_status = 'approved' AND exposure_count < max_exposure"),
    )


def downgrade() -> None:
    # Drop indexes first
    for idx in (
        "ix_diagnostic_items_irt_selection",
        "ix_diagnostic_items_caps_ref_approved",
        "ix_diagnostic_items_exposure_cap",
        "ix_diagnostic_items_grade_subject_term",
        "ix_diagnostic_items_review_status",
        "ix_diagnostic_items_caps_ref",
    ):
        op.drop_index(idx, table_name="diagnostic_items")

    # Drop constraints
    for ck in (
        "ck_diagnostic_items_reviewer_consistency",
        "ck_diagnostic_items_exposure_non_negative",
        "ck_diagnostic_items_quality_score_range",
        "ck_diagnostic_items_guessing_c_range",
        "ck_diagnostic_items_discrimination_a_range",
        "ck_diagnostic_items_difficulty_b_range",
        "ck_diagnostic_items_term_range",
        "ck_diagnostic_items_grade_range",
    ):
        op.drop_constraint(ck, "diagnostic_items")

    op.drop_table("diagnostic_items")

    # Drop enum types only if no other table references them
    for enum in (
        _DIFFICULTY_BAND_ENUM,
        _ITEM_SOURCE_ENUM,
        _REVIEW_STATUS_ENUM,
        _LANGUAGE_ENUM,
        _SUBJECT_CODE_ENUM,
        _ITEM_TYPE_ENUM,
    ):
        enum.drop(op.get_bind(), checkfirst=True)
