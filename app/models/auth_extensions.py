"""
auth_extensions.py — EduBoost SA V2
SQLAlchemy models for: password-reset tokens, email-verification tokens,
onboarding completion state, and per-user privacy controls (POPIA-aligned).

Place at:
    app/models/auth_extensions.py

Add to app/models/__init__.py:
    from app.models.auth_extensions import (
        SecureToken, OnboardingState, PrivacySettings, TokenPurpose
    )

Add these to the User model (app/models/user.py):
    from sqlalchemy import Boolean, Column
    from sqlalchemy.sql import expression

    email_verified   = Column(Boolean, server_default=expression.false(), nullable=False)
    secure_tokens    = relationship("SecureToken",     back_populates="user", cascade="all, delete-orphan")
    onboarding_state = relationship("OnboardingState", back_populates="user", uselist=False, cascade="all, delete-orphan")
    privacy_settings = relationship("PrivacySettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey,
    Index, Integer, String, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ─────────────────────────────────────────────────────────────────────────────
# Enum
# ─────────────────────────────────────────────────────────────────────────────

class TokenPurpose(str, enum.Enum):
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFY   = "email_verify"


# ─────────────────────────────────────────────────────────────────────────────
# SecureToken — one-use, expiring token (hash-only storage)
# ─────────────────────────────────────────────────────────────────────────────

class SecureToken(Base):
    """
    One-use, expiring token for password-reset and email-verification flows.
    Raw secrets are NEVER stored — callers hash with passlib before insert.
    Bcrypt verify provides timing-safe comparison at consumption time.
    """
    __tablename__ = "secure_tokens"
    __table_args__ = (
        Index("ix_secure_tokens_user_purpose", "user_id", "purpose"),
        Index("ix_secure_tokens_expires_at",   "expires_at"),
    )

    id:         Mapped[int]             = mapped_column(Integer, primary_key=True)
    user_id:    Mapped[str]             = mapped_column(
        String(36), ForeignKey("guardians.id", ondelete="CASCADE"), nullable=False
    )
    purpose:    Mapped[TokenPurpose]    = mapped_column(Enum(TokenPurpose, values_callable=lambda enum_cls: [item.value for item in enum_cls]), nullable=False)
    token_hash: Mapped[str]             = mapped_column(String(256), nullable=False)
    expires_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), nullable=False)
    used_at:    Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime]        = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("Guardian", back_populates="secure_tokens", lazy="raise")

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_valid(self) -> bool:
        return not self.is_expired and not self.is_used

    def __repr__(self) -> str:
        return f"<SecureToken id={self.id} purpose={self.purpose} valid={self.is_valid}>"


# ─────────────────────────────────────────────────────────────────────────────
# OnboardingState — 5-step learner onboarding progress
# ─────────────────────────────────────────────────────────────────────────────

class OnboardingState(Base):
    """
    Tracks each learner/guardian's multi-step onboarding journey.
    One row per user; NULL columns mean the step hasn't been reached yet.

    Steps (in order):
      1. email_verified   — email address confirmed via link
      2. profile_complete — learner name, grade, home language saved
      3. guardian_consent — POPIA parental consent given
      4. diagnostic_done  — baseline diagnostic assessment completed
      5. plan_accepted    — CAPS-aligned study plan accepted
    """
    __tablename__ = "onboarding_states"

    id:      Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("guardians.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    email_verified:   Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    profile_complete: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    guardian_consent: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    diagnostic_done:  Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    plan_accepted:    Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at:   Mapped[datetime]        = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at:   Mapped[datetime]        = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("Guardian", back_populates="onboarding_state", lazy="raise")

    @property
    def is_complete(self) -> bool:
        return all([
            self.email_verified,
            self.profile_complete,
            self.guardian_consent,
            self.diagnostic_done,
            self.plan_accepted,
        ])

    @property
    def progress_pct(self) -> int:
        """Integer 0–100 representing percentage of steps completed."""
        steps = [
            self.email_verified,
            self.profile_complete,
            self.guardian_consent,
            self.diagnostic_done,
            self.plan_accepted,
        ]
        done = sum(1 for s in steps if s)
        return round(done / len(steps) * 100)

    def to_dict(self) -> dict:
        return {
            "email_verified":   self.email_verified,
            "profile_complete": self.profile_complete,
            "guardian_consent": self.guardian_consent,
            "diagnostic_done":  self.diagnostic_done,
            "plan_accepted":    self.plan_accepted,
            "completed_at":     self.completed_at.isoformat() if self.completed_at else None,
            "is_complete":      self.is_complete,
            "progress_pct":     self.progress_pct,
        }


# ─────────────────────────────────────────────────────────────────────────────
# PrivacySettings — POPIA-aligned per-user data preferences
# ─────────────────────────────────────────────────────────────────────────────

class PrivacySettings(Base):
    """
    Granular, per-user privacy preferences aligned with POPIA section 11
    (lawful processing) and section 23 (right to object / right to access).

    analytics_enabled    — aggregate performance analytics shared with teachers
    ai_improvement       — anonymised interaction data fed to RLHF pipeline
    marketing_emails     — transactional-only vs also marketing
    data_retention_days  — learner-selected retention window (90 / 365 / 730 / 0=unlimited)
    show_leaderboard     — whether learner appears on classroom leaderboard
    export_requested_at  — POPIA right-of-access (section 23) tracking
    deletion_requested_at — POPIA right-to-erasure tracking
    """
    __tablename__ = "privacy_settings"

    id:      Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("guardians.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    analytics_enabled:    Mapped[bool] = mapped_column(Boolean, default=True,  nullable=False)
    ai_improvement:       Mapped[bool] = mapped_column(Boolean, default=True,  nullable=False)
    marketing_emails:     Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_retention_days:  Mapped[int]  = mapped_column(Integer, default=365,   nullable=False)
    show_leaderboard:     Mapped[bool] = mapped_column(Boolean, default=True,  nullable=False)

    export_requested_at:   Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deletion_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("Guardian", back_populates="privacy_settings", lazy="raise")

    def to_dict(self) -> dict:
        return {
            "analytics_enabled":     self.analytics_enabled,
            "ai_improvement":        self.ai_improvement,
            "marketing_emails":      self.marketing_emails,
            "data_retention_days":   self.data_retention_days,
            "show_leaderboard":      self.show_leaderboard,
            "export_requested_at":   self.export_requested_at.isoformat()   if self.export_requested_at   else None,
            "deletion_requested_at": self.deletion_requested_at.isoformat() if self.deletion_requested_at else None,
            "updated_at":            self.updated_at.isoformat(),
        }
