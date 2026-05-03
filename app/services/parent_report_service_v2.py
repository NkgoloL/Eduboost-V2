from __future__ import annotations

from typing import Any

from app.services.audit_service import AuditService


class ParentReportServiceV2:
    def __init__(self, learner_repository: Any, parent_report_repository: Any) -> None:
        self.learner_repository = learner_repository
        self.parent_report_repository = parent_report_repository

    async def build_report(self, learner_id: str, guardian_id: str) -> dict:
        learner = await self.learner_repository.get_by_id(learner_id)
        if learner is None:
            raise ValueError("Learner not found")
        if not await self.parent_report_repository.verify_guardian_link(learner_id, guardian_id):
            raise PermissionError("Guardian is not linked to learner")
        subjects = await self.parent_report_repository.get_subject_mastery(learner_id)
        weak = [s for s in subjects if s.get("mastery_score", 1.0) < 0.5]
        summary = "Learner is progressing steadily."
        if weak:
            summary = "Priority support needed in " + ", ".join(s.get("subject_code", "subject") for s in weak) + "."
        report_id = await self.parent_report_repository.persist_report(
            learner_id=learner_id,
            guardian_id=guardian_id,
            summary=summary,
            subjects=subjects,
        )
        await AuditService().log_event("PARENT_REPORT_CREATED", {"report_id": report_id}, learner_id)
        return {"report_id": report_id, "summary": summary, "subjects": subjects}

    async def list_reports(self, learner_id: str, guardian_id: str) -> list[dict]:
        if not await self.parent_report_repository.verify_guardian_link(learner_id, guardian_id):
            raise PermissionError("Guardian is not linked to learner")
        return await self.parent_report_repository.get_reports_for_learner(learner_id)
