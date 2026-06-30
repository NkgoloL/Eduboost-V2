from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class DiagnosticTransactionInput:
    learner_id: str
    session_id: str
    item_id: str
    caps_ref: str
    is_correct: bool
    theta_delta: float = 0.0
    fail_after_response: bool = False
    fail_after_mastery: bool = False
    fail_after_audit: bool = False


@dataclass(frozen=True)
class DiagnosticTransactionResult:
    response_id: str
    mastery_id: str
    audit_event_id: str
    learner_id: str
    session_id: str
    item_id: str


class DiagnosticTransactionError(RuntimeError):
    """Raised by proof fixtures to simulate multi-write failure."""


class TransactionalDiagnosticResponseService:
    """Transaction-bound diagnostic response proof service.

    A diagnostic answer write is not safely complete unless the response row,
    mastery/progress update, and audit/event row are committed as one unit.
    This proof service intentionally models that multi-write boundary in a
    narrow, testable form.
    """

    def __init__(
        self,
        session: Any,
        *,
        responses_table: Any,
        mastery_table: Any,
        audit_events_table: Any,
        clock: Any | None = None,
    ) -> None:
        self.session = session
        self.responses_table = responses_table
        self.mastery_table = mastery_table
        self.audit_events_table = audit_events_table
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    async def submit_response(self, data: DiagnosticTransactionInput) -> DiagnosticTransactionResult:
        response_id = str(uuid4())
        mastery_id = str(uuid4())
        audit_event_id = str(uuid4())
        now = self.clock()

        try:
            async with self.session.begin():
                await self.session.execute(
                    self.responses_table.insert().values(
                        id=response_id,
                        learner_id=data.learner_id,
                        session_id=data.session_id,
                        item_id=data.item_id,
                        caps_ref=data.caps_ref,
                        is_correct=data.is_correct,
                        created_at=now,
                    )
                )
                if data.fail_after_response:
                    raise DiagnosticTransactionError("simulated failure after diagnostic response insert")

                await self.session.execute(
                    self.mastery_table.insert().values(
                        id=mastery_id,
                        learner_id=data.learner_id,
                        caps_ref=data.caps_ref,
                        theta_delta=data.theta_delta,
                        source_response_id=response_id,
                        updated_at=now,
                    )
                )
                if data.fail_after_mastery:
                    raise DiagnosticTransactionError("simulated failure after mastery update")

                await self.session.execute(
                    self.audit_events_table.insert().values(
                        id=audit_event_id,
                        learner_id=data.learner_id,
                        event_type="diagnostic.response_submitted",
                        source_response_id=response_id,
                        created_at=now,
                    )
                )
                if data.fail_after_audit:
                    raise DiagnosticTransactionError("simulated failure after diagnostic audit event insert")
        except Exception:
            # SQLAlchemy's transaction context rolls back automatically.
            raise

        return DiagnosticTransactionResult(
            response_id=response_id,
            mastery_id=mastery_id,
            audit_event_id=audit_event_id,
            learner_id=data.learner_id,
            session_id=data.session_id,
            item_id=data.item_id,
        )


__all__ = [
    "DiagnosticTransactionError",
    "DiagnosticTransactionInput",
    "DiagnosticTransactionResult",
    "TransactionalDiagnosticResponseService",
]
