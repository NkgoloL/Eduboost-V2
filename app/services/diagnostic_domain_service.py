"""Diagnostic domain service for EduBoost V2.

Encapsulates all database persistence and domain orchestration for diagnostics,
ensuring FastAPI v2 routers remain decoupled from repositories and ORM models.
"""
from __future__ import annotations

import sys
from typing import Any, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.diagnostics.diagnostic_session_service import (
    DiagnosticResponseResult,
    DiagnosticSessionService,
)
from app.modules.diagnostics.item_bank_service import ItemBankService
from app.modules.diagnostics.session_recovery_service import (
    DiagnosticSessionSnapshot,
    SessionRecoveryService,
)
from app.repositories.diagnostic_session_repository import DiagnosticSessionRepository
from app.repositories.item_bank_repository import ItemBankRepository
from app.repositories.mastery_repository import MasteryRepository
from app.repositories.repositories import (
    DiagnosticRepository,
    GuardianRepository,
    IRTRepository,
    KnowledgeGapRepository,
    LearnerRepository,
)


def _resolve_session_service_factory(**kwargs: Any) -> Any:
    diag_mod = sys.modules.get("app.api_v2_routers.diagnostics")
    cls = getattr(diag_mod, "DiagnosticSessionService", DiagnosticSessionService)
    return cls(**kwargs)


def _resolve_item_bank_service_factory(repo: Any) -> Any:
    diag_mod = sys.modules.get("app.api_v2_routers.diagnostics")
    cls = getattr(diag_mod, "ItemBankService", ItemBankService)
    return cls(repo)


class DiagnosticDomainService:
    """Domain service orchestrating all diagnostic repository access and domain operations."""

    def __init__(
        self,
        db: AsyncSession,
        *,
        learner_repo: LearnerRepository | Any | None = None,
        guardian_repo: GuardianRepository | Any | None = None,
        irt_repo: IRTRepository | Any | None = None,
        diagnostic_repo: DiagnosticRepository | Any | None = None,
        knowledge_gap_repo: KnowledgeGapRepository | Any | None = None,
        item_bank_repo: ItemBankRepository | Any | None = None,
        session_repo: DiagnosticSessionRepository | Any | None = None,
        mastery_repo: MasteryRepository | Any | None = None,
        recovery_service: SessionRecoveryService | None = None,
        session_service_factory: Any | None = None,
        item_bank_service_factory: Any | None = None,
    ) -> None:
        self.db = db
        self.learner_repo = learner_repo if learner_repo is not None else LearnerRepository(db)
        self.guardian_repo = guardian_repo if guardian_repo is not None else GuardianRepository(db)
        self.irt_repo = irt_repo if irt_repo is not None else IRTRepository(db)
        self.diagnostic_repo = diagnostic_repo if diagnostic_repo is not None else DiagnosticRepository(db)
        self.knowledge_gap_repo = knowledge_gap_repo if knowledge_gap_repo is not None else KnowledgeGapRepository(db)
        self.item_bank_repo = item_bank_repo if item_bank_repo is not None else ItemBankRepository(db)
        self.session_repo = session_repo if session_repo is not None else DiagnosticSessionRepository(db)
        self.mastery_repo = mastery_repo if mastery_repo is not None else MasteryRepository(db)
        self.recovery_service = recovery_service or SessionRecoveryService()
        self.session_service_factory = session_service_factory or _resolve_session_service_factory
        self.item_bank_service_factory = item_bank_service_factory or _resolve_item_bank_service_factory

    # --- Learner & Guardian Operations ---

    async def get_learner(self, learner_id: str | UUID) -> Any:
        return await self.learner_repo.get_by_id(str(learner_id))

    async def get_guardian(self, guardian_id: str | UUID) -> Any:
        return await self.guardian_repo.get_by_id(str(guardian_id))

    async def update_learner_theta(self, learner_id: str | UUID, theta: float) -> None:
        await self.learner_repo.update_theta(str(learner_id), theta)

    # --- Item & Item Bank Operations ---

    async def list_approved_items_for_grade(
        self, grade: int, limit: int = 20
    ) -> Sequence[Any]:
        return await self.item_bank_repo.list_approved_for_grade(grade, limit=limit)

    async def get_irt_items_for_grade(
        self, grade: int, limit: int | None = None
    ) -> list[Any]:
        if limit is not None:
            return await self.irt_repo.get_items_for_grade(grade, limit=limit)
        return await self.irt_repo.get_items_for_grade(grade)

    async def get_item_bank_item(self, item_id: UUID | str) -> Any:
        return await self.item_bank_repo.get_item(UUID(str(item_id)))

    async def list_items_by_caps_ref(
        self, caps_ref: str, limit: int = 200
    ) -> Sequence[Any]:
        return await self.item_bank_repo.list_by_caps_ref(caps_ref, limit=limit)

    def get_item_bank_service(self) -> Any:
        return self.item_bank_service_factory(self.item_bank_repo)

    async def get_item_bank_coverage_summary(self) -> dict[str, dict[str, Any]]:
        service = self.get_item_bank_service()
        return await service.get_coverage_summary()

    async def mark_item_reviewed(
        self,
        *,
        item_id: UUID | str,
        new_status: str,
        reviewer_id: UUID | str,
        quality_score: float | None = None,
    ) -> Any:
        service = self.get_item_bank_service()
        return await service.mark_item_reviewed(
            item_id=UUID(str(item_id)),
            new_status=new_status,
            reviewer_id=UUID(str(reviewer_id)),
            quality_score=quality_score,
        )

    # --- Diagnostic Sessions & Knowledge Gaps ---

    async def create_session(
        self, learner_id: str | UUID, theta_start: float = 0.0
    ) -> Any:
        return await self.diagnostic_repo.create_session(str(learner_id), theta_start)

    async def complete_session(
        self,
        session_id: str | UUID,
        responses: dict[str, str],
        theta_final: float,
    ) -> None:
        await self.diagnostic_repo.complete_session(str(session_id), responses, theta_final)

    async def upsert_knowledge_gap(
        self,
        learner_id: str | UUID,
        grade: int,
        subject: str,
        topic: str,
        severity: float,
    ) -> Any:
        return await self.knowledge_gap_repo.upsert(str(learner_id), grade, subject, topic, severity)

    # --- Adaptive Diagnostic Session Service ---

    def get_session_service(self, *, recovery_only: bool = False) -> Any:
        if recovery_only:
            return self.session_service_factory(recovery_service=self.recovery_service)
        return self.session_service_factory(
            session_repository=self.session_repo,
            mastery_repository=self.mastery_repo,
            recovery_service=self.recovery_service,
        )

    async def start_session(
        self, learner_id: str | UUID, caps_ref: str, *, theta: float = 0.0
    ) -> DiagnosticSessionSnapshot:
        service = self.get_session_service()
        return await service.start_session(learner_id, caps_ref, theta=theta)

    async def recover_session(
        self, session_id: str | UUID
    ) -> DiagnosticSessionSnapshot | None:
        service = self.get_session_service(recovery_only=True)
        return await service.recover_session(session_id)

    async def get_next_session_item(
        self, session_id: str | UUID, items: list[object] | None = None
    ) -> Any | None:
        service = self.get_session_service(recovery_only=True)
        return await service.get_next_item(session_id, items)

    async def submit_session_response(
        self,
        session_id: str | UUID,
        item: object,
        *,
        correct: bool,
        response: str | None = None,
    ) -> DiagnosticResponseResult:
        service = self.get_session_service()
        return await service.submit_response(session_id, item, correct=correct, response=response)


def get_diagnostic_domain_service(
    db: AsyncSession = Depends(get_db),
) -> DiagnosticDomainService:
    """FastAPI dependency providing DiagnosticDomainService."""
    from app.api_v2_deps import diagnostic_repositories

    return DiagnosticDomainService(
        db,
        learner_repo=diagnostic_repositories.learner(db),
        guardian_repo=diagnostic_repositories.guardian(db),
        irt_repo=diagnostic_repositories.irt(db),
        diagnostic_repo=diagnostic_repositories.diagnostic(db),
        knowledge_gap_repo=diagnostic_repositories.knowledge_gap(db),
        item_bank_repo=diagnostic_repositories.item_bank(db),
        session_repo=diagnostic_repositories.diagnostic_session(db),
        mastery_repo=diagnostic_repositories.mastery(db),
    )


__all__ = [
    "DiagnosticDomainService",
    "get_diagnostic_domain_service",
]

