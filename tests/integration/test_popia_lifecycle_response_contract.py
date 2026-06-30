from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api_v2_deps.consent_lifecycle import get_canonical_consent_service
from app.api_v2_routers import popia
from app.core.security import get_current_user
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


def _client(monkeypatch: pytest.MonkeyPatch, service: FakeConsentService, *, deny_authz: bool = False) -> TestClient:
    async def fake_enforce(current_user: Any, learner_id: uuid.UUID) -> None:
        if deny_authz:
            raise HTTPException(status_code=403, detail="forbidden")

    monkeypatch.setattr(popia, "_enforce_popia_learner_write", fake_enforce)
    app = FastAPI()
    app.include_router(popia.router)
    app.dependency_overrides[get_current_user] = lambda: {"id": str(ACTOR_ID), "guardian_id": str(GUARDIAN_ID)}
    app.dependency_overrides[get_canonical_consent_service] = lambda: POPIAConsentLifecycleAdapter(service)
    return TestClient(app, raise_server_exceptions=True)


def _assert_consent_payload(payload: dict[str, Any], *, state: str) -> None:
    data = _unwrap(payload)
    assert data["learner_id"] == str(LEARNER_ID)
    assert data["guardian_id"] in {str(GUARDIAN_ID), str(ACTOR_ID)}
    assert data["privacy_notice_version"] in {NOTICE_VERSION, "unknown"}
    assert data["state"] == state


def test_grant_deny_withdraw_renew_http_response_contracts_no_skips(monkeypatch: pytest.MonkeyPatch):
    service = FakeConsentService()
    client = _client(monkeypatch, service)

    grant = client.post(
        "/popia/consent/grant",
        json={"learner_id": str(LEARNER_ID), "guardian_id": str(GUARDIAN_ID), "privacy_notice_version": NOTICE_VERSION},
    )
    assert grant.status_code == 200
    _assert_consent_payload(grant.json(), state="granted")

    deny = client.post(
        "/popia/consent/deny",
        json={
            "learner_id": str(LEARNER_ID),
            "guardian_id": str(GUARDIAN_ID),
            "privacy_notice_version": NOTICE_VERSION,
            "reason": "denied",
        },
    )
    assert deny.status_code == 200
    _assert_consent_payload(deny.json(), state="denied")

    withdraw = client.post("/popia/consent/withdraw", json={"learner_id": str(LEARNER_ID)})
    assert withdraw.status_code == 200
    _assert_consent_payload(withdraw.json(), state="withdrawn")

    renew = client.post(
        "/popia/consent/renew",
        json={"learner_id": str(LEARNER_ID), "privacy_notice_version": NOTICE_VERSION},
    )
    assert renew.status_code == 200
    _assert_consent_payload(renew.json(), state="granted")
    assert {"consent.granted", "consent.denied", "consent.revoked", "consent.renewed"}.issubset(set(service.events))


def test_unauthorized_learner_consent_mutation_is_denied_no_skips(monkeypatch: pytest.MonkeyPatch):
    client = _client(monkeypatch, FakeConsentService(), deny_authz=True)
    response = client.post(
        "/popia/consent/grant",
        json={"learner_id": str(LEARNER_ID), "guardian_id": str(GUARDIAN_ID), "privacy_notice_version": NOTICE_VERSION},
    )
    assert response.status_code == 403


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
