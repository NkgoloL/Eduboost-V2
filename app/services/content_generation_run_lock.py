"""Run lock for full generation to prevent concurrent execution."""
from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import ContentGenerationRun


DEFAULT_LOCK_TTL_MINUTES = 180


@dataclass(frozen=True)
class LockAcquisitionResult:
    """Result of lock acquisition attempt."""
    acquired: bool
    lock_holder: str | None = None
    lock_acquired_at: str | None = None
    lock_expires_at: str | None = None
    error: str | None = None


class ContentGenerationRunLock:
    """Lock manager for full generation runs."""

    def __init__(self, ttl_minutes: int | None = None) -> None:
        self.ttl_minutes = ttl_minutes or int(os.environ.get("CONTENT_FACTORY_FULL_RUN_LOCK_TTL_MINUTES", DEFAULT_LOCK_TTL_MINUTES))
        self.ttl_seconds = self.ttl_minutes * 60

    async def acquire(
        self,
        session: AsyncSession,
        *,
        holder: str,
    ) -> LockAcquisitionResult:
        """Acquire the full generation run lock.

        Args:
            session: Database session
            holder: Identifier for the lock holder (e.g., hostname, process ID)

        Returns:
            LockAcquisitionResult indicating success or failure
        """
        now = time.time()
        expires_at = now + self.ttl_seconds

        # Check for existing active lock
        existing_lock = await self._get_active_lock(session)
        if existing_lock:
            # Check if lock is stale
            lock_acquired_at = existing_lock.get("lock_acquired_at", 0)
            if lock_acquired_at and now < lock_acquired_at + self.ttl_seconds:
                return LockAcquisitionResult(
                    acquired=False,
                    lock_holder=existing_lock.get("lock_holder"),
                    lock_acquired_at=existing_lock.get("lock_acquired_at"),
                    lock_expires_at=existing_lock.get("lock_expires_at"),
                    error="Lock already held",
                )
            # Lock is stale, will be released below

        # Release any stale locks
        await self._release_stale_locks(session)

        # Acquire new lock by updating the most recent run
        result = await session.execute(
            select(ContentGenerationRun)
            .where(ContentGenerationRun.scope_id == "all_scopes")
            .order_by(ContentGenerationRun.created_at.desc())
            .limit(1)
        )
        latest_run = result.scalar_one_or_none()

        if latest_run:
            metadata = dict(latest_run.run_metadata or {})
            metadata["full_generation_lock"] = {
                "holder": holder,
                "lock_acquired_at": now,
                "lock_expires_at": expires_at,
            }
            latest_run.run_metadata = metadata
            await session.flush()

            return LockAcquisitionResult(
                acquired=True,
                lock_holder=holder,
                lock_acquired_at=now,
                lock_expires_at=expires_at,
            )

        # No run exists, create a placeholder run for the lock
        placeholder_run = ContentGenerationRun(
            run_id=uuid.uuid4(),
            scope_id="all_scopes",
            status="queued",
            requested_by=holder,
            run_metadata={
                "full_generation_lock": {
                    "holder": holder,
                    "lock_acquired_at": now,
                    "lock_expires_at": expires_at,
                },
            },
        )
        session.add(placeholder_run)
        await session.flush()

        return LockAcquisitionResult(
            acquired=True,
            lock_holder=holder,
            lock_acquired_at=now,
            lock_expires_at=expires_at,
        )

    async def release(
        self,
        session: AsyncSession,
        *,
        holder: str,
    ) -> bool:
        """Release the full generation run lock.

        Args:
            session: Database session
            holder: Identifier for the lock holder

        Returns:
            True if lock was released, False otherwise
        """
        now = time.time()

        result = await session.execute(
            select(ContentGenerationRun)
            .where(ContentGenerationRun.scope_id == "all_scopes")
            .order_by(ContentGenerationRun.created_at.desc())
            .limit(1)
        )
        latest_run = result.scalar_one_or_none()

        if latest_run:
            metadata = dict(latest_run.run_metadata or {})
            lock_info = metadata.get("full_generation_lock", {})

            if lock_info.get("holder") == holder:
                metadata["full_generation_lock"] = {
                    "holder": None,
                    "lock_acquired_at": None,
                    "lock_expires_at": None,
                    "lock_released_at": now,
                }
                latest_run.run_metadata = metadata
                await session.flush()
                return True

        return False

    async def _get_active_lock(self, session: AsyncSession) -> dict[str, Any] | None:
        """Get the current active lock if any."""
        now = time.time()

        result = await session.execute(
            select(ContentGenerationRun)
            .where(ContentGenerationRun.scope_id == "all_scopes")
            .order_by(ContentGenerationRun.created_at.desc())
            .limit(1)
        )
        latest_run = result.scalar_one_or_none()

        if latest_run:
            metadata = dict(latest_run.run_metadata or {})
            lock_info = metadata.get("full_generation_lock", {})
            lock_acquired_at = lock_info.get("lock_acquired_at", 0)

            if lock_acquired_at and now < lock_acquired_at + self.ttl_seconds:
                return lock_info

        return None

    async def _release_stale_locks(self, session: AsyncSession) -> None:
        """Release any stale locks."""
        now = time.time()

        result = await session.execute(
            select(ContentGenerationRun)
            .where(ContentGenerationRun.scope_id == "all_scopes")
            .order_by(ContentGenerationRun.created_at.desc())
            .limit(1)
        )
        latest_run = result.scalar_one_or_none()

        if latest_run:
            metadata = dict(latest_run.run_metadata or {})
            lock_info = metadata.get("full_generation_lock", {})
            lock_acquired_at = lock_info.get("lock_acquired_at", 0)

            if lock_acquired_at and now >= lock_acquired_at + self.ttl_seconds:
                metadata["full_generation_lock"] = {
                    "holder": None,
                    "lock_acquired_at": None,
                    "lock_expires_at": None,
                    "lock_released_at": now,
                    "reason": "stale",
                }
                latest_run.run_metadata = metadata
                await session.flush()
