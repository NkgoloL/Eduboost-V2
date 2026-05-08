from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from app.core.consent_policy import ConsentState, derive_consent_state
from app.core.exceptions import ConsentExpiredError, ConsentRequiredError
from app.modules.consent.service import ConsentService


NOW = datetime(2026, 5, 7, tzinfo=UTC)


def consent(**overrides):
    data = {
        "learner_id": "learner-1",
        "policy_version": "2026.05",
        "granted_at": NOW - timedelta(days=10),
        "expires_at": NOW + timedelta(days=120),
        "revoked_at": None,
        "status": ConsentState.GRANTED,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_missing_consent_is_pending_and_blocking() -> None:
    decision = derive_consent_state(None, learner_id="learner-1", now=NOW)
    assert decision.state == ConsentState.PENDING
    assert decision.active is False
    assert decision.reason == "no_consent_record"


def test_granted_consent_is_active() -> None:
    decision = derive_consent_state(consent(), learner_id="learner-1", now=NOW)
    assert decision.state == ConsentState.GRANTED
    assert decision.active is True


def test_expiring_consent_enters_renewal_required_but_remains_active() -> None:
    decision = derive_consent_state(
        consent(expires_at=NOW + timedelta(days=5)),
        learner_id="learner-1",
        now=NOW,
        renewal_window_days=30,
    )
    assert decision.state == ConsentState.RENEWAL_REQUIRED
    assert decision.active is True


def test_withdrawn_and_expired_consent_block() -> None:
    withdrawn = derive_consent_state(consent(revoked_at=NOW), learner_id="learner-1", now=NOW)
    expired = derive_consent_state(consent(expires_at=NOW - timedelta(seconds=1)), learner_id="learner-1", now=NOW)
    assert withdrawn.state == ConsentState.WITHDRAWN
    assert expired.state == ConsentState.EXPIRED
    assert withdrawn.active is False
    assert expired.active is False


class FakeRepo:
    def __init__(self, record):
        self.record = record

    async def get_latest_for_learner(self, learner_id: str):
        return self.record


class FakeAudit:
    def __init__(self):
        self.events = []

    async def append(self, **kwargs):
        self.events.append(kwargs)


@pytest.mark.asyncio
async def test_consent_service_rejects_missing_consent_with_audit() -> None:
    audit = FakeAudit()
    service = ConsentService(consent_repo=FakeRepo(None), audit_repo=audit)

    with pytest.raises(ConsentRequiredError):
        await service.require_active_consent("learner-1", actor_id="guardian-1")

    assert audit.events[0]["event_type"] == "consent.access_rejected"
    assert audit.events[0]["payload"]["state"] == "pending"


@pytest.mark.asyncio
async def test_consent_service_distinguishes_expired_consent() -> None:
    audit = FakeAudit()
    service = ConsentService(
        consent_repo=FakeRepo(consent(expires_at=datetime(2020, 1, 1, tzinfo=UTC))),
        audit_repo=audit,
    )

    with pytest.raises(ConsentExpiredError):
        await service.require_active_consent("learner-1", actor_id="guardian-1")
