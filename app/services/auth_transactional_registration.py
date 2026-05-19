from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class AuthRegistrationInput:
    email: str
    name: str
    password_hash: str
    learner_name: str
    fail_after_user: bool = False
    fail_after_guardian: bool = False
    fail_after_learner: bool = False


@dataclass(frozen=True)
class AuthRegistrationResult:
    user_id: str
    guardian_id: str
    learner_id: str
    email: str


class AuthRegistrationTransactionError(RuntimeError):
    """Raised by proof fixtures to simulate multi-write failure."""


class TransactionalAuthRegistrationService:
    """Small transaction-bound registration proof service.

    This service is intentionally narrow. It proves that high-risk auth
    registration style multi-write flows can share one transaction boundary and
    fail atomically.
    """

    def __init__(
        self,
        session: Any,
        *,
        users_table: Any,
        guardians_table: Any,
        learners_table: Any,
        clock: Any | None = None,
    ) -> None:
        self.session = session
        self.users_table = users_table
        self.guardians_table = guardians_table
        self.learners_table = learners_table
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    async def register(self, data: AuthRegistrationInput) -> AuthRegistrationResult:
        user_id = str(uuid4())
        guardian_id = str(uuid4())
        learner_id = str(uuid4())
        now = self.clock()

        try:
            async with self.session.begin():
                await self.session.execute(
                    self.users_table.insert().values(
                        id=user_id,
                        email=data.email,
                        password_hash=data.password_hash,
                        created_at=now,
                    )
                )
                if data.fail_after_user:
                    raise AuthRegistrationTransactionError("simulated failure after user insert")

                await self.session.execute(
                    self.guardians_table.insert().values(
                        id=guardian_id,
                        user_id=user_id,
                        name=data.name,
                        created_at=now,
                    )
                )
                if data.fail_after_guardian:
                    raise AuthRegistrationTransactionError("simulated failure after guardian insert")

                await self.session.execute(
                    self.learners_table.insert().values(
                        id=learner_id,
                        guardian_id=guardian_id,
                        name=data.learner_name,
                        created_at=now,
                    )
                )
                if data.fail_after_learner:
                    raise AuthRegistrationTransactionError("simulated failure after learner insert")
        except Exception:
            # The async session transaction context rolls back automatically.
            raise

        return AuthRegistrationResult(
            user_id=user_id,
            guardian_id=guardian_id,
            learner_id=learner_id,
            email=data.email,
        )


__all__ = [
    "AuthRegistrationInput",
    "AuthRegistrationResult",
    "AuthRegistrationTransactionError",
    "TransactionalAuthRegistrationService",
]
