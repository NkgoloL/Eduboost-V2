"""
app/domain/consent.py
POPIA consent domain – states, aggregate, and domain events.
Covers backlog §4.1 (consent lifecycle) and §4.2 (declarative enforcement).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# §4.1  Consent states
# ---------------------------------------------------------------------------

class ConsentState(str, Enum):
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    RENEWAL_REQUIRED = "renewal_required"


# Transitions that are allowed (from_state → {to_states})
ALLOWED_TRANSITIONS: dict[ConsentState, set[ConsentState]] = {
    ConsentState.PENDING:          {ConsentState.GRANTED, ConsentState.DENIED},
    ConsentState.GRANTED:          {ConsentState.GRANTED, ConsentState.WITHDRAWN,
                                    ConsentState.EXPIRED, ConsentState.RENEWAL_REQUIRED},
    ConsentState.DENIED:           {ConsentState.GRANTED},
    ConsentState.EXPIRED:          {ConsentState.RENEWAL_REQUIRED, ConsentState.GRANTED},
    ConsentState.WITHDRAWN:        {ConsentState.GRANTED},
    ConsentState.RENEWAL_REQUIRED: {ConsentState.GRANTED, ConsentState.WITHDRAWN},
}

# Default consent validity in days (P1: configurable via settings)
CONSENT_VALIDITY_DAYS = 365
RENEWAL_WARNING_DAYS = 30     # how early to flag renewal_required


# ---------------------------------------------------------------------------
# Consent aggregate
# ---------------------------------------------------------------------------

class ConsentRecord(BaseModel):
    """Immutable value-object representing one consent snapshot."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    learner_id: uuid.UUID                        # §4.1 tie to learner identity
    guardian_id: uuid.UUID                       # §4.1 tie to guardian identity
    privacy_notice_version: str                  # §4.1 tie to notice version
    state: ConsentState = ConsentState.PENDING
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    denial_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # -----------------------------------------------------------------------
    # §4.1 Flow helpers (return NEW record – domain objects stay immutable)
    # -----------------------------------------------------------------------

    def grant(self, privacy_notice_version: str) -> "ConsentRecord":
        # audit_log
        self._assert_transition(ConsentState.GRANTED)
        now = datetime.now(timezone.utc)
        return self.model_copy(update={
            "state": ConsentState.GRANTED,
            "granted_at": now,
            "expires_at": now + timedelta(days=CONSENT_VALIDITY_DAYS),
            "privacy_notice_version": privacy_notice_version,
            "updated_at": now,
        })

    def deny(self, reason: Optional[str] = None) -> "ConsentRecord":
        self._assert_transition(ConsentState.DENIED)
        now = datetime.now(timezone.utc)
        return self.model_copy(update={
            "state": ConsentState.DENIED,
            "denial_reason": reason,
            "updated_at": now,
        })

    def withdraw(self) -> "ConsentRecord":
        self._assert_transition(ConsentState.WITHDRAWN)
        now = datetime.now(timezone.utc)
        return self.model_copy(update={
            "state": ConsentState.WITHDRAWN,
            "withdrawn_at": now,
            "updated_at": now,
        })

    def renew(self, privacy_notice_version: str) -> "ConsentRecord":
        """Reset the expiry clock – used for §4.1 renewal flow."""
        self._assert_transition(ConsentState.GRANTED)
        now = datetime.now(timezone.utc)
        return self.model_copy(update={
            "state": ConsentState.GRANTED,
            "granted_at": now,
            "expires_at": now + timedelta(days=CONSENT_VALIDITY_DAYS),
            "privacy_notice_version": privacy_notice_version,
            "updated_at": now,
        })

    def mark_expired(self) -> "ConsentRecord":
        self._assert_transition(ConsentState.EXPIRED)
        return self.model_copy(update={
            "state": ConsentState.EXPIRED,
            "updated_at": datetime.now(timezone.utc),
        })

    def mark_renewal_required(self) -> "ConsentRecord":
        self._assert_transition(ConsentState.RENEWAL_REQUIRED)
        return self.model_copy(update={
            "state": ConsentState.RENEWAL_REQUIRED,
            "updated_at": datetime.now(timezone.utc),
        })

    def is_active(self) -> bool:
        """True only when consent is GRANTED and not yet expired."""
        if self.state != ConsentState.GRANTED:
            return False
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            return False
        return True

    def days_until_expiry(self) -> Optional[int]:
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.now(timezone.utc)
        return max(0, delta.days)

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _assert_transition(self, target: ConsentState) -> None:
        allowed = ALLOWED_TRANSITIONS.get(self.state, set())
        if target not in allowed:
            raise ValueError(
                f"Invalid consent transition: {self.state!r} → {target!r}. "
                f"Allowed: {allowed}"
            )


# ---------------------------------------------------------------------------
# §4.5  Audit event types (domain-level enum, used by audit repository)
# ---------------------------------------------------------------------------

class AuditEventType(str, Enum):
    # Auth
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    TOKEN_REFRESH = "token_refresh"
    LOGOUT = "logout"
    # Consent
    CONSENT_GRANT = "consent_grant"
    CONSENT_RENEWAL = "consent_renewal"
    CONSENT_WITHDRAWAL = "consent_withdrawal"
    CONSENT_EXPIRY = "consent_expiry"
    CONSENT_DENIAL = "consent_denial"
    # Learner data
    LEARNER_PROFILE_CREATE = "learner_profile_create"
    LEARNER_PROFILE_UPDATE = "learner_profile_update"
    LEARNER_PROFILE_DELETE = "learner_profile_delete"
    # Diagnostics
    DIAGNOSTIC_START = "diagnostic_start"
    DIAGNOSTIC_ANSWER = "diagnostic_answer_submission"
    DIAGNOSTIC_COMPLETE = "diagnostic_completion"
    # Learning
    LESSON_GENERATION = "lesson_generation"
    LLM_PROVIDER_CALL = "llm_provider_call"
    PARENT_REPORT_GENERATION = "parent_report_generation"
    # Data subject rights
    DATA_EXPORT_REQUEST = "data_export_request"
    DATA_EXPORT_DOWNLOAD = "data_export_download"
    ERASURE_REQUEST = "erasure_request"
    ERASURE_EXECUTION = "erasure_execution"
    # Admin / billing
    ADMIN_ACCESS = "admin_access"
    BILLING_CHANGE = "billing_change"
