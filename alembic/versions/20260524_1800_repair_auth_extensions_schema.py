"""repair auth extension schema drift

Revision ID: 20260524_1800
Revises: 20260523_0000
Create Date: 2026-05-24

Production may have been stamped at the auth-extension head before all objects
were present. This additive repair migration makes the expected objects exist
without dropping data.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260524_1800"
down_revision = "20260523_0000"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def _tables() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _indexes(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return set()
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    tokenpurpose = postgresql.ENUM(
        "password_reset",
        "email_verify",
        name="tokenpurpose",
        create_type=False,
    )
    tokenpurpose.create(op.get_bind(), checkfirst=True)

    tables = _tables()

    if "email_verified" not in _columns("guardians"):
        op.add_column(
            "guardians",
            sa.Column(
                "email_verified",
                sa.Boolean,
                server_default=sa.text("false"),
                nullable=False,
            ),
        )

    if "secure_tokens" not in tables:
        op.create_table(
            "secure_tokens",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column(
                "user_id",
                sa.String(36),
                sa.ForeignKey("guardians.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "purpose",
                tokenpurpose,
                nullable=False,
            ),
            sa.Column("token_hash", sa.String(256), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )

    secure_indexes = _indexes("secure_tokens")
    if "ix_secure_tokens_user_purpose" not in secure_indexes:
        op.create_index("ix_secure_tokens_user_purpose", "secure_tokens", ["user_id", "purpose"])
    if "ix_secure_tokens_expires_at" not in secure_indexes:
        op.create_index("ix_secure_tokens_expires_at", "secure_tokens", ["expires_at"])

    tables = _tables()
    if "onboarding_states" not in tables:
        op.create_table(
            "onboarding_states",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("user_id", sa.String(36), sa.ForeignKey("guardians.id", ondelete="CASCADE"), unique=True, nullable=False),
            sa.Column("email_verified", sa.Boolean, nullable=True),
            sa.Column("profile_complete", sa.Boolean, nullable=True),
            sa.Column("guardian_consent", sa.Boolean, nullable=True),
            sa.Column("diagnostic_done", sa.Boolean, nullable=True),
            sa.Column("plan_accepted", sa.Boolean, nullable=True),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )

    if "privacy_settings" not in tables:
        op.create_table(
            "privacy_settings",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("user_id", sa.String(36), sa.ForeignKey("guardians.id", ondelete="CASCADE"), unique=True, nullable=False),
            sa.Column("analytics_enabled", sa.Boolean, server_default=sa.text("true"), nullable=False),
            sa.Column("ai_improvement", sa.Boolean, server_default=sa.text("true"), nullable=False),
            sa.Column("marketing_emails", sa.Boolean, server_default=sa.text("false"), nullable=False),
            sa.Column("data_retention_days", sa.Integer, server_default=sa.text("365"), nullable=False),
            sa.Column("show_leaderboard", sa.Boolean, server_default=sa.text("true"), nullable=False),
            sa.Column("export_requested_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("deletion_requested_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )


def downgrade() -> None:
    # Additive drift repair only. Do not drop production data on downgrade.
    pass
