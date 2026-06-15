"""Phase 6 durable AI operations accounting.

Revision ID: 20260615_1500_p6_ai_ops
Revises: 20260615_1200_p5_tutor
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260615_1500_p6_ai_ops"
down_revision = "20260615_1200_p5_tutor"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_budget_counters",
        sa.Column("scope_type", sa.String(16), primary_key=True),
        sa.Column("scope_id", sa.String(128), primary_key=True),
        sa.Column("period_key", sa.String(16), primary_key=True),
        sa.Column("used_tokens", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("reserved_tokens", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("used_cost_usd", sa.Numeric(18, 8), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("scope_type IN ('user','tenant','global')", name="ck_ai_budget_counter_scope_type"),
        sa.CheckConstraint("used_tokens >= 0 AND reserved_tokens >= 0", name="ck_ai_budget_counter_tokens_nonnegative"),
        sa.CheckConstraint("used_cost_usd >= 0", name="ck_ai_budget_counter_cost_nonnegative"),
    )
    op.create_index("ix_ai_budget_counters_period", "ai_budget_counters", ["period_key", "scope_type"])

    op.create_table(
        "ai_usage_reservations",
        sa.Column("reservation_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("operation_id", sa.String(160), nullable=False, unique=True),
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("purpose", sa.String(64), nullable=False),
        sa.Column("estimated_tokens", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("failure_reason", sa.String(96), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("reserved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("estimated_tokens > 0", name="ck_ai_usage_reservation_estimate_positive"),
        sa.CheckConstraint("status IN ('pending','finalized','cancelled','expired')", name="ck_ai_usage_reservation_status"),
    )
    op.create_index("ix_ai_usage_reservations_status_expires", "ai_usage_reservations", ["status", "expires_at"])
    op.create_index("ix_ai_usage_reservations_tenant_created", "ai_usage_reservations", ["tenant_id", "reserved_at"])

    op.create_table(
        "ai_usage_events",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("reservation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_usage_reservations.reservation_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("operation_id", sa.String(160), nullable=False, unique=True),
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("purpose", sa.String(64), nullable=False),
        sa.Column("provider", sa.String(48), nullable=False),
        sa.Column("model", sa.String(128), nullable=False),
        sa.Column("prompt_tokens", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.BigInteger(), nullable=False),
        sa.Column("estimated_cost_usd", sa.Numeric(18, 8), nullable=False, server_default="0"),
        sa.Column("outcome", sa.String(24), nullable=False, server_default="success"),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("prompt_tokens >= 0 AND completion_tokens >= 0 AND total_tokens >= 0", name="ck_ai_usage_event_tokens"),
        sa.CheckConstraint("estimated_cost_usd >= 0", name="ck_ai_usage_event_cost"),
        sa.CheckConstraint("outcome IN ('success','fallback','blocked','error')", name="ck_ai_usage_event_outcome"),
        sa.UniqueConstraint("reservation_id", name="uq_ai_usage_event_reservation"),
    )
    op.create_index("ix_ai_usage_events_tenant_created", "ai_usage_events", ["tenant_id", "created_at"])
    op.create_index("ix_ai_usage_events_provider_created", "ai_usage_events", ["provider", "created_at"])
    op.create_index("ix_ai_usage_events_purpose_created", "ai_usage_events", ["purpose", "created_at"])

    op.execute("""
    CREATE OR REPLACE FUNCTION prevent_ai_usage_event_mutation()
    RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      RAISE EXCEPTION 'ai_usage_events is append-only';
    END;
    $$;
    """)
    op.execute("""
    CREATE TRIGGER trg_ai_usage_events_append_only
    BEFORE UPDATE OR DELETE ON ai_usage_events
    FOR EACH ROW EXECUTE FUNCTION prevent_ai_usage_event_mutation();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_ai_usage_events_append_only ON ai_usage_events")
    op.execute("DROP FUNCTION IF EXISTS prevent_ai_usage_event_mutation()")
    op.drop_table("ai_usage_events")
    op.drop_table("ai_usage_reservations")
    op.drop_table("ai_budget_counters")
