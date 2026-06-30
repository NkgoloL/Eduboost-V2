from __future__ import annotations

from typing import Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.learner_repository import LearnerRepository
from app.repositories.knowledge_gap_repository import KnowledgeGapRepository
from app.services.consent import ConsentService
from app.services.audit_service import AuditService

class LearnerService:
    def __init__(self, db: AsyncSession, repository: Any | None = None) -> None:
        self.db = db
        # Backward compatibility for tests that pass repository directly
        self.repository = repository if repository else LearnerRepository(db)

    async def get_learner_summary(self, learner_id: str):
        return await self.repository.get_by_id(learner_id)

    async def create_learner(self, guardian_id: str, display_name: str, grade: int, language: str) -> Any:
        return await self.repository.create(
            guardian_id=guardian_id,
            display_name=display_name,
            grade=grade,
            language=language,
        )

    async def get_mastery(self, learner_id: str, actor_id: str | None = None) -> dict:
        consent = ConsentService(self.db)
        await consent.require_active_consent(learner_id, actor_id=actor_id)

        learner = await self.repository.get_by_id(learner_id)
        if not learner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

        active_gaps = await KnowledgeGapRepository(self.db).get_active_gaps(learner_id)
        default_subjects = {"MATH": 0.72, "ENG": 0.7, "LIFE": 0.78, "NS": 0.68, "SS": 0.69}
        mastery_map = default_subjects.copy()
        
        for gap in active_gaps:
            key = gap.subject.upper()
            baseline = mastery_map.get(key, 0.7)
            mastery_map[key] = max(0.15, min(0.98, baseline - (gap.severity * 0.18)))

        return {
            "learner_id": learner_id,
            "mastery": [
                {"subject_code": subject_code, "mastery_score": round(score, 3)}
                for subject_code, score in mastery_map.items()
            ],
        }

    async def request_erasure(self, learner_id: str, current_user: dict) -> tuple[str, str]:
        """
        Processes erasure request and returns (learner_id, learner_pseudonym) for background purging.
        """
        learner = await self.repository.get_by_id(learner_id)
        if not learner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

        role = str(current_user.get("role", "")).lower()
        if learner.guardian_id != current_user["sub"] and role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to erase this learner")

        learner_pseudonym = learner.pseudonym_id

        consent_svc = ConsentService(self.db)
        await consent_svc.execute_erasure(current_user["sub"], learner_id)

        # Soft-delete immediately
        await self.repository.soft_delete(learner_id)

        # Audit
        audit = AuditService(self.db)
        await audit.record(
            "learner.erased",
            actor_id=current_user["sub"],
            learner_pseudonym=learner_pseudonym,
            resource_id=learner_id,
            payload={"learner_id": learner_id},
            constitutional_outcome="APPROVED",
        )

        return learner_id, learner_pseudonym

    async def process_onboarding(self, learner_id: str, answers: list[dict]) -> dict:
        from app.services.archetype_service import ArchetypeService
        
        learner = await self.repository.get_by_id(learner_id)
        if not learner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

        archetype_service = ArchetypeService()
        archetype, description, probabilities = archetype_service.classify_archetype(answers)

        await self.repository.update_archetype(learner_id, archetype.value)

        return {
            "learner_id": learner_id,
            "archetype": archetype.value,
            "description": description,
            "probabilities": probabilities,
        }
