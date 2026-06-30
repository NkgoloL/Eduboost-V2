from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DiagnosticSession


class DiagnosticSessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_session(self, learner_id: str | UUID, *, theta: float = 0.0, se: float = 1.0, caps_ref: str | None = None) -> DiagnosticSession:
        session = DiagnosticSession(
            learner_id=str(learner_id),
            theta_before=theta,
            theta_after=theta,
            session_state="initialising",
            se_estimate=se,
            items_served=0,
            gap_topics=[],
            misconception_tags=[],
            theta_history=[{"theta": theta, "se": se, "at": datetime.now(timezone.utc).isoformat()}],
            responses={"caps_ref": caps_ref} if caps_ref else {},
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_session(self, session_id: str | UUID) -> DiagnosticSession | None:
        result = await self.db.execute(select(DiagnosticSession).where(DiagnosticSession.id == str(session_id)))
        return result.scalar_one_or_none()

    async def update_session_state(self, session_id: str | UUID, state: str, **values) -> DiagnosticSession | None:
        session = await self.get_session(session_id)
        if session is None:
            return None
        session.session_state = state
        for key, value in values.items():
            setattr(session, key, value)
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def append_response(self, session_id: str | UUID, response: dict) -> DiagnosticSession | None:
        session = await self.get_session(session_id)
        if session is None:
            return None
        responses = dict(session.responses or {})
        items = list(responses.get("items", []))
        items.append(response)
        responses["items"] = items
        session.responses = responses
        session.items_served = len(items)
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def list_incomplete_sessions(self, learner_id: str | UUID) -> list[DiagnosticSession]:
        result = await self.db.execute(
            select(DiagnosticSession).where(
                DiagnosticSession.learner_id == str(learner_id),
                DiagnosticSession.completed_at.is_(None),
                DiagnosticSession.session_state.not_in(["completed", "abandoned"]),
            )
        )
        return list(result.scalars().all())
