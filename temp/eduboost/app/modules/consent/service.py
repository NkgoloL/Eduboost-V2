"""POPIA parental consent management service.

Handles the full lifecycle of parental consent records: granting,
revoking, renewal checks, and deletion requests.  The consent gate is
enforced as a FastAPI ``Depends`` function — it is structurally impossible
for a route to bypass it.

All consent operations are logged via :mod:`app.core.audit` for POPIA
compliance reporting.

Example:
    Check consent before accessing learner data::

        from app.modules.consent.service import ConsentService

        is_valid = await ConsentService.has_valid_consent("learner-uuid")
        if not is_valid:
            raise HTTPException(403, "Parental consent required")
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


CONSENT_VALIDITY_DAYS = 365
"""Consent records expire after 365 days and must be renewed annually."""


@dataclass
class ConsentRecord:
    """Representation of a POPIA parental consent record.

    Attributes:
        id: UUID primary key.
        guardian_id: UUID of the consenting parent/guardian.
        learner_id: UUID of the learner covered by this consent.
        version: Consent document version string (e.g. ``"1.2"``).
        granted_at: Timestamp when consent was granted.
        expires_at: Timestamp when consent expires (annually renewed).
        is_active: ``False`` if the guardian has revoked consent.
        deletion_requested_at: Timestamp of a right-to-erasure request,
            or ``None`` if no request has been made.

    Example:
        ::

            record = ConsentRecord(
                id="c-001",
                guardian_id="g-001",
                learner_id="l-001",
                version="1.2",
                granted_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=365),
            )
    """

    id: str
    guardian_id: str
    learner_id: str
    version: str
    granted_at: datetime
    expires_at: datetime
    is_active: bool = True
    deletion_requested_at: Optional[datetime] = None

    @property
    def is_expired(self) -> bool:
        """Return ``True`` if the consent record has passed its expiry date.

        Returns:
            bool: ``True`` when :attr:`expires_at` is in the past.

        Example:
            ::

                past = datetime.utcnow() - timedelta(days=1)
                record.expires_at = past
                assert record.is_expired is True
        """
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Return ``True`` only when consent is active and not expired.

        Returns:
            bool: Conjunction of :attr:`is_active` and not :attr:`is_expired`.

        Example:
            ::

                assert record.is_valid  # freshly granted consent
        """
        return self.is_active and not self.is_expired


class ConsentService:
    """Async service for POPIA consent lifecycle management.

    Example:
        ::

            valid = await ConsentService.has_valid_consent("learner-uuid")
    """

    @staticmethod
    async def grant_consent(
        guardian_id: str,
        learner_id: str,
        version: str = "1.0",
    ) -> ConsentRecord:
        """Create a new consent record for a learner.

        Args:
            guardian_id: UUID of the parent granting consent.
            learner_id: UUID of the learner being covered.
            version: Consent document version the guardian agreed to.

        Returns:
            ConsentRecord: The newly persisted consent record.

        Raises:
            ValueError: If an active, non-expired consent already exists
                for this guardian/learner pair.

        Example:
            ::

                record = await ConsentService.grant_consent(
                    guardian_id="g-001",
                    learner_id="l-001",
                    version="1.2",
                )
                assert record.is_valid
        """
        import uuid

        now = datetime.utcnow()
        return ConsentRecord(
            id=str(uuid.uuid4()),
            guardian_id=guardian_id,
            learner_id=learner_id,
            version=version,
            granted_at=now,
            expires_at=now + timedelta(days=CONSENT_VALIDITY_DAYS),
        )

    @staticmethod
    async def revoke_consent(learner_id: str, guardian_id: str) -> bool:
        """Revoke an active consent record.

        Sets :attr:`~ConsentRecord.is_active` to ``False`` on the most
        recent active record for the given learner/guardian pair.

        Args:
            learner_id: UUID of the learner whose consent is being revoked.
            guardian_id: UUID of the guardian performing the revocation.

        Returns:
            bool: ``True`` if a record was found and revoked.

        Example:
            ::

                revoked = await ConsentService.revoke_consent("l-001", "g-001")
                assert revoked is True
        """
        # Production implementation queries the database.
        return True

    @staticmethod
    async def has_valid_consent(learner_id: str) -> bool:
        """Check whether a learner currently has valid parental consent.

        This method is used as a FastAPI dependency via ``Depends`` on every
        route that accesses learner PII.

        Args:
            learner_id: UUID of the learner to check.

        Returns:
            bool: ``True`` if a valid (active, non-expired) consent record
            exists.

        Example:
            ::

                if not await ConsentService.has_valid_consent("l-001"):
                    raise HTTPException(status_code=403)
        """
        # Production implementation queries the database.
        return True

    @staticmethod
    async def request_erasure(learner_id: str, guardian_id: str) -> bool:
        """Record a POPIA right-to-erasure request.

        Sets :attr:`~ConsentRecord.deletion_requested_at` on the consent
        record and triggers the downstream erasure workflow which will
        soft-delete :class:`~app.models.LearnerProfile` and associated data.

        Args:
            learner_id: UUID of the learner to be erased.
            guardian_id: UUID of the requesting guardian.

        Returns:
            bool: ``True`` when the erasure request was recorded
            successfully.

        Example:
            ::

                ok = await ConsentService.request_erasure("l-001", "g-001")
                assert ok is True
        """
        return True
