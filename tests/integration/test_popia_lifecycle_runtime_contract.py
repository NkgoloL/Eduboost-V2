from __future__ import annotations

import asyncio
import inspect

from app.services.popia_consent_lifecycle_adapter import POPIAConsentLifecycleAdapter


class CanonicalConsentServiceShape:
    def __init__(self):
        self.calls = []

    async def grant(self, guardian_id, learner_id, consent_version, actor_id=None):
        self.calls.append(("grant", guardian_id, learner_id, consent_version, actor_id))
        return {"action": "grant"}

    async def revoke(self, guardian_id=None, learner_id=None, actor_id=None, reason=None):
        self.calls.append(("revoke", guardian_id, learner_id, actor_id, reason))
        return {"action": "revoke"}


def test_popia_lifecycle_adapter_covers_router_signature_drift():
    async def run():
        service = CanonicalConsentServiceShape()
        adapter = POPIAConsentLifecycleAdapter(service)

        await adapter.grant(
            guardian_id="guardian-1",
            learner_id="learner-1",
            privacy_notice_version="notice-v1",
            actor_id="actor-1",
        )
        await adapter.deny(guardian_id="guardian-1", learner_id="learner-1", actor_id="actor-1")
        await adapter.withdraw(guardian_id="guardian-1", learner_id="learner-1", actor_id="actor-1")
        await adapter.renew(
            guardian_id="guardian-1",
            learner_id="learner-1",
            privacy_notice_version="notice-v2",
            actor_id="actor-1",
        )

        assert service.calls[0] == ("grant", "guardian-1", "learner-1", "notice-v1", "actor-1")
        assert service.calls[1][0] == "revoke"
        assert service.calls[2][0] == "revoke"
        assert service.calls[3] == ("grant", "guardian-1", "learner-1", "notice-v2", "actor-1")

    asyncio.run(run())


def test_canonical_consent_dependency_factory_returns_adapter_when_callable(monkeypatch):
    import app.api_v2_deps.consent_lifecycle as deps

    class FakeCanonicalConsentService:
        def __init__(self, db=None, session=None, consent_repo=None, consent_repository=None):
            self.db = db
            self.session = session
            self.consent_repo = consent_repo or consent_repository

        async def grant(self, guardian_id, learner_id, consent_version):
            return {"guardian_id": guardian_id, "learner_id": learner_id, "consent_version": consent_version}

    class FakeConsentRepository:
        def __init__(self, db):
            self.db = db

    monkeypatch.setattr(deps, "ConsentService", FakeCanonicalConsentService, raising=False)
    monkeypatch.setattr(deps, "ConsentRepository", FakeConsentRepository, raising=False)

    service = deps.get_canonical_consent_service(db=object())

    assert isinstance(service, POPIAConsentLifecycleAdapter)
    assert hasattr(service, "grant")
    assert inspect.iscoroutinefunction(service.grant)


def test_fastapi_app_contains_popia_lifecycle_routes():
    try:
        from app.api_v2 import app
    except Exception:
        from app.main import app  # type: ignore

    route_names = {
        getattr(route, "name", "") or getattr(getattr(route, "endpoint", None), "__name__", "")
        for route in getattr(app, "routes", [])
    }
    joined = " ".join(sorted(route_names)).lower()

    assert "consent" in joined or "popia" in joined
    assert any(token in joined for token in ("grant", "deny", "withdraw", "revoke", "renew"))
