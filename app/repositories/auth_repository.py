"""Authentication / user persistence repository for EduBoost V2.

Owns all DB reads and writes for guardians (users), token revocation,
and refresh-token JTI tracking.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, text

from app.api.core.database import AsyncSessionFactory
from app.api.models.db_models import Guardian


class AuthRepository:
    """Repository for guardian (user) and token-lifecycle operations."""

    # ------------------------------------------------------------------ #
    # Guardian CRUD                                                         #
    # ------------------------------------------------------------------ #

    async def get_guardian_by_email_hash(self, email: str) -> dict | None:
        """Look up a guardian by their hashed email address."""
        email_hash = hashlib.sha256(email.strip().lower().encode()).hexdigest()
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(Guardian).where(Guardian.email_hash == email_hash)
            )
            guardian = result.scalar_one_or_none()
            if guardian is None:
                return None
        return self._guardian_to_dict(guardian)

    async def get_guardian_by_id(self, guardian_id: str) -> dict | None:
        """Return a guardian record by UUID."""
        async with AsyncSessionFactory() as session:
            guardian = await session.get(Guardian, uuid.UUID(guardian_id))
            if guardian is None:
                return None
        return self._guardian_to_dict(guardian)

    async def create_guardian(
        self,
        email: str,
        full_name: str,
        password_hash: str,
        phone_number: str | None = None,
    ) -> dict:
        """Create a new guardian record and return it."""
        email_hash = hashlib.sha256(email.strip().lower().encode()).hexdigest()
        guardian_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        async with AsyncSessionFactory() as session:
            guardian = Guardian(
                guardian_id=guardian_id,
                email_hash=email_hash,
                full_name_encrypted=full_name,  # encryption applied upstream
                password_hash=password_hash,
                phone_number=phone_number,
                created_at=now,
            )
            session.add(guardian)
            await session.commit()
            await session.refresh(guardian)
        return self._guardian_to_dict(guardian)

    # ------------------------------------------------------------------ #
    # Token revocation (JTI denylist via append-only audit table)          #
    # ------------------------------------------------------------------ #

    async def revoke_jti(self, jti: str, expires_at: datetime) -> None:
        """Mark a JWT JTI as revoked so it can't be reused."""
        async with AsyncSessionFactory() as session:
            await session.execute(
                text(
                    "INSERT INTO revoked_tokens (jti, revoked_at, expires_at) "
                    "VALUES (:jti, :revoked_at, :expires_at) "
                    "ON CONFLICT (jti) DO NOTHING"
                ),
                {
                    "jti": jti,
                    "revoked_at": datetime.now(timezone.utc),
                    "expires_at": expires_at,
                },
            )
            await session.commit()

    async def is_jti_revoked(self, jti: str) -> bool:
        """Return True if the given JTI has been revoked."""
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                text("SELECT 1 FROM revoked_tokens WHERE jti = :jti"), {"jti": jti}
            )
            return result.first() is not None

    # ------------------------------------------------------------------ #
    # Helpers                                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _guardian_to_dict(guardian: Guardian) -> dict[str, Any]:
        return {
            "guardian_id": str(guardian.guardian_id),
            "email_hash": guardian.email_hash,
            "full_name_encrypted": guardian.full_name_encrypted,
            "password_hash": guardian.password_hash,
            "phone_number": guardian.phone_number,
            "created_at": guardian.created_at.isoformat() if guardian.created_at else None,
        }
