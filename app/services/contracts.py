"""
EduBoost SA — Service Contracts (Protocols)
===========================================
Defines the interfaces for all core services to enable decoupled 
service-to-service communication and easier testing/mocking.
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


@runtime_checkable
class IAuthService(Protocol):
    async def authenticate(self, email: str, password: str, db: AsyncSession) -> dict[str, Any]: ...
    async def refresh_token(self, refresh_token: str, db: AsyncSession) -> dict[str, Any]: ...
    async def logout(self, jti: str, db: AsyncSession) -> None: ...


@runtime_checkable
class ILearnerService(Protocol):
    async def create_learner(self, guardian_id: UUID, data: dict[str, Any], db: AsyncSession) -> dict[str, Any]: ...
    async def get_learner(self, learner_id: UUID, db: AsyncSession) -> dict[str, Any] | None: ...
    async def update_xp(self, learner_id: UUID, xp_delta: int, db: AsyncSession) -> None: ...


@runtime_checkable
class IConsentService(Protocol):
    async def grant_consent(self, guardian_id: UUID, learner_id: UUID, db: AsyncSession) -> None: ...
    async def revoke_consent(self, guardian_id: UUID, learner_id: UUID, db: AsyncSession) -> None: ...
    async def has_active_consent(self, learner_id: UUID, db: AsyncSession) -> bool: ...


@runtime_checkable
class IDiagnosticService(Protocol):
    async def start_session(self, learner_id: UUID, subject: str, db: AsyncSession) -> dict[str, Any]: ...
    async def submit_response(self, session_id: UUID, item_id: str, is_correct: bool, db: AsyncSession) -> dict[str, Any]: ...


@runtime_checkable
class ILessonService(Protocol):
    async def generate_lesson(self, learner_id: UUID, subject: str, topic: str, db: AsyncSession) -> dict[str, Any]: ...
    async def mark_lesson_completed(self, lesson_id: UUID, db: AsyncSession) -> None: ...
