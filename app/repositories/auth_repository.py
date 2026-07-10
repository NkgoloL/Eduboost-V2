"""Guardian persistence repository for EduBoost V2."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import Guardian


class GuardianRepository(BaseRepository[Guardian]):
    """Repository for guardian accounts and token lifecycle operations.

    The repository is intentionally usable in both canonical V2 styles:
    ``GuardianRepository().method(..., db)`` and the legacy/billing runtime
    style ``GuardianRepository(db).method(...)``.  This removes the release
    blocker where live billing code constructed the modern repository with a
    bound session but the modern class did not accept one.
    """

    model = Guardian

    def __init__(self, db: AsyncSession | None = None) -> None:
        self.db = db

    def _resolve_db(self, db: AsyncSession | None = None) -> AsyncSession:
        session = db or self.db
        if session is None:
            raise ValueError("GuardianRepository requires an AsyncSession")
        return session

    async def get_by_id(self, guardian_id: str, db: AsyncSession | None = None) -> Guardian | None:
        session = self._resolve_db(db)
        result = await session.execute(select(Guardian).where(Guardian.id == str(guardian_id)))
        return result.scalar_one_or_none()

    async def get_by_email_hash(self, email_hash: str, db: AsyncSession | None = None) -> Guardian | None:
        session = self._resolve_db(db)
        result = await session.execute(select(Guardian).where(Guardian.email_hash == email_hash))
        return result.scalar_one_or_none()

    async def get_by_verification_token(self, token: str, db: AsyncSession | None = None) -> Guardian | None:
        session = self._resolve_db(db)
        result = await session.execute(select(Guardian).where(Guardian.verification_token == token))
        return result.scalar_one_or_none()

    async def get_guardian_by_id(self, guardian_id: str, db: AsyncSession | None = None) -> Guardian | None:
        return await self.get_by_id(guardian_id, db)

    async def get_by_stripe_customer_id(self, stripe_customer_id: str, db: AsyncSession | None = None) -> Guardian | None:
        session = self._resolve_db(db)
        result = await session.execute(
            select(Guardian).where(Guardian.stripe_customer_id == stripe_customer_id)
        )
        return result.scalar_one_or_none()

    async def update_subscription(
        self,
        guardian_id: str,
        tier: str,
        stripe_sub_id: str | None = None,
        db: AsyncSession | None = None,
    ) -> None:
        session = self._resolve_db(db)
        await session.execute(
            update(Guardian)
            .where(Guardian.id == str(guardian_id))
            .values(
                subscription_tier=tier,
                stripe_subscription_id=stripe_sub_id,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await session.flush()

    async def revoke_jti(self, jti: str, expires_at: datetime, db: AsyncSession | None = None) -> None:
        """Mark a JWT JTI as revoked so it cannot be reused."""
        session = self._resolve_db(db)
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

    async def is_jti_revoked(self, jti: str, db: AsyncSession | None = None) -> bool:
        """Return True if the given JTI has been revoked."""
        session = self._resolve_db(db)
        result = await session.execute(
            text("SELECT 1 FROM revoked_tokens WHERE jti = :jti"), {"jti": jti}
        )
        return result.first() is not None


AuthRepository = GuardianRepository
