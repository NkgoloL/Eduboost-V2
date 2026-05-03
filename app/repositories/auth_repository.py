"""Guardian persistence repository for EduBoost V2."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import Guardian


class GuardianRepository(BaseRepository[Guardian]):
    """Repository for guardian accounts and token lifecycle operations."""

    model = Guardian

    async def get_by_email_hash(self, email_hash: str, db: AsyncSession) -> Guardian | None:
        result = await db.execute(select(Guardian).where(Guardian.email_hash == email_hash))
        return result.scalar_one_or_none()

    async def get_by_verification_token(self, token: str, db: AsyncSession) -> Guardian | None:
        result = await db.execute(select(Guardian).where(Guardian.verification_token == token))
        return result.scalar_one_or_none()

    async def get_guardian_by_id(self, guardian_id: str, db: AsyncSession) -> Guardian | None:
        return await self.get(UUID(guardian_id), db)

    async def revoke_jti(self, jti: str, expires_at: datetime, db: AsyncSession) -> None:
        """Mark a JWT JTI as revoked so it can't be reused."""
        await db.execute(
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

    async def is_jti_revoked(self, jti: str, db: AsyncSession) -> bool:
        """Return True if the given JTI has been revoked."""
        result = await db.execute(
            text("SELECT 1 FROM revoked_tokens WHERE jti = :jti"), {"jti": jti}
        )
        return result.first() is not None


AuthRepository = GuardianRepository
