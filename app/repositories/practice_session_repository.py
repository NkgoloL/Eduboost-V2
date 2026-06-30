"""Practice session persistence repository for EduBoost V2.

Owns all DB reads and writes for practice sessions,
replacing the process-local `_SESSIONS` dict.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PracticeSession


class PracticeSessionRepository:
    """Repository for durable practice session storage.
    
    Provides CRUD operations and lifecycle management for practice sessions,
    ensuring durability across process restarts and multi-worker consistency.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        learner_id: str,
        owner_subject: str,
        items: list[str],
        gap_topics: list[str] | None = None,
        theta: float = 0.0,
        session_ttl_hours: int = 24,
    ) -> PracticeSession:
        """Create a new practice session.
        
        Args:
            learner_id: Learner participating in practice
            owner_subject: User ID/subject who owns this session
            items: List of item IDs (UUIDs as strings) in sequence
            gap_topics: Optional list of CAPS references for gap remediation
            theta: Initial IRT ability estimate (default: 0.0)
            session_ttl_hours: Time-to-live in hours (default: 24 for auto-expiry)
            
        Returns:
            Created PracticeSession model instance
        """
        now = datetime.now(timezone.utc)
        session = PracticeSession(
            id=str(uuid4()),
            learner_id=learner_id,
            owner_subject=owner_subject,
            items=items,
            gap_topics=gap_topics or [],
            theta=theta,
            cursor=0,
            responses=[],
            created_at=now,
            expires_at=now + timedelta(hours=session_ttl_hours),
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_by_id(self, session_id: str) -> PracticeSession | None:
        """Fetch a practice session by ID.
        
        Returns None if not found or if expired.
        
        Args:
            session_id: The session ID
            
        Returns:
            PracticeSession if found and not expired, else None
        """
        result = await self.db.execute(
            select(PracticeSession).where(
                PracticeSession.id == session_id,
                PracticeSession.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalar_one_or_none()

    async def update_cursor_and_responses(
        self,
        session_id: str,
        new_cursor: int,
        new_responses: list,
    ) -> bool:
        """Update session cursor position and responses atomically.
        
        Args:
            session_id: The session ID
            new_cursor: New cursor position
            new_responses: Updated responses list
            
        Returns:
            True if updated, False if session not found or expired
        """
        stmt = (
            update(PracticeSession)
            .where(
                PracticeSession.id == session_id,
                PracticeSession.expires_at > datetime.now(timezone.utc),
            )
            .values(cursor=new_cursor, responses=new_responses)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount > 0

    async def mark_completed(self, session_id: str) -> bool:
        """Mark a session as completed.
        
        Args:
            session_id: The session ID
            
        Returns:
            True if marked, False if session not found or already expired
        """
        stmt = (
            update(PracticeSession)
            .where(
                PracticeSession.id == session_id,
                PracticeSession.expires_at > datetime.now(timezone.utc),
            )
            .values(completed_at=datetime.now(timezone.utc))
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount > 0

    async def delete_expired(self) -> int:
        """Delete all expired practice sessions.
        
        Useful as a periodic cleanup task (e.g., via background job).
        
        Returns:
            Number of sessions deleted
        """
        stmt = delete(PracticeSession).where(
            PracticeSession.expires_at <= datetime.now(timezone.utc)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def list_by_learner(self, learner_id: str) -> list[PracticeSession]:
        """List all active (non-expired) practice sessions for a learner.
        
        Args:
            learner_id: The learner ID
            
        Returns:
            List of active PracticeSession instances
        """
        result = await self.db.execute(
            select(PracticeSession).where(
                PracticeSession.learner_id == learner_id,
                PracticeSession.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalars().all()
