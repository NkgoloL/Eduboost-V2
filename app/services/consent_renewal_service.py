"""
Consent Renewal Reminder Service — Task #24
============================================
POPIA §18 requires guardians to renew parental consent annually.
This service queries for ParentalConsent records expiring within 30 days
and dispatches SendGrid reminder emails with a renewal link.

Designed to run as:
  - A FastAPI BackgroundTask (V2 path)
  - A daily scheduled job via arq (if configured)
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Protocol, Sequence

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------

class ConsentRecord(Protocol):
    """Structural typing — matches the SQLAlchemy ParentalConsent ORM model."""
    id: str
    guardian_id: str
    expires_at: datetime
    is_active: bool


class GuardianRecord(Protocol):
    """Structural typing — matches the SQLAlchemy Guardian ORM model."""
    id: str
    email_hash: str          # SHA-256 hash — never plaintext
    email_encrypted: bytes   # AES-encrypted ciphertext


# ---------------------------------------------------------------------------
# Email gateway abstraction (pluggable for testing)
# ---------------------------------------------------------------------------

class EmailGateway(Protocol):
    async def send_renewal_reminder(
        self,
        *,
        to_encrypted_email: bytes,
        guardian_id: str,
        consent_id: str,
        expires_at: datetime,
        renewal_url: str,
    ) -> bool:
        """Return True if the email was dispatched successfully."""
        ...


# ---------------------------------------------------------------------------
# SendGrid implementation
# ---------------------------------------------------------------------------

class SendGridEmailGateway:
    """
    Sends renewal reminder emails via SendGrid.

    Requires in settings:
      SENDGRID_API_KEY       — SendGrid API key
      SENDGRID_FROM_EMAIL    — verified sender address
      APP_BASE_URL           — e.g. https://eduboost.co.za
      ENCRYPTION_KEY         — Fernet key used to decrypt email ciphertext
    """

    def __init__(self, settings) -> None:
        self._settings = settings
        self._client = None  # lazy-initialised

    def _get_client(self):
        if self._client is None:
            try:
                import sendgrid  # type: ignore[import]
                self._client = sendgrid.SendGridAPIClient(
                    api_key=self._settings.SENDGRID_API_KEY
                )
            except ImportError as exc:
                raise RuntimeError(
                    "sendgrid package is required. "
                    "Add 'sendgrid' to requirements/base.txt."
                ) from exc
        return self._client

    def _decrypt_email(self, ciphertext: bytes) -> str:
        """Decrypt the guardian's email address for sending."""
        try:
            from cryptography.fernet import Fernet  # type: ignore[import]
            key = self._settings.ENCRYPTION_KEY.encode()
            return Fernet(key).decrypt(ciphertext).decode()
        except Exception as exc:
            raise ValueError(f"Failed to decrypt guardian email: {exc}") from exc

    async def send_renewal_reminder(
        self,
        *,
        to_encrypted_email: bytes,
        guardian_id: str,
        consent_id: str,
        expires_at: datetime,
        renewal_url: str,
    ) -> bool:
        try:
            from sendgrid.helpers.mail import Mail  # type: ignore[import]

            to_email = self._decrypt_email(to_encrypted_email)
            days_left = (expires_at - datetime.now(tz=timezone.utc)).days

            message = Mail(
                from_email=self._settings.SENDGRID_FROM_EMAIL,
                to_emails=to_email,
                subject="Action Required: Renew Your EduBoost Parental Consent",
                html_content=self._build_html(
                    days_left=days_left,
                    renewal_url=renewal_url,
                ),
            )

            client = self._get_client()
            response = client.send(message)
            success = response.status_code in (200, 202)

            if success:
                logger.info(
                    "consent_renewal_reminder_sent",
                    extra={
                        "guardian_id": guardian_id,
                        "consent_id": consent_id,
                        "days_until_expiry": days_left,
                    },
                )
            else:
                logger.warning(
                    "consent_renewal_reminder_failed",
                    extra={
                        "guardian_id": guardian_id,
                        "consent_id": consent_id,
                        "sendgrid_status": response.status_code,
                    },
                )
            return success

        except Exception as exc:  # noqa: BLE001
            logger.error(
                "consent_renewal_reminder_error",
                extra={"guardian_id": guardian_id, "error": str(exc)},
            )
            return False

    @staticmethod
    def _build_html(*, days_left: int, renewal_url: str) -> str:
        urgency = "urgent" if days_left <= 7 else "upcoming"
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
          <h2>🦁 EduBoost SA — Parental Consent Renewal</h2>
          <p>Your parental consent is <strong>{urgency}</strong> — it expires
             in <strong>{days_left} day(s)</strong>.</p>
          <p>Under POPIA (Protection of Personal Information Act), we are required
             to obtain renewed consent annually to continue providing personalised
             learning for your child.</p>
          <p>
            <a href="{renewal_url}"
               style="background:#2563eb;color:#fff;padding:12px 24px;
                      border-radius:6px;text-decoration:none;display:inline-block;">
              Renew Consent Now
            </a>
          </p>
          <p style="color:#888;font-size:12px;">
            If you did not expect this email, or would like to revoke consent,
            please contact support@eduboost.co.za.<br/>
            EduBoost SA · POPIA Compliant · South Africa
          </p>
        </body>
        </html>
        """


# ---------------------------------------------------------------------------
# Core service
# ---------------------------------------------------------------------------

class ConsentRenewalService:
    """
    Queries for ParentalConsent records expiring within ``days_threshold``
    and dispatches renewal reminder emails via the injected EmailGateway.

    Usage (FastAPI BackgroundTask — V2 path):
        background_tasks.add_task(
            ConsentRenewalService(db, gateway, settings).run
        )

    Usage (arq worker):
        await ConsentRenewalService(db, gateway, settings).run()
    """

    def __init__(
        self,
        db: AsyncSession,
        email_gateway: EmailGateway,
        settings,
        *,
        days_threshold: int = 30,
    ) -> None:
        self._db = db
        self._email_gateway = email_gateway
        self._settings = settings
        self._days_threshold = days_threshold

    async def run(self) -> dict:
        """
        Main entry point.  Returns a summary dict suitable for logging.

        Returns:
            {
                "checked": int,
                "reminded": int,
                "failed": int,
                "skipped_already_expired": int,
            }
        """
        expiring = await self._fetch_expiring_consents()

        stats = {
            "checked": len(expiring),
            "reminded": 0,
            "failed": 0,
            "skipped_already_expired": 0,
        }

        now = datetime.now(tz=timezone.utc)

        for consent in expiring:
            if consent.expires_at <= now:
                stats["skipped_already_expired"] += 1
                continue

            guardian = await self._fetch_guardian(consent.guardian_id)
            if guardian is None:
                logger.warning(
                    "consent_renewal_guardian_not_found",
                    extra={"consent_id": consent.id, "guardian_id": consent.guardian_id},
                )
                stats["failed"] += 1
                continue

            renewal_url = self._build_renewal_url(
                consent_id=consent.id, guardian_id=consent.guardian_id
            )

            sent = await self._email_gateway.send_renewal_reminder(
                to_encrypted_email=guardian.email_encrypted,
                guardian_id=guardian.id,
                consent_id=consent.id,
                expires_at=consent.expires_at,
                renewal_url=renewal_url,
            )

            if sent:
                stats["reminded"] += 1
            else:
                stats["failed"] += 1

        logger.info("consent_renewal_run_complete", extra=stats)
        return stats

    async def _fetch_expiring_consents(self) -> Sequence:
        """Return active consents expiring within the threshold window."""
        try:
            from sqlalchemy import select as sa_select  # type: ignore[import]
            from app.models import ParentalConsent  # type: ignore[import]
        except ImportError:
            # Fallback for unit-test environments without the full ORM.
            return []

        cutoff = datetime.now(tz=timezone.utc) + timedelta(days=self._days_threshold)
        result = await self._db.execute(
            sa_select(ParentalConsent).where(
                ParentalConsent.is_active == True,  # noqa: E712
                ParentalConsent.expires_at <= cutoff,
            )
        )
        return result.scalars().all()

    async def _fetch_guardian(self, guardian_id: str):
        try:
            from sqlalchemy import select as sa_select  # type: ignore[import]
            from app.models import Guardian  # type: ignore[import]
        except ImportError:
            return None

        result = await self._db.execute(
            sa_select(Guardian).where(Guardian.id == guardian_id)
        )
        return result.scalar_one_or_none()

    def _build_renewal_url(self, *, consent_id: str, guardian_id: str) -> str:
        base = getattr(self._settings, "APP_BASE_URL", "https://eduboost.co.za")
        return f"{base}/consent/renew?consent_id={consent_id}&guardian_id={guardian_id}"
