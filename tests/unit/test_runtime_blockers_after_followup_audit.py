from __future__ import annotations

import asyncio
from pathlib import Path

from app.services.popia_consent_lifecycle_adapter import POPIAConsentLifecycleAdapter

ROOT = Path(__file__).resolve().parents[2]


class CanonicalConsentStub:
    def __init__(self):
        self.calls = []

    async def grant(self, guardian_id, learner_id, consent_version, actor_id=None):
        self.calls.append(("grant", guardian_id, learner_id, consent_version, actor_id))
        return {"ok": True}

    async def revoke(self, guardian_id=None, learner_id=None, actor_id=None, reason=None):
        self.calls.append(("revoke", guardian_id, learner_id, actor_id, reason))
        return {"ok": True}


def test_popia_adapter_maps_router_kwargs_to_canonical_grant():
    async def run():
        service = CanonicalConsentStub()
        adapter = POPIAConsentLifecycleAdapter(service)
        await adapter.grant(guardian_id="guardian-1", learner_id="learner-1", privacy_notice_version="v1", actor_id="actor-1")
        assert service.calls[0] == ("grant", "guardian-1", "learner-1", "v1", "actor-1")
    asyncio.run(run())


def test_popia_adapter_provides_deny_withdraw_via_revoke_fallback():
    async def run():
        service = CanonicalConsentStub()
        adapter = POPIAConsentLifecycleAdapter(service)
        await adapter.deny(guardian_id="g", learner_id="l", actor_id="a")
        await adapter.withdraw(guardian_id="g", learner_id="l", actor_id="a")
        assert [call[0] for call in service.calls] == ["revoke", "revoke"]
    asyncio.run(run())


def test_auth_router_has_no_learners_regression_or_direct_repo_constructors():
    source = (ROOT / "app/api_v2_routers/auth.py").read_text(encoding="utf-8")
    assert "learners" not in source
    assert "LearnerRepository(" not in source
    assert "ConsentRepository(" not in source
    assert "GuardianRepository(" not in source


def test_jobs_have_consent_reminder_aliases_without_missing_direct_symbols():
    source = (ROOT / "app/modules/jobs.py").read_text(encoding="utf-8")
    assert "async def send_consent_reminders" in source
    assert "async def send_consent_renewal_reminders" in source
    assert "run_consent_reminder_cycle" in source
    assert "ConsentService(" not in source
    assert "AsyncSessionLocal" not in source


def test_diagnostics_submission_is_not_generated_with_require_items_false():
    source = (ROOT / "app/api_v2_routers/diagnostics.py").read_text(encoding="utf-8")
    assert "require_items=False" not in source


def test_consent_lifecycle_dependency_uses_adapter():
    source = (ROOT / "app/api_v2_deps/consent_lifecycle.py").read_text(encoding="utf-8")
    assert "POPIAConsentLifecycleAdapter" in source
