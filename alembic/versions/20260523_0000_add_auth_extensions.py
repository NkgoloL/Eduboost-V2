"""add_auth_extensions

Revision ID: 20260523_0000
Revises: <SET_TO_YOUR_LATEST_REVISION>
Create Date: 2026-05-23

Adds:
    secure_tokens        — one-use bcrypt-hashed tokens (password-reset, email-verify)
    onboarding_states    — per-user 5-step onboarding progress
    privacy_settings     — POPIA-aligned per-user data preferences
    users.email_verified — boolean column on existing users table

Before running:
    1. Replace down_revision below with the output of:  alembic current
    2. Run:  alembic upgrade 3f8a2c1d9e04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision      = "20260523_0000"
down_revision = "20260516_0100"
branch_labels = None
depends_on    = None


def upgrade() -> None:
    # ── tokenpurpose enum ─────────────────────────────────────────────────────
    tokenpurpose = postgresql.ENUM(
        "password_reset", "email_verify",
        name="tokenpurpose",
        create_type=False,
    )
    tokenpurpose.create(op.get_bind(), checkfirst=True)

    # ── secure_tokens ─────────────────────────────────────────────────────────
    op.create_table(
        "secure_tokens",
        sa.Column("id",         sa.Integer,                  primary_key=True),
        sa.Column(
            "user_id", sa.String(36),
            sa.ForeignKey("guardians.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "purpose",
            tokenpurpose,
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(256),               nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True),   nullable=False),
        sa.Column("used_at",    sa.DateTime(timezone=True),   nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
    )
    op.create_index(
        "ix_secure_tokens_user_purpose", "secure_tokens", ["user_id", "purpose"]
    )
    op.create_index(
        "ix_secure_tokens_expires_at", "secure_tokens", ["expires_at"]
    )

    # ── onboarding_states ─────────────────────────────────────────────────────
    op.create_table(
        "onboarding_states",
        sa.Column("id",      sa.Integer, primary_key=True),
        sa.Column(
            "user_id", sa.String(36),
            sa.ForeignKey("guardians.id", ondelete="CASCADE"),
            unique=True, nullable=False,
        ),
        sa.Column("email_verified",   sa.Boolean, nullable=True),
        sa.Column("profile_complete", sa.Boolean, nullable=True),
        sa.Column("guardian_consent", sa.Boolean, nullable=True),
        sa.Column("diagnostic_done",  sa.Boolean, nullable=True),
        sa.Column("plan_accepted",    sa.Boolean, nullable=True),
        sa.Column("completed_at",     sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
    )

    # ── privacy_settings ──────────────────────────────────────────────────────
    op.create_table(
        "privacy_settings",
        sa.Column("id",      sa.Integer, primary_key=True),
        sa.Column(
            "user_id", sa.String(36),
            sa.ForeignKey("guardians.id", ondelete="CASCADE"),
            unique=True, nullable=False,
        ),
        sa.Column(
            "analytics_enabled", sa.Boolean,
            server_default=sa.text("true"),  nullable=False,
        ),
        sa.Column(
            "ai_improvement", sa.Boolean,
            server_default=sa.text("true"),  nullable=False,
        ),
        sa.Column(
            "marketing_emails", sa.Boolean,
            server_default=sa.text("false"), nullable=False,
        ),
        sa.Column(
            "data_retention_days", sa.Integer,
            server_default=sa.text("365"),   nullable=False,
        ),
        sa.Column(
            "show_leaderboard", sa.Boolean,
            server_default=sa.text("true"),  nullable=False,
        ),
        sa.Column("export_requested_at",   sa.DateTime(timezone=True), nullable=True),
        sa.Column("deletion_requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
    )

    # ── email_verified on guardians ───────────────────────────────────────────────
    op.add_column(
        "guardians",
        sa.Column(
            "email_verified", sa.Boolean,
            server_default=sa.text("false"), nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("guardians", "email_verified")
    op.drop_table("privacy_settings")
    op.drop_table("onboarding_states")
    op.drop_index("ix_secure_tokens_expires_at",   "secure_tokens")
    op.drop_index("ix_secure_tokens_user_purpose", "secure_tokens")
    op.drop_table("secure_tokens")
    op.execute("DROP TYPE IF EXISTS tokenpurpose")
