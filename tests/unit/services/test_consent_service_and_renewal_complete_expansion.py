"""Comprehensive expansion unit tests for consent_service.py and consent_renewal_service.py."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.domain.consent import (
    AuditEventType,
    ConsentRecord,
    ConsentState,
)
from app.services.consent_service import ConsentService
from app.services.consent_renewal_service import (
    ConsentRenewalService,
    SendGridEmailGateway,
)


# ==============================================================================
# ConsentService Comprehensive Tests
# ==============================================================================

class TestConsentServiceExpansion:
    @pytest.fixture
    def mock_repos(self):
        consent_repo = AsyncMock()
        audit_repo = AsyncMock()
        return consent_repo, audit_repo

    @pytest.fixture
    def service(self, mock_repos):
        consent_repo, audit_repo = mock_repos
        return ConsentService(consent_repo, audit_repo)

    @pytest.mark.asyncio
    async def test_grant_new_record(self, service, mock_repos):
        consent_repo, audit_repo = mock_repos
        consent_repo.get_active_for_learner.return_value = None

        learner_id = uuid.uuid4()
        guardian_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        version = "v1.0"

        created_record = ConsentRecord(
            learner_id=learner_id,
            guardian_id=guardian_id,
            privacy_notice_version=version,
            state=ConsentState.GRANTED,
        )
        consent_repo.create.return_value = created_record

        record = await service.grant(learner_id, guardian_id, version, actor_id)

        assert record == created_record
        consent_repo.create.assert_awaited_once()
        audit_repo.record.assert_awaited_once_with(
            AuditEventType.CONSENT_GRANT,
            actor_id=actor_id,
            learner_id=learner_id,
            payload={
                "consent_id": str(created_record.id),
                "privacy_notice_version": version,
                "expires_at": created_record.expires_at.isoformat() if created_record.expires_at else None,
            },
        )

    @pytest.mark.asyncio
    async def test_grant_existing_record(self, service, mock_repos):
        consent_repo, audit_repo = mock_repos
        learner_id = uuid.uuid4()
        guardian_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        version = "v2.0"

        existing = ConsentRecord(
            learner_id=learner_id,
            guardian_id=guardian_id,
            privacy_notice_version="v1.0",
            state=ConsentState.PENDING,
        )
        consent_repo.get_active_for_learner.return_value = existing
        updated = existing.grant(version)
        consent_repo.update.return_value = updated

        record = await service.grant(learner_id, guardian_id, version, actor_id)

        assert record.privacy_notice_version == version
        consent_repo.update.assert_awaited_once()
        audit_repo.record.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_deny_new_record(self, service, mock_repos):
        consent_repo, audit_repo = mock_repos
        consent_repo.get_active_for_learner.return_value = None

        learner_id = uuid.uuid4()
        guardian_id = uuid.uuid4()
        actor_id = uuid.uuid4()

        denied_record = ConsentRecord(
            learner_id=learner_id,
            guardian_id=guardian_id,
            privacy_notice_version="v1.0",
            state=ConsentState.DENIED,
        )
        consent_repo.create.return_value = denied_record

        record = await service.deny(
            learner_id, guardian_id, "v1.0", actor_id, reason="Guardian opted out"
        )
        assert record == denied_record
        consent_repo.create.assert_awaited_once()
        audit_repo.record.assert_awaited_once_with(
            AuditEventType.CONSENT_DENIAL,
            actor_id=actor_id,
            learner_id=learner_id,
            payload={"consent_id": str(denied_record.id), "reason": "Guardian opted out"},
        )

    @pytest.mark.asyncio
    async def test_deny_existing_record(self, service, mock_repos):
        consent_repo, audit_repo = mock_repos
        learner_id = uuid.uuid4()
        guardian_id = uuid.uuid4()
        actor_id = uuid.uuid4()

        existing = ConsentRecord(
            learner_id=learner_id,
            guardian_id=guardian_id,
            privacy_notice_version="v1.0",
            state=ConsentState.PENDING,
        )
        consent_repo.get_active_for_learner.return_value = existing
        updated = existing.deny("Guardian refused")
        consent_repo.update.return_value = updated

        record = await service.deny(
            learner_id, guardian_id, "v1.0", actor_id, reason="Guardian refused"
        )
        assert record.state == ConsentState.DENIED
        consent_repo.update.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_withdraw(self, service, mock_repos):
        consent_repo, audit_repo = mock_repos
        learner_id = uuid.uuid4()
        actor_id = uuid.uuid4()

        record = ConsentRecord(
            learner_id=learner_id,
            guardian_id=uuid.uuid4(),
            privacy_notice_version="v1.0",
            state=ConsentState.GRANTED,
        )
        consent_repo.get_active_for_learner.return_value = record
        updated = record.withdraw()
        consent_repo.update.return_value = updated

        saved = await service.withdraw(learner_id, actor_id)
        assert saved.state == ConsentState.WITHDRAWN
        consent_repo.update.assert_awaited_once()
        audit_repo.record.assert_awaited_once_with(
            AuditEventType.CONSENT_WITHDRAWAL,
            actor_id=actor_id,
            learner_id=learner_id,
            payload={"consent_id": str(saved.id)},
        )

    @pytest.mark.asyncio
    async def test_renew(self, service, mock_repos):
        consent_repo, audit_repo = mock_repos
        learner_id = uuid.uuid4()
        actor_id = uuid.uuid4()

        record = ConsentRecord(
            learner_id=learner_id,
            guardian_id=uuid.uuid4(),
            privacy_notice_version="v1.0",
            state=ConsentState.GRANTED,
        )
        consent_repo.get_active_for_learner.return_value = record
        updated = record.renew("v2.0")
        consent_repo.update.return_value = updated

        saved = await service.renew(learner_id, actor_id, "v2.0")
        assert saved.privacy_notice_version == "v2.0"
        assert saved.state == ConsentState.GRANTED
        consent_repo.update.assert_awaited_once()
        audit_repo.record.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_process_expiry(self, service, mock_repos):
        consent_repo, audit_repo = mock_repos
        learner_id = uuid.uuid4()

        record = ConsentRecord(
            learner_id=learner_id,
            guardian_id=uuid.uuid4(),
            privacy_notice_version="v1.0",
            state=ConsentState.GRANTED,
        )
        consent_repo.get_active_for_learner.return_value = record
        updated = record.mark_expired()
        consent_repo.update.return_value = updated

        saved = await service.process_expiry(learner_id)
        assert saved.state == ConsentState.EXPIRED
        consent_repo.update.assert_awaited_once()
        audit_repo.record.assert_awaited_once_with(
            AuditEventType.CONSENT_EXPIRY,
            actor_id=None,
            learner_id=learner_id,
            payload={"consent_id": str(saved.id)},
        )

    @pytest.mark.asyncio
    async def test_assert_active_consent_success(self, service, mock_repos):
        consent_repo, _ = mock_repos
        learner_id = uuid.uuid4()

        now = datetime.now(timezone.utc)
        record = ConsentRecord(
            learner_id=learner_id,
            guardian_id=uuid.uuid4(),
            privacy_notice_version="v1.0",
            state=ConsentState.GRANTED,
            granted_at=now,
            expires_at=now + timedelta(days=100),
        )
        consent_repo.get_active_for_learner.return_value = record

        res = await service.assert_active_consent(learner_id)
        assert res == record

    @pytest.mark.asyncio
    async def test_assert_active_consent_fails_when_none(self, service, mock_repos):
        consent_repo, _ = mock_repos
        learner_id = uuid.uuid4()
        consent_repo.get_active_for_learner.return_value = None

        with pytest.raises(PermissionError, match="No active POPIA consent"):
            await service.assert_active_consent(learner_id)

    @pytest.mark.asyncio
    async def test_assert_active_consent_fails_when_inactive(self, service, mock_repos):
        consent_repo, _ = mock_repos
        learner_id = uuid.uuid4()
        record = ConsentRecord(
            learner_id=learner_id,
            guardian_id=uuid.uuid4(),
            privacy_notice_version="v1.0",
            state=ConsentState.EXPIRED,
        )
        consent_repo.get_active_for_learner.return_value = record

        with pytest.raises(PermissionError, match="Access is restricted"):
            await service.assert_active_consent(learner_id)

    @pytest.mark.asyncio
    async def test_require_consent_record_raises_value_error(self, service, mock_repos):
        consent_repo, _ = mock_repos
        learner_id = uuid.uuid4()
        consent_repo.get_active_for_learner.return_value = None

        with pytest.raises(ValueError, match="No consent record found"):
            await service._require_consent_record(learner_id)

    @pytest.mark.asyncio
    async def test_flag_approaching_renewals(self, service, mock_repos):
        consent_repo, audit_repo = mock_repos
        learner_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        record = ConsentRecord(
            learner_id=learner_id,
            guardian_id=uuid.uuid4(),
            privacy_notice_version="v1.0",
            state=ConsentState.GRANTED,
            granted_at=now - timedelta(days=300),
            expires_at=now + timedelta(days=15),
        )
        consent_repo.list_expiring_soon.return_value = [record]
        updated = record.mark_renewal_required()
        consent_repo.update.return_value = updated

        flagged = await service.flag_approaching_renewals()
        assert len(flagged) == 1
        assert flagged[0].state == ConsentState.RENEWAL_REQUIRED
        consent_repo.update.assert_awaited_once()
        audit_repo.record.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_emit_runtime_consent_audit(self, service):
        service.audit_repository = AsyncMock()
        with patch("app.services.consent_service.emit_consent_runtime_event", new_callable=AsyncMock) as mock_emit:
            mock_emit.return_value = {"status": "ok"}
            res = await service._emit_runtime_consent_audit(
                action="consent.verified",
                learner_id=str(uuid.uuid4()),
                actor_id=str(uuid.uuid4()),
                metadata={"test": 1},
            )
            assert res == {"status": "ok"}
            mock_emit.assert_awaited_once()


# ==============================================================================
# ConsentRenewalService & SendGridEmailGateway Tests
# ==============================================================================

class TestConsentRenewalServiceExpansion:
    @pytest.fixture
    def dummy_settings(self):
        class Settings:
            SENDGRID_API_KEY = "test-key"
            SENDGRID_FROM_EMAIL = "noreply@eduboost.co.za"
            APP_BASE_URL = "https://eduboost.co.za"
            ENCRYPTION_KEY = "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE="
        return Settings()

    def test_sendgrid_gateway_get_client_import_error(self, dummy_settings):
        gateway = SendGridEmailGateway(dummy_settings)
        with patch.dict("sys.modules", {"sendgrid": None}):
            with pytest.raises(RuntimeError, match="sendgrid package is required"):
                gateway._get_client()

    def test_sendgrid_gateway_get_client_success(self, dummy_settings):
        gateway = SendGridEmailGateway(dummy_settings)
        mock_sg = MagicMock()
        with patch.dict("sys.modules", {"sendgrid": mock_sg}):
            client = gateway._get_client()
            assert client is not None
            mock_sg.SendGridAPIClient.assert_called_once_with(api_key="test-key")

    def test_decrypt_email_success_and_error(self, dummy_settings):
        from cryptography.fernet import Fernet
        fernet = Fernet(dummy_settings.ENCRYPTION_KEY.encode())
        encrypted = fernet.encrypt(b"parent@example.com").decode()

        gateway = SendGridEmailGateway(dummy_settings)
        decrypted = gateway._decrypt_email(encrypted)
        assert decrypted == "parent@example.com"

        with pytest.raises(ValueError, match="Failed to decrypt"):
            gateway._decrypt_email("invalid_ciphertext")

    @pytest.mark.asyncio
    async def test_send_renewal_reminder_success(self, dummy_settings):
        from cryptography.fernet import Fernet
        fernet = Fernet(dummy_settings.ENCRYPTION_KEY.encode())
        encrypted = fernet.encrypt(b"parent@example.com").decode()

        gateway = SendGridEmailGateway(dummy_settings)
        mock_client = MagicMock()
        mock_response = MagicMock(status_code=202)
        mock_client.send.return_value = mock_response
        gateway._client = mock_client

        res = await gateway.send_renewal_reminder(
            to_encrypted_email=encrypted,
            guardian_id="g123",
            consent_id="c123",
            expires_at=datetime.now(timezone.utc) + timedelta(days=10),
            renewal_url="https://eduboost.co.za/renew",
        )
        assert res is True
        mock_client.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_renewal_reminder_status_code_failed(self, dummy_settings):
        from cryptography.fernet import Fernet
        fernet = Fernet(dummy_settings.ENCRYPTION_KEY.encode())
        encrypted = fernet.encrypt(b"parent@example.com").decode()

        gateway = SendGridEmailGateway(dummy_settings)
        mock_client = MagicMock()
        mock_response = MagicMock(status_code=400)
        mock_client.send.return_value = mock_response
        gateway._client = mock_client

        res = await gateway.send_renewal_reminder(
            to_encrypted_email=encrypted,
            guardian_id="g123",
            consent_id="c123",
            expires_at=datetime.now(timezone.utc) + timedelta(days=10),
            renewal_url="https://eduboost.co.za/renew",
        )
        assert res is False

    @pytest.mark.asyncio
    async def test_send_renewal_reminder_exception(self, dummy_settings):
        gateway = SendGridEmailGateway(dummy_settings)
        res = await gateway.send_renewal_reminder(
            to_encrypted_email="bad_encrypted",
            guardian_id="g123",
            consent_id="c123",
            expires_at=datetime.now(timezone.utc),
            renewal_url="https://eduboost.co.za/renew",
        )
        assert res is False

    @pytest.mark.asyncio
    async def test_consent_renewal_service_run_workflow(self, dummy_settings):
        mock_db = AsyncMock()
        mock_gateway = AsyncMock()
        service = ConsentRenewalService(mock_db, mock_gateway, dummy_settings, days_threshold=30)

        now = datetime.now(timezone.utc)

        # Consent 1: already expired -> skipped
        c1 = MagicMock(id="c1", guardian_id="g1", expires_at=now - timedelta(days=1))
        # Consent 2: guardian not found -> failed
        c2 = MagicMock(id="c2", guardian_id="g2", expires_at=now + timedelta(days=10))
        # Consent 3: sent successfully -> reminded
        c3 = MagicMock(id="c3", guardian_id="g3", expires_at=now + timedelta(days=20))
        # Consent 4: send failed -> failed
        c4 = MagicMock(id="c4", guardian_id="g4", expires_at=now + timedelta(days=25))

        service._fetch_expiring_consents = AsyncMock(return_value=[c1, c2, c3, c4])

        g3 = MagicMock(id="g3", email_encrypted="enc3")
        g4 = MagicMock(id="g4", email_encrypted="enc4")

        async def fake_fetch_guardian(gid):
            if gid == "g2":
                return None
            if gid == "g3":
                return g3
            if gid == "g4":
                return g4
            return None

        service._fetch_guardian = AsyncMock(side_effect=fake_fetch_guardian)
        mock_gateway.send_renewal_reminder.side_effect = [True, False]

        stats = await service.run()

        assert stats["checked"] == 4
        assert stats["skipped_already_expired"] == 1
        assert stats["failed"] == 2  # g2 not found, g4 send failed
        assert stats["reminded"] == 1

    @pytest.mark.asyncio
    async def test_fetch_expiring_consents_import_fallback(self, dummy_settings):
        mock_db = AsyncMock()
        mock_gateway = AsyncMock()
        service = ConsentRenewalService(mock_db, mock_gateway, dummy_settings)

        # Normal execution with db mock returning scalars
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = ["consent1"]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        consents = await service._fetch_expiring_consents()
        assert consents == ["consent1"]

    @pytest.mark.asyncio
    async def test_fetch_guardian_execution(self, dummy_settings):
        mock_db = AsyncMock()
        mock_gateway = AsyncMock()
        service = ConsentRenewalService(mock_db, mock_gateway, dummy_settings)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock(id="g123")
        mock_db.execute.return_value = mock_result

        guardian = await service._fetch_guardian("g123")
        assert guardian.id == "g123"

    def test_build_renewal_url(self, dummy_settings):
        service = ConsentRenewalService(AsyncMock(), AsyncMock(), dummy_settings)
        url = service._build_renewal_url(consent_id="c999", guardian_id="g888")
        assert url == "https://eduboost.co.za/consent/renew?consent_id=c999&guardian_id=g888"


# ==============================================================================
# Consent Expiry Scan Execution Test
# ==============================================================================

@pytest.mark.asyncio
async def test_run_consent_expiry_scan():
    from app.services.consent_expiry_service import run_consent_expiry_scan

    with patch("app.services.consent_expiry_service.ConsentRenewalService") as mock_service_cls:
        mock_inst = AsyncMock()
        mock_inst.run.return_value = {"reminded": 7}
        mock_service_cls.return_value = mock_inst

        with patch("app.services.consent_expiry_service.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            mock_session_local.return_value.__aexit__.return_value = None

            reminded = await run_consent_expiry_scan()
            assert reminded == 7
