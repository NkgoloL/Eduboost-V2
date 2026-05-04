"""
Integration Tests — POPIA Annual Consent Renewal Reminder  (Task #24)
======================================================================
Run: pytest tests/integration/test_consent_renewal.py -v
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Minimal fakes — no ORM dependency required for unit-level coverage
# ---------------------------------------------------------------------------

class FakeConsent:
    def __init__(self, id, guardian_id, expires_at, is_active=True):
        self.id = id
        self.guardian_id = guardian_id
        self.expires_at = expires_at
        self.is_active = is_active


class FakeGuardian:
    def __init__(self, id, email_encrypted=b"enc_email"):
        self.id = id
        self.email_encrypted = email_encrypted


class FakeSettings:
    SENDGRID_API_KEY = "SG.test"
    SENDGRID_FROM_EMAIL = "no-reply@eduboost.co.za"
    APP_BASE_URL = "https://eduboost.co.za"
    ENCRYPTION_KEY = "A" * 44  # placeholder Fernet-length key


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_service(db, gateway, days=30):
    """Construct a ConsentRenewalService with fakes, bypassing ORM imports."""
    from app.services.consent_renewal_service import ConsentRenewalService  # type: ignore
    return ConsentRenewalService(db, gateway, FakeSettings(), days_threshold=days)


# ---------------------------------------------------------------------------
# Test suite
# ---------------------------------------------------------------------------

class TestConsentRenewalService:

    @pytest.mark.asyncio
    async def test_sends_reminder_for_expiring_consent(self):
        """Happy path: one consent expiring in 15 days → one email sent."""
        from app.services.consent_renewal_service import ConsentRenewalService

        now = datetime.now(tz=timezone.utc)
        expiring_consent = FakeConsent(
            id="consent-001",
            guardian_id="guardian-001",
            expires_at=now + timedelta(days=15),
        )
        guardian = FakeGuardian(id="guardian-001")

        gateway = AsyncMock()
        gateway.send_renewal_reminder = AsyncMock(return_value=True)

        service = ConsentRenewalService.__new__(ConsentRenewalService)
        service._db = MagicMock()
        service._email_gateway = gateway
        service._settings = FakeSettings()
        service._days_threshold = 30

        # Patch internal fetch methods
        service._fetch_expiring_consents = AsyncMock(return_value=[expiring_consent])
        service._fetch_guardian = AsyncMock(return_value=guardian)
        service._build_renewal_url = MagicMock(
            return_value="https://eduboost.co.za/consent/renew?consent_id=consent-001&guardian_id=guardian-001"
        )

        stats = await service.run()

        assert stats["checked"] == 1
        assert stats["reminded"] == 1
        assert stats["failed"] == 0
        assert stats["skipped_already_expired"] == 0
        gateway.send_renewal_reminder.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_skips_already_expired_consent(self):
        """Consents that are already past expiry are skipped (not reminded)."""
        from app.services.consent_renewal_service import ConsentRenewalService

        now = datetime.now(tz=timezone.utc)
        expired_consent = FakeConsent(
            id="consent-002",
            guardian_id="guardian-002",
            expires_at=now - timedelta(days=1),   # already expired
        )

        gateway = AsyncMock()
        service = ConsentRenewalService.__new__(ConsentRenewalService)
        service._db = MagicMock()
        service._email_gateway = gateway
        service._settings = FakeSettings()
        service._days_threshold = 30
        service._fetch_expiring_consents = AsyncMock(return_value=[expired_consent])
        service._fetch_guardian = AsyncMock()

        stats = await service.run()

        assert stats["skipped_already_expired"] == 1
        assert stats["reminded"] == 0
        gateway.send_renewal_reminder.assert_not_called()

    @pytest.mark.asyncio
    async def test_records_failure_when_email_dispatch_fails(self):
        """If SendGrid returns False, the record is counted as failed."""
        from app.services.consent_renewal_service import ConsentRenewalService

        now = datetime.now(tz=timezone.utc)
        consent = FakeConsent(
            id="consent-003",
            guardian_id="guardian-003",
            expires_at=now + timedelta(days=5),
        )
        guardian = FakeGuardian(id="guardian-003")

        gateway = AsyncMock()
        gateway.send_renewal_reminder = AsyncMock(return_value=False)  # delivery failure

        service = ConsentRenewalService.__new__(ConsentRenewalService)
        service._db = MagicMock()
        service._email_gateway = gateway
        service._settings = FakeSettings()
        service._days_threshold = 30
        service._fetch_expiring_consents = AsyncMock(return_value=[consent])
        service._fetch_guardian = AsyncMock(return_value=guardian)
        service._build_renewal_url = MagicMock(return_value="https://eduboost.co.za/renew")

        stats = await service.run()

        assert stats["failed"] == 1
        assert stats["reminded"] == 0

    @pytest.mark.asyncio
    async def test_records_failure_when_guardian_not_found(self):
        """If the guardian record is missing, the consent is counted as failed."""
        from app.services.consent_renewal_service import ConsentRenewalService

        now = datetime.now(tz=timezone.utc)
        consent = FakeConsent(
            id="consent-004",
            guardian_id="ghost-guardian",
            expires_at=now + timedelta(days=10),
        )

        gateway = AsyncMock()
        service = ConsentRenewalService.__new__(ConsentRenewalService)
        service._db = MagicMock()
        service._email_gateway = gateway
        service._settings = FakeSettings()
        service._days_threshold = 30
        service._fetch_expiring_consents = AsyncMock(return_value=[consent])
        service._fetch_guardian = AsyncMock(return_value=None)  # not found

        stats = await service.run()

        assert stats["failed"] == 1
        gateway.send_renewal_reminder.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_run_produces_zero_stats(self):
        """No expiring consents → all stats are zero."""
        from app.services.consent_renewal_service import ConsentRenewalService

        gateway = AsyncMock()
        service = ConsentRenewalService.__new__(ConsentRenewalService)
        service._db = MagicMock()
        service._email_gateway = gateway
        service._settings = FakeSettings()
        service._days_threshold = 30
        service._fetch_expiring_consents = AsyncMock(return_value=[])

        stats = await service.run()

        assert stats == {
            "checked": 0,
            "reminded": 0,
            "failed": 0,
            "skipped_already_expired": 0,
        }

    @pytest.mark.asyncio
    async def test_mixed_batch(self):
        """Batch with valid, already-expired, and missing-guardian records."""
        from app.services.consent_renewal_service import ConsentRenewalService

        now = datetime.now(tz=timezone.utc)
        consents = [
            FakeConsent("c1", "g1", now + timedelta(days=5)),   # should remind
            FakeConsent("c2", "g2", now - timedelta(days=1)),   # already expired → skip
            FakeConsent("c3", "g3", now + timedelta(days=20)),  # guardian missing → fail
        ]

        gateway = AsyncMock()
        gateway.send_renewal_reminder = AsyncMock(return_value=True)

        service = ConsentRenewalService.__new__(ConsentRenewalService)
        service._db = MagicMock()
        service._email_gateway = gateway
        service._settings = FakeSettings()
        service._days_threshold = 30

        async def fake_fetch_guardian(guardian_id):
            if guardian_id == "g1":
                return FakeGuardian(id="g1")
            return None  # g3 not found

        service._fetch_expiring_consents = AsyncMock(return_value=consents)
        service._fetch_guardian = AsyncMock(side_effect=fake_fetch_guardian)
        service._build_renewal_url = MagicMock(return_value="https://eduboost.co.za/renew")

        stats = await service.run()

        assert stats["checked"] == 3
        assert stats["reminded"] == 1
        assert stats["failed"] == 1
        assert stats["skipped_already_expired"] == 1

    def test_build_renewal_url_uses_settings_base_url(self):
        """Renewal URL is constructed from APP_BASE_URL in settings."""
        from app.services.consent_renewal_service import ConsentRenewalService

        service = ConsentRenewalService.__new__(ConsentRenewalService)
        service._settings = FakeSettings()

        url = service._build_renewal_url(
            consent_id="consent-xyz", guardian_id="guardian-abc"
        )

        assert url.startswith("https://eduboost.co.za")
        assert "consent_id=consent-xyz" in url
        assert "guardian_id=guardian-abc" in url

    def test_html_email_contains_renewal_link(self):
        """The HTML email body must include the renewal link and POPIA reference."""
        from app.services.consent_renewal_service import SendGridEmailGateway

        html = SendGridEmailGateway._build_html(
            days_left=14, renewal_url="https://eduboost.co.za/consent/renew?id=1"
        )

        assert "https://eduboost.co.za/consent/renew?id=1" in html
        assert "POPIA" in html
        assert "14 day(s)" in html

    def test_html_email_urgency_threshold(self):
        """Emails within 7 days should flag as urgent."""
        from app.services.consent_renewal_service import SendGridEmailGateway

        html_urgent = SendGridEmailGateway._build_html(
            days_left=3, renewal_url="https://example.com"
        )
        html_upcoming = SendGridEmailGateway._build_html(
            days_left=20, renewal_url="https://example.com"
        )

        assert "urgent" in html_urgent
        assert "upcoming" in html_upcoming
