"""add missing production indexes and partial indexes

Revision ID: 771fb3ac38b8
Revises: 0008_lesson_completion_tracking
Create Date: 2026-05-05 19:33:18.069461
"""
from alembic import op
import sqlalchemy as sa


revision = '771fb3ac38b8'
down_revision = '0008_lesson_completion_tracking'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Guarding against existing indexes ──────────────────────────────────────────
    # Standard indexes for performance on lookups and sorting
    op.create_index("ix_guardians_created_at", "guardians", ["created_at"])
    op.create_index("ix_learner_profiles_created_at", "learner_profiles", ["created_at"])
    op.create_index("ix_learner_profiles_last_active", "learner_profiles", ["last_active"])
    op.create_index("ix_lessons_created_at", "lessons", ["created_at"])
    op.create_index("ix_knowledge_gaps_created_at", "knowledge_gaps", ["created_at"])
    
    # Partial index for active consents (high-frequency query in every learner-scoped request)
    # We use a literal SQL condition for Postgres compatibility
    op.create_index(
        "ix_active_parental_consents",
        "parental_consents",
        ["learner_id"],
        postgresql_where=sa.text("revoked_at IS NULL AND expires_at > CURRENT_TIMESTAMP")
    )


def downgrade() -> None:
    op.drop_index("ix_active_parental_consents", "parental_consents")
    op.drop_index("ix_knowledge_gaps_created_at", "knowledge_gaps")
    op.drop_index("ix_lessons_created_at", "lessons")
    op.drop_index("ix_learner_profiles_last_active", "learner_profiles")
    op.drop_index("ix_learner_profiles_created_at", "learner_profiles")
    op.drop_index("ix_guardians_created_at", "guardians")
