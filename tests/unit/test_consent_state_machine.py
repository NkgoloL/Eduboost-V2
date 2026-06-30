"""
B.1/B.2 — Consent lifecycle state machine tests and enforcement tests.

Covers:
  - All valid state transitions (pending→granted, granted→withdrawn, etc.)
  - Invalid transitions raise ValueError
  - Active/inactive state determination
  - Consent denial flow with reason
  - Consent enforcement: analytics, export, erasure blocked without active consent
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.consent import (
    ConsentRecord,
    ConsentState,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _consent(state: ConsentState, **kwargs) -> ConsentRecord:
    base = dict(
        learner_id="00000000-0000-0000-0000-000000000001",
        guardian_id="00000000-0000-0000-0000-000000000002",
        privacy_notice_version="1.0.0",
        state=state,
    )
    base.update(kwargs)
    return ConsentRecord(**base)


# ── B.1.1 — State transitions: pending ───────────────────────────────────────

def test_pending_can_be_granted():
    c = _consent(ConsentState.PENDING)
    granted = c.grant("1.0.0")
    assert granted.state == ConsentState.GRANTED
    assert granted.granted_at is not None
    assert granted.expires_at is not None


def test_pending_can_be_denied():
    c = _consent(ConsentState.PENDING)
    denied = c.deny(reason="Guardian declines")
    assert denied.state == ConsentState.DENIED
    assert denied.denial_reason == "Guardian declines"


def test_pending_cannot_be_withdrawn():
    c = _consent(ConsentState.PENDING)
    with pytest.raises(ValueError, match="Invalid consent transition"):
        c.withdraw()


# ── B.1.2 — State transitions: granted ───────────────────────────────────────

def test_granted_can_be_withdrawn():
    c = _consent(ConsentState.GRANTED)
    withdrawn = c.withdraw()
    assert withdrawn.state == ConsentState.WITHDRAWN
    assert withdrawn.withdrawn_at is not None


def test_granted_can_be_renewed():
    c = _consent(ConsentState.GRANTED)
    renewed = c.renew("2.0.0")
    assert renewed.state == ConsentState.GRANTED
    assert renewed.privacy_notice_version == "2.0.0"
    assert renewed.expires_at > datetime.now(timezone.utc)


def test_granted_can_be_expired():
    c = _consent(ConsentState.GRANTED)
    expired = c.mark_expired()
    assert expired.state == ConsentState.EXPIRED


def test_granted_can_become_renewal_required():
    c = _consent(ConsentState.GRANTED)
    renewal_req = c.mark_renewal_required()
    assert renewal_req.state == ConsentState.RENEWAL_REQUIRED


def test_granted_cannot_be_denied():
    c = _consent(ConsentState.GRANTED)
    with pytest.raises(ValueError, match="Invalid consent transition"):
        c.deny()


# ── B.1.3 — State transitions: denied ────────────────────────────────────────

def test_denied_can_be_granted():
    c = _consent(ConsentState.DENIED)
    granted = c.grant("1.1.0")
    assert granted.state == ConsentState.GRANTED


def test_denied_cannot_be_withdrawn():
    c = _consent(ConsentState.DENIED)
    with pytest.raises(ValueError, match="Invalid consent transition"):
        c.withdraw()


# ── B.1.4 — State transitions: expired ───────────────────────────────────────

def test_expired_can_be_renewed():
    c = _consent(ConsentState.EXPIRED)
    granted = c.grant("1.2.0")
    assert granted.state == ConsentState.GRANTED


def test_expired_can_become_renewal_required():
    c = _consent(ConsentState.EXPIRED)
    renewal_req = c.mark_renewal_required()
    assert renewal_req.state == ConsentState.RENEWAL_REQUIRED


# ── B.1.5 — State transitions: withdrawn ─────────────────────────────────────

def test_withdrawn_can_be_re_granted():
    c = _consent(ConsentState.WITHDRAWN)
    granted = c.grant("1.0.0")
    assert granted.state == ConsentState.GRANTED


# ── B.1.6 — State transitions: renewal_required ──────────────────────────────

def test_renewal_required_can_be_granted():
    c = _consent(ConsentState.RENEWAL_REQUIRED)
    granted = c.grant("2.0.0")
    assert granted.state == ConsentState.GRANTED


def test_renewal_required_can_be_withdrawn():
    c = _consent(ConsentState.RENEWAL_REQUIRED)
    withdrawn = c.withdraw()
    assert withdrawn.state == ConsentState.WITHDRAWN


# ── B.1.7 — is_active() logic ────────────────────────────────────────────────

def test_granted_not_expired_is_active():
    future = datetime.now(timezone.utc) + timedelta(days=100)
    c = _consent(ConsentState.GRANTED, expires_at=future, granted_at=datetime.now(timezone.utc))
    assert c.is_active() is True


def test_granted_but_expired_timestamp_is_not_active():
    past = datetime.now(timezone.utc) - timedelta(days=1)
    c = _consent(ConsentState.GRANTED, expires_at=past)
    assert c.is_active() is False


def test_withdrawn_is_not_active():
    c = _consent(ConsentState.WITHDRAWN)
    assert c.is_active() is False


def test_denied_is_not_active():
    c = _consent(ConsentState.DENIED)
    assert c.is_active() is False


def test_expired_state_is_not_active():
    c = _consent(ConsentState.EXPIRED)
    assert c.is_active() is False


def test_renewal_required_is_not_active():
    c = _consent(ConsentState.RENEWAL_REQUIRED)
    assert c.is_active() is False


def test_pending_is_not_active():
    c = _consent(ConsentState.PENDING)
    assert c.is_active() is False


# ── B.1.8 — days_until_expiry ────────────────────────────────────────────────

def test_days_until_expiry_returns_positive_for_future():
    future = datetime.now(timezone.utc) + timedelta(days=30)
    c = _consent(ConsentState.GRANTED, expires_at=future)
    assert c.days_until_expiry() == 30


def test_days_until_expiry_returns_zero_for_past():
    past = datetime.now(timezone.utc) - timedelta(days=5)
    c = _consent(ConsentState.GRANTED, expires_at=past)
    assert c.days_until_expiry() == 0


def test_days_until_expiry_returns_none_when_no_expiry():
    c = _consent(ConsentState.GRANTED, expires_at=None)
    assert c.days_until_expiry() is None


# ── B.2 — Consent enforcement: operations blocked without active consent ──────

@pytest.mark.asyncio
async def test_require_active_consent_raises_when_no_consent():
    """require_active_consent must raise ConsentRequiredError when no record exists."""
    from app.core.exceptions import ConsentRequiredError
    from app.modules.consent.service import ConsentService

    mock_repo = AsyncMock()
    mock_repo.get_latest_for_learner = AsyncMock(return_value=None)

    svc = ConsentService(consent_repo=mock_repo)

    with pytest.raises(ConsentRequiredError):
        await svc.require_active_consent("learner-no-consent")


@pytest.mark.asyncio
async def test_require_active_consent_raises_when_withdrawn():
    """require_active_consent must raise when consent is in WITHDRAWN state."""
    from app.core.exceptions import ConsentRequiredError
    from app.modules.consent.service import ConsentService

    mock_consent = MagicMock()
    mock_consent.is_active = MagicMock(return_value=False)
    mock_consent.revoked_at = datetime.now(timezone.utc)
    mock_consent.expires_at = None
    mock_consent.granted_at = None
    mock_consent.learner_id = "learner-1"
    mock_consent.policy_version = "1.0.0"

    mock_repo = AsyncMock()
    mock_repo.get_latest_for_learner = AsyncMock(return_value=mock_consent)

    # derive_consent_state will evaluate the raw object
    from unittest.mock import patch

    with patch("app.modules.consent.service.derive_consent_state") as mock_derive:

        # Simulate a withdrawn decision
        mock_decision = MagicMock()
        mock_decision.active = False
        mock_decision.reason = "Consent has been withdrawn"
        mock_decision.state = MagicMock(value="withdrawn")
        mock_derive.return_value = mock_decision

        svc = ConsentService(consent_repo=mock_repo)

        with pytest.raises(ConsentRequiredError):
            await svc.require_active_consent("learner-1")


@pytest.mark.asyncio
async def test_require_active_consent_raises_when_expired():
    """require_active_consent must raise ConsentExpiredError when consent is expired."""
    from app.core.exceptions import ConsentExpiredError
    from app.modules.consent.service import ConsentService
    from unittest.mock import patch

    mock_repo = AsyncMock()
    mock_repo.get_latest_for_learner = AsyncMock(return_value=MagicMock(
        is_active=lambda: False,
        revoked_at=None,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        granted_at=datetime.now(timezone.utc) - timedelta(days=366),
        learner_id="learner-expired",
        policy_version="1.0.0",
    ))

    with patch("app.modules.consent.service.derive_consent_state") as mock_derive:
        mock_decision = MagicMock()
        mock_decision.active = False
        mock_decision.reason = "Consent has expired"
        mock_decision.state = MagicMock(value="expired")
        mock_derive.return_value = mock_decision

        svc = ConsentService(consent_repo=mock_repo)

        with pytest.raises(ConsentExpiredError):
            await svc.require_active_consent("learner-expired")


@pytest.mark.asyncio
async def test_require_active_consent_passes_when_active():
    """require_active_consent must not raise when consent is active and valid."""
    from app.modules.consent.service import ConsentService
    from unittest.mock import patch

    mock_repo = AsyncMock()
    mock_repo.get_latest_for_learner = AsyncMock(return_value=MagicMock(
        is_active=lambda: True,
        revoked_at=None,
        expires_at=datetime.now(timezone.utc) + timedelta(days=100),
        granted_at=datetime.now(timezone.utc) - timedelta(days=10),
        learner_id="learner-active",
        policy_version="1.0.0",
    ))

    with patch("app.modules.consent.service.derive_consent_state") as mock_derive:
        mock_decision = MagicMock()
        mock_decision.active = True
        mock_decision.reason = None
        mock_decision.state = MagicMock(value="granted")
        mock_derive.return_value = mock_decision

        svc = ConsentService(consent_repo=mock_repo)
        result = await svc.require_active_consent("learner-active")

    assert result.active is True
