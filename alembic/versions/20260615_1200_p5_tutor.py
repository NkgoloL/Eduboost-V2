"""Phase 5 safe learner tutor sessions, messages, and escalations.

Revision ID: 20260615_1200_p5_tutor
Revises: 20260615_0900_p4_irt_quality
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260615_1200_p5_tutor"
down_revision = "20260615_0900_p4_irt_quality"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tutor_sessions",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("learner_id", sa.String(36), sa.ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lesson_id", sa.String(36), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by", sa.String(80), nullable=False),
        sa.Column("language", sa.String(8), nullable=False, server_default="en"),
        sa.Column("status", sa.String(24), nullable=False, server_default="active"),
        sa.Column("context_hash", sa.String(64), nullable=False),
        sa.Column("message_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("escalation_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('active','cancelled','escalated','closed')", name="ck_tutor_sessions_status"),
        sa.CheckConstraint("message_count >= 0", name="ck_tutor_sessions_message_count"),
        sa.CheckConstraint("escalation_count >= 0", name="ck_tutor_sessions_escalation_count"),
    )
    op.create_index("ix_tutor_sessions_learner_activity", "tutor_sessions", ["learner_id", "last_activity_at"])
    op.create_index("ix_tutor_sessions_lesson", "tutor_sessions", ["lesson_id"])
    op.create_index(
        "uq_tutor_sessions_active_lesson",
        "tutor_sessions",
        ["learner_id", "lesson_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "tutor_messages",
        sa.Column("message_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tutor_sessions.session_id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_message_id", sa.String(80), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("pii_redacted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("safety_status", sa.String(24), nullable=False, server_default="safe"),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("provider", sa.String(40), nullable=True),
        sa.Column("model", sa.String(120), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("session_id", "client_message_id", "role", name="uq_tutor_message_session_client_role"),
        sa.CheckConstraint("role IN ('learner','assistant','system')", name="ck_tutor_messages_role"),
        sa.CheckConstraint("safety_status IN ('safe','redacted','blocked','fallback','escalated')", name="ck_tutor_messages_safety"),
        sa.CheckConstraint("quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1)", name="ck_tutor_messages_quality"),
        sa.CheckConstraint("prompt_tokens >= 0 AND completion_tokens >= 0", name="ck_tutor_messages_tokens"),
    )
    op.create_index("ix_tutor_messages_session_created", "tutor_messages", ["session_id", "created_at"])

    op.create_table(
        "tutor_escalations",
        sa.Column("escalation_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tutor_sessions.session_id", ondelete="CASCADE"), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tutor_messages.message_id", ondelete="SET NULL"), nullable=True),
        sa.Column("reason_code", sa.String(48), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("summary", sa.String(500), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="open"),
        sa.Column("assigned_to", sa.String(80), nullable=True),
        sa.Column("resolution", sa.Text(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("severity IN ('low','medium','high','critical')", name="ck_tutor_escalations_severity"),
        sa.CheckConstraint("status IN ('open','acknowledged','resolved','dismissed')", name="ck_tutor_escalations_status"),
    )
    op.create_index("ix_tutor_escalations_status_created", "tutor_escalations", ["status", "created_at"])
    op.create_index("ix_tutor_escalations_session", "tutor_escalations", ["session_id"])

    op.execute("""
    CREATE OR REPLACE FUNCTION prevent_tutor_message_mutation()
    RETURNS trigger AS $$
    BEGIN
      RAISE EXCEPTION 'tutor_messages is immutable after insert';
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_tutor_messages_append_only
    BEFORE UPDATE ON tutor_messages
    FOR EACH ROW EXECUTE FUNCTION prevent_tutor_message_mutation();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_tutor_messages_append_only ON tutor_messages")
    op.execute("DROP FUNCTION IF EXISTS prevent_tutor_message_mutation()")
    op.drop_index("ix_tutor_escalations_session", table_name="tutor_escalations")
    op.drop_index("ix_tutor_escalations_status_created", table_name="tutor_escalations")
    op.drop_table("tutor_escalations")
    op.drop_index("ix_tutor_messages_session_created", table_name="tutor_messages")
    op.drop_table("tutor_messages")
    op.drop_index("uq_tutor_sessions_active_lesson", table_name="tutor_sessions")
    op.drop_index("ix_tutor_sessions_lesson", table_name="tutor_sessions")
    op.drop_index("ix_tutor_sessions_learner_activity", table_name="tutor_sessions")
    op.drop_table("tutor_sessions")
