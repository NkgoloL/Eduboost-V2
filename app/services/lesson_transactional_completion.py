from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class LessonCompletionInput:
    lesson_id: str
    learner_id: str
    xp_award: int
    audit_actor_id: str
    fail_after_lesson: bool = False
    fail_after_xp: bool = False
    fail_after_audit: bool = False


@dataclass(frozen=True)
class LessonCompletionResult:
    lesson_id: str
    learner_id: str
    xp_award: int
    audit_event_id: str


class LessonCompletionTransactionError(RuntimeError):
    """Raised by proof fixtures to simulate lesson completion failures."""


class LessonCompletionNotFoundError(RuntimeError):
    """Raised when the lesson/profile proof fixture is missing expected rows."""


class TransactionalLessonCompletionService:
    """Transaction-bound proof for lesson completion + XP + audit writes."""

    def __init__(
        self,
        session: Any,
        *,
        lessons_table: Any,
        profiles_table: Any,
        audit_events_table: Any,
        clock: Any | None = None,
    ) -> None:
        self.session = session
        self.lessons_table = lessons_table
        self.profiles_table = profiles_table
        self.audit_events_table = audit_events_table
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    async def complete_lesson(self, data: LessonCompletionInput) -> LessonCompletionResult:
        audit_event_id = str(uuid4())
        now = self.clock()

        try:
            async with self.session.begin():
                lesson_result = await self.session.execute(
                    self.lessons_table.update()
                    .where(self.lessons_table.c.id == data.lesson_id)
                    .where(self.lessons_table.c.learner_id == data.learner_id)
                    .values(completed=True, completed_at=now)
                )
                if lesson_result.rowcount != 1:
                    raise LessonCompletionNotFoundError("lesson not found for learner")
                if data.fail_after_lesson:
                    raise LessonCompletionTransactionError("simulated failure after lesson completion")

                profile_result = await self.session.execute(
                    self.profiles_table.update()
                    .where(self.profiles_table.c.learner_id == data.learner_id)
                    .values(xp=self.profiles_table.c.xp + data.xp_award, updated_at=now)
                )
                if profile_result.rowcount != 1:
                    raise LessonCompletionNotFoundError("gamification profile not found for learner")
                if data.fail_after_xp:
                    raise LessonCompletionTransactionError("simulated failure after XP update")

                await self.session.execute(
                    self.audit_events_table.insert().values(
                        id=audit_event_id,
                        event_type="lesson.completed",
                        actor_id=data.audit_actor_id,
                        learner_id=data.learner_id,
                        resource_id=data.lesson_id,
                        created_at=now,
                    )
                )
                if data.fail_after_audit:
                    raise LessonCompletionTransactionError("simulated failure after audit write")
        except Exception:
            # The async session transaction context rolls back automatically.
            raise

        return LessonCompletionResult(
            lesson_id=data.lesson_id,
            learner_id=data.learner_id,
            xp_award=data.xp_award,
            audit_event_id=audit_event_id,
        )


__all__ = [
    "LessonCompletionInput",
    "LessonCompletionNotFoundError",
    "LessonCompletionResult",
    "LessonCompletionTransactionError",
    "TransactionalLessonCompletionService",
]
