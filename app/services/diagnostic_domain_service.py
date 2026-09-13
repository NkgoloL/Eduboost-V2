"""EduBoost V2 — Diagnostic Domain Service.

Provides a typed domain service boundary between API routers and persistence repositories,
ensuring routers never import or reflectively instantiate repositories directly.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.repositories import (
    LearnerRepository,
    GuardianRepository,
    IRTRepository,
    DiagnosticRepository,
    KnowledgeGapRepository,
)
from app.repositories.item_bank_repository import ItemBankRepository
from app.repositories.diagnostic_session_repository import DiagnosticSessionRepository
from app.repositories.mastery_repository import MasteryRepository
from app.modules.diagnostics.diagnostic_session_service import DiagnosticSessionService
from app.modules.diagnostics.session_recovery_service import SessionRecoveryService
from app.modules.diagnostics.item_bank_service import ItemBankService


class DiagnosticDomainService:
    """Typed domain service managing diagnostic persistence and orchestration."""

    def __init__(
        self,
        db: AsyncSession,
        learner_repo: Any = None,
        guardian_repo: Any = None,
        item_bank_repo: Any = None,
        irt_repo: Any = None,
        diagnostic_repo: Any = None,
        knowledge_gap_repo: Any = None,
        session_repo: Any = None,
        mastery_repo: Any = None,
    ) -> None:
        self.db = db
        # Check router-level compatibility layer if tests patched diagnostic_repositories
        compat_repos = None
        try:
            from app.api_v2_routers import diagnostics as diag_module
            compat_repos = getattr(diag_module, "diagnostic_repositories", None)
        except Exception:
            pass

        if compat_repos is not None:
            self.learner_repo = learner_repo or compat_repos.learner(db)
            self.guardian_repo = guardian_repo or compat_repos.guardian(db)
            self.item_bank_repo = item_bank_repo or compat_repos.item_bank(db)
            self.irt_repo = irt_repo or compat_repos.irt(db)
            self.diagnostic_repo = diagnostic_repo or compat_repos.diagnostic(db)
            self.knowledge_gap_repo = knowledge_gap_repo or compat_repos.knowledge_gap(db)
            self.session_repo = session_repo or compat_repos.diagnostic_session(db)
            self.mastery_repo = mastery_repo or compat_repos.mastery(db)
        else:
            self.learner_repo = learner_repo or LearnerRepository(db)
            self.guardian_repo = guardian_repo or GuardianRepository(db)
            self.item_bank_repo = item_bank_repo or ItemBankRepository(db)
            self.irt_repo = irt_repo or IRTRepository(db)
            self.diagnostic_repo = diagnostic_repo or DiagnosticRepository(db)
            self.knowledge_gap_repo = knowledge_gap_repo or KnowledgeGapRepository(db)
            self.session_repo = session_repo or DiagnosticSessionRepository(db)
            self.mastery_repo = mastery_repo or MasteryRepository(db)

    async def get_learner(self, learner_id: str | UUID) -> Any:
        return await self.learner_repo.get_by_id(str(learner_id))

    async def update_learner_theta(self, learner_id: str | UUID, theta: float) -> None:
        await self.learner_repo.update_theta(str(learner_id), theta)

    async def get_guardian(self, guardian_id: str | UUID) -> Any:
        return await self.guardian_repo.get_by_id(str(guardian_id))

    async def list_approved_items_for_grade(self, grade: int, limit: int = 20) -> list[Any]:
        return await self.item_bank_repo.list_approved_for_grade(grade, limit=limit)

    async def get_irt_items_for_grade(self, grade: int, limit: int = 20) -> list[Any]:
        return await self.irt_repo.get_items_for_grade(grade, limit=limit)

    async def get_item_bank_item(self, item_id: str | UUID) -> Any:
        return await self.item_bank_repo.get_item(item_id)

    async def list_items_by_caps_ref(self, caps_ref: str, limit: int = 200) -> list[Any]:
        return list(await self.item_bank_repo.list_by_caps_ref(caps_ref, limit=limit))

    async def create_diagnostic_session(self, learner_id: str | UUID, theta_start: float) -> Any:
        return await self.diagnostic_repo.create_session(str(learner_id), theta_start)

    async def complete_diagnostic_session(
        self, session_id: str | UUID, responses: dict[str, str], theta_after: float
    ) -> Any:
        return await self.diagnostic_repo.complete_session(session_id, responses, theta_after)

    async def upsert_knowledge_gap(
        self, learner_id: str | UUID, grade: int, subject: str, topic: str, severity: float
    ) -> Any:
        return await self.knowledge_gap_repo.upsert(str(learner_id), grade, subject, topic, severity)

    async def upsert_knowledge_gaps(
        self, learner_id: str | UUID, gaps: list[dict[str, Any]]
    ) -> None:
        for g in gaps:
            await self.knowledge_gap_repo.upsert(
                str(learner_id), g["grade"], g["subject"], g["topic"], g["severity"]
            )

    def get_item_bank_service(self) -> ItemBankService:
        return ItemBankService(self.item_bank_repo)

    def get_session_service(self) -> DiagnosticSessionService:
        return DiagnosticSessionService(
            session_repository=self.session_repo,
            mastery_repository=self.mastery_repo,
            recovery_service=SessionRecoveryService(),
        )


def get_diagnostic_domain_service(
    db: AsyncSession = Depends(get_db),
) -> DiagnosticDomainService:
    """FastAPI dependency provider for DiagnosticDomainService."""
    return DiagnosticDomainService(db)

