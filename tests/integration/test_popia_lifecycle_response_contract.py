from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from fastapi import HTTPException

from app.api_v2_deps.consent_lifecycle import get_canonical_consent_service
from app.api_v2_routers import popia
from app.domain.consent import ConsentRecord, ConsentState
from app.services.popia_consent_lifecycle_adapter import POPIAConsentLifecycleAdapter

@pytest.fixture(autouse=True)
def integration_db():
    pass


LEARNER_ID = uuid.uuid4()
GUARDIAN_ID = uuid.uuid4()
ACTOR_ID = uuid.uuid4()
NOTICE_VERSION = "2026.05"


@dataclass
class FakeConsentService:
    events: list[str] = field(default_factory=list)

    async def grant(self, learner_id: uuid.UUID, guardian_id: uuid.UUID, consent_version: str, **_: Any) -> ConsentRecord:
        self.events.append("consent.granted")
        now = datetime.now(timezone.utc)
        return ConsentRecord(
            learner_id=learner_id,
            guardian_id=guardian_id,
            privacy_notice_version=consent_version,
            state=ConsentState.GRANTED,
            granted_at=now,
            expires_at=now + timedelta(days=365),
        )

    async def revoke(self, learner_id: uuid.UUID, guardian_id: uuid.UUID | None = None, reason: str = "revoked") -> int:
        self.events.append(f"consent.{reason}")
        return 1

    async def renew(self, learner_id: uuid.UUID, consent_version: str = "", guardian_id: uuid.UUID | None = None, **kwargs: Any) -> dict[str, Any]:
        self.events.append("consent.renewed")
        now = datetime.now(timezone.utc)
        return {
            "learner_id": learner_id,
            "guardian_id": guardian_id or kwargs.get("actor_id"),
            "privacy_notice_version": consent_version,
            "state": "granted",
            "granted_at": now,
            "expires_at": now + timedelta(days=365),
        }


def _unwrap(payload: dict[str, Any]) -> dict[str, Any]:
    return payload["data"] if "data" in payload and "meta" in payload else payload


def _current_user() -> dict[str, Any]:
    return {"id": str(ACTOR_ID), "guardian_id": str(GUARDIAN_ID), "role": "parent"}


def _service(service: FakeConsentService) -> POPIAConsentLifecycleAdapter:
    return POPIAConsentLifecycleAdapter(service)


async def _enforce_allow(current_user: Any, learner_id: uuid.UUID) -> None:
    return None


async def _enforce_deny(current_user: Any, learner_id: uuid.UUID) -> None:
    raise HTTPException(status_code=403, detail="forbidden")


def _patch_enforcement(monkeypatch: pytest.MonkeyPatch, *, deny_authz: bool = False) -> None:
    monkeypatch.setattr(popia, "_enforce_popia_learner_write", _enforce_deny if deny_authz else _enforce_allow)


async def _grant_flow(service: FakeConsentService, *, deny_authz: bool = False) -> ConsentRecord:
    body = popia.ConsentGrantRequest(
        learner_id=LEARNER_ID,
        guardian_id=GUARDIAN_ID,
        privacy_notice_version=NOTICE_VERSION,
    )
    return await popia.grant_consent(
        body=body,
        consent_svc=_service(service),
        current_user=_current_user(),
    )


async def _deny_flow(service: FakeConsentService, *, deny_authz: bool = False) -> ConsentRecord:
    body = popia.ConsentDenyRequest(
        learner_id=LEARNER_ID,
        guardian_id=GUARDIAN_ID,
        privacy_notice_version=NOTICE_VERSION,
        reason="denied",
    )
    return await popia.deny_consent(
        body=body,
        consent_svc=_service(service),
        current_user=_current_user(),
    )


async def _withdraw_flow(service: FakeConsentService) -> ConsentRecord:
    body = popia.ConsentWithdrawRequest(learner_id=LEARNER_ID)
    return await popia.withdraw_consent(
        body=body,
        consent_svc=_service(service),
        current_user=_current_user(),
    )


async def _renew_flow(service: FakeConsentService) -> ConsentRecord:
    body = popia.ConsentRenewRequest(
        learner_id=LEARNER_ID,
        privacy_notice_version=NOTICE_VERSION,
    )
    return await popia.renew_consent(
        body=body,
        consent_svc=_service(service),
        current_user=_current_user(),
    )


@pytest.mark.asyncio
async def test_grant_deny_withdraw_renew_http_response_contracts_no_skips(monkeypatch: pytest.MonkeyPatch):
    async def fake_enforce(current_user: Any, learner_id: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(popia, "_enforce_popia_learner_write", fake_enforce)
    service = FakeConsentService()

    grant = await _grant_flow(service)
    assert grant.learner_id == LEARNER_ID
    assert grant.guardian_id == GUARDIAN_ID
    assert grant.privacy_notice_version == NOTICE_VERSION
    assert grant.state == ConsentState.GRANTED

    deny = await _deny_flow(service)
    assert deny.learner_id == LEARNER_ID
    assert deny.guardian_id == GUARDIAN_ID
    assert deny.privacy_notice_version == NOTICE_VERSION
    assert deny.state == ConsentState.DENIED

    withdraw = await _withdraw_flow(service)
    assert withdraw.learner_id == LEARNER_ID
    assert withdraw.guardian_id == ACTOR_ID
    assert withdraw.privacy_notice_version in {NOTICE_VERSION, "unknown"}
    assert withdraw.state == ConsentState.WITHDRAWN

    renew = await _renew_flow(service)
    assert renew.learner_id == LEARNER_ID
    assert renew.guardian_id == ACTOR_ID
    assert renew.privacy_notice_version == NOTICE_VERSION
    assert renew.state == ConsentState.GRANTED
    assert {"consent.granted", "consent.denied", "consent.revoked", "consent.renewed"}.issubset(set(service.events))


@pytest.mark.asyncio
async def test_unauthorized_learner_consent_mutation_is_denied_no_skips(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(popia, "_enforce_popia_learner_write", _enforce_deny)
    with pytest.raises(HTTPException) as exc:
        await _grant_flow(FakeConsentService(), deny_authz=True)
    assert exc.value.status_code == 403


def test_adapter_normalizes_legacy_revoke_integer_to_consent_record_no_skips():
    async def run() -> None:
        adapter = POPIAConsentLifecycleAdapter(FakeConsentService())
        record = await adapter.withdraw(
            learner_id=LEARNER_ID,
            guardian_id=GUARDIAN_ID,
            privacy_notice_version=NOTICE_VERSION,
            actor_id=ACTOR_ID,
        )
        assert isinstance(record, ConsentRecord)
        assert record.state == ConsentState.WITHDRAWN

    asyncio.run(run())
