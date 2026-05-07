"""Canonical POPIA consent-state policy.

The database currently stores consent as lifecycle timestamps.  This module
provides the single runtime interpretation used by routers, services, tests,
and documentation so consent semantics do not drift into scattered boolean
checks.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any


class ConsentState(StrEnum):
    """Canonical learner consent states for POPIA workflows."""

    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    RENEWAL_REQUIRED = "renewal_required"


ACTIVE_CONSENT_STATES = {ConsentState.GRANTED, ConsentState.RENEWAL_REQUIRED}
BLOCKING_CONSENT_STATES = {
    ConsentState.PENDING,
    ConsentState.DENIED,
    ConsentState.EXPIRED,
    ConsentState.WITHDRAWN,
}


@dataclass(frozen=True)
class ConsentPolicyDecision:
    learner_id: str
    state: ConsentState
    active: bool
    reason: str
    policy_version: str | None = None
    privacy_notice_version: str | None = None
    granted_at: datetime | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    renewal_due_at: datetime | None = None


def _as_aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def derive_consent_state(
    consent: Any | None,
    *,
    learner_id: str,
    privacy_notice_version: str | None = None,
    renewal_window_days: int = 30,
    now: datetime | None = None,
) -> ConsentPolicyDecision:
    """Return the canonical consent decision for a learner.

    ``renewal_required`` is deliberately still active: it allows the learner to
    continue core educational processing during the renewal window while
    product/ops can surface notices.  ``expired`` and ``withdrawn`` block all
    learner-data processing.
    """
    current_time = _as_aware(now) or datetime.now(UTC)
    if consent is None:
        return ConsentPolicyDecision(
            learner_id=str(learner_id),
            state=ConsentState.PENDING,
            active=False,
            reason="no_consent_record",
            privacy_notice_version=privacy_notice_version,
        )

    granted_at = _as_aware(getattr(consent, "granted_at", None))
    expires_at = _as_aware(getattr(consent, "expires_at", None))
    revoked_at = _as_aware(getattr(consent, "revoked_at", None))
    policy_version = getattr(consent, "policy_version", None)
    renewal_due_at = None

    persisted_state = getattr(consent, "status", None)
    if persisted_state is not None:
        try:
            persisted_state = ConsentState(getattr(persisted_state, "value", persisted_state))
        except ValueError:
            persisted_state = None

    if persisted_state in {ConsentState.PENDING, ConsentState.DENIED}:
        state = persisted_state
        active = False
        reason = f"consent_{state.value}"
    elif revoked_at is not None or persisted_state == ConsentState.WITHDRAWN:
        state = ConsentState.WITHDRAWN
        active = False
        reason = "consent_withdrawn"
    elif expires_at is not None and expires_at <= current_time:
        state = ConsentState.EXPIRED
        active = False
        reason = "consent_expired"
    else:
        if expires_at is not None:
            renewal_due_at = expires_at - timedelta(days=renewal_window_days)
        if renewal_due_at is not None and current_time >= renewal_due_at:
            state = ConsentState.RENEWAL_REQUIRED
            active = True
            reason = "consent_in_renewal_window"
        else:
            state = ConsentState.GRANTED
            active = True
            reason = "active_consent"

    return ConsentPolicyDecision(
        learner_id=str(learner_id),
        state=state,
        active=active,
        reason=reason,
        policy_version=policy_version,
        privacy_notice_version=privacy_notice_version,
        granted_at=granted_at,
        expires_at=expires_at,
        revoked_at=revoked_at,
        renewal_due_at=renewal_due_at,
    )


__all__ = [
    "ACTIVE_CONSENT_STATES",
    "BLOCKING_CONSENT_STATES",
    "ConsentPolicyDecision",
    "ConsentState",
    "derive_consent_state",
]
