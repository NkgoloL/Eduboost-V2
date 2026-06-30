from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.consent_policy import ConsentPolicyDecision, ConsentState
from app.core.exceptions import ConsentExpiredError, ConsentRequiredError
from app.modules.consent.service import ConsentService
from app.utils.versioning import VersionChangeType


@pytest.mark.unit
def test_constructor_requires_db_or_repo():
    with pytest.raises(ValueError, match="requires a db session or consent_repo"):
        ConsentService()


@pytest.mark.asyncio
async def test_require_active_consent_rejects_expired_with_explicit_error():
    service = ConsentService(consent_repo=AsyncMock())
    service.consent_decision = AsyncMock(
        return_value=ConsentPolicyDecision(
            learner_id="learner-1",
            state=ConsentState.EXPIRED,
            active=False,
            reason="consent_expired",
        )
    )
    service._append_audit = AsyncMock()

    with pytest.raises(ConsentExpiredError):
        await service.require_active_consent("learner-1", actor_id="guardian-1")

    service._append_audit.assert_awaited_once()


@pytest.mark.asyncio
async def test_require_active_consent_rejects_pending():
    service = ConsentService(consent_repo=AsyncMock())
    service.consent_decision = AsyncMock(
        return_value=ConsentPolicyDecision(
            learner_id="learner-1",
            state=ConsentState.PENDING,
            active=False,
            reason="no_consent_record",
        )
    )
    service._append_audit = AsyncMock()

    with pytest.raises(ConsentRequiredError):
        await service.require_active_consent("learner-1", actor_id="guardian-1")

    service._append_audit.assert_awaited_once()


@pytest.mark.asyncio
async def test_grant_emits_audit_and_history():
    consent = SimpleNamespace(
        id="consent-1",
        learner_id="learner-1",
        guardian_id="guardian-1",
        policy_version="1.0.0",
        granted_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        revoked_at=None,
    )
    repo = AsyncMock()
    repo.grant.return_value = consent

    service = ConsentService(consent_repo=repo)
    service._append_audit = AsyncMock()
    service._record_version_history = AsyncMock()

    result = await service.grant("guardian-1", "learner-1", "1.0.0")

    assert result is consent
    repo.grant.assert_awaited_once()
    service._append_audit.assert_awaited_once()
    service._record_version_history.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_with_active_record_audits_and_histories():
    active = SimpleNamespace(
        id="consent-1",
        learner_id="learner-1",
        guardian_id="guardian-1",
        policy_version="1.0.0",
        granted_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        revoked_at=None,
    )
    repo = AsyncMock()
    repo.get_active.return_value = active
    repo.revoke.return_value = 1

    service = ConsentService(consent_repo=repo)
    service._append_audit = AsyncMock()
    service._record_version_history = AsyncMock()

    count = await service.revoke("learner-1", guardian_id="guardian-1", reason="revoked")

    assert count == 1
    service._append_audit.assert_awaited_once()
    service._record_version_history.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_without_active_record_skips_audit():
    repo = AsyncMock()
    repo.get_active.return_value = None
    repo.revoke.return_value = 0

    service = ConsentService(consent_repo=repo)
    service._append_audit = AsyncMock()
    service._record_version_history = AsyncMock()

    count = await service.revoke("learner-1", guardian_id="guardian-1", reason="revoked")

    assert count == 0
    service._append_audit.assert_not_awaited()
    service._record_version_history.assert_not_awaited()


@pytest.mark.asyncio
async def test_renew_includes_change_type_in_audit_payload():
    previous = SimpleNamespace(policy_version="1.0.0")
    renewed = SimpleNamespace(
        id="consent-2",
        learner_id="learner-1",
        guardian_id="guardian-1",
        policy_version="1.1.0",
        granted_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        revoked_at=None,
    )

    repo = AsyncMock()
    repo.get_latest_for_learner.return_value = previous
    repo.renew.return_value = (previous, renewed)

    service = ConsentService(consent_repo=repo)
    service._append_audit = AsyncMock()
    service._record_version_history = AsyncMock()
    service.detect_version_change_type = lambda _a, _b: VersionChangeType.MINOR

    result = await service.renew("guardian-1", "learner-1", "1.1.0")

    assert result is renewed
    payload = service._append_audit.await_args.kwargs["payload"]
    assert payload["change_type"] == VersionChangeType.MINOR.value


@pytest.mark.asyncio
async def test_execute_erasure_calls_revoke_and_audit():
    service = ConsentService(consent_repo=AsyncMock())
    service.revoke = AsyncMock(return_value=1)
    service._append_audit = AsyncMock()

    await service.execute_erasure("guardian-1", "learner-1")

    service.revoke.assert_awaited_once_with("learner-1", guardian_id="guardian-1", reason="erasure_requested")
    service._append_audit.assert_awaited_once()


@pytest.mark.asyncio
async def test_append_audit_uses_audit_repo_when_configured():
    audit_repo = AsyncMock()
    service = ConsentService(consent_repo=AsyncMock(), audit_repo=audit_repo)

    await service._append_audit(
        "consent.granted",
        actor_id="guardian-1",
        resource_id="consent-1",
        payload={"ok": True},
    )

    audit_repo.append.assert_awaited_once()


@pytest.mark.asyncio
async def test_append_audit_falls_back_to_fourth_estate_when_no_repo():
    service = ConsentService(consent_repo=AsyncMock())
    service._db = MagicMock()
    service._audit_repo = None

    with patch("app.modules.consent.service.FourthEstateService") as fourth_estate_cls:
        instance = fourth_estate_cls.return_value
        instance.record = AsyncMock()

        await service._append_audit(
            "consent.granted",
            actor_id="guardian-1",
            resource_id="consent-1",
            payload={"ok": True},
        )

        instance.record.assert_awaited_once()


@pytest.mark.asyncio
async def test_record_version_history_no_db_noop():
    service = ConsentService(consent_repo=AsyncMock())
    consent = SimpleNamespace(
        id="consent-1",
        policy_version="1.0.0",
        granted_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        revoked_at=None,
    )

    await service._record_version_history(consent, "granted", "initial_grant")


@pytest.mark.asyncio
async def test_record_version_history_writes_with_db():
    db = MagicMock()
    db.flush = AsyncMock()
    service = ConsentService(consent_repo=AsyncMock())
    service._db = db

    consent = SimpleNamespace(
        id="consent-1",
        policy_version="1.0.0",
        granted_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        revoked_at=None,
    )

    await service._record_version_history(consent, "granted", "initial_grant")

    db.add.assert_called_once()
    db.flush.assert_awaited_once()
