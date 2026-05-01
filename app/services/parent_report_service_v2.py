"""V2 parent reporting service — fully repository-driven.

Delegates all persistence to ParentReportRepository and LearnerRepository,
keeping this class focused purely on report construction logic.
"""

from __future__ import annotations

from app.repositories.learner_repository import LearnerRepository
from app.repositories.parent_report_repository import ParentReportRepository
from app.services.audit_service import AuditService


class ParentReportServiceV2:
    """Build and persist parent-facing learner progress reports."""

    def __init__(
        self,
        learner_repository: LearnerRepository | None = None,
        parent_report_repository: ParentReportRepository | None = None,
    ) -> None:
        self.learner_repository = learner_repository or LearnerRepository()
        self.parent_report_repository = parent_report_repository or ParentReportRepository()

    async def build_report(self, learner_id: str, guardian_id: str) -> dict:
        """Generate a parent progress report and persist it to the reports table."""
        learner = await self.learner_repository.get_by_id(learner_id)
        if learner is None:
            raise ValueError("Learner not found")

        # Enforce guardian–learner link
        is_linked = await self.parent_report_repository.verify_guardian_link(
            learner_id=learner_id, guardian_id=guardian_id
        )
        if not is_linked:
            raise PermissionError("Guardian is not linked to this learner")

        subjects = await self.parent_report_repository.get_subject_mastery(learner_id)

        # Derive narrative summary
        weak_subjects = [s for s in subjects if s["mastery_score"] < 0.5]
        strong_subjects = [s for s in subjects if s["mastery_score"] >= 0.75]
        summary_lines = [
            f"Grade {learner.grade} learner — overall mastery: {learner.overall_mastery:.0%}.",
        ]
        if weak_subjects:
            names = ", ".join(f"{s['subject_code']} (Grade {s['grade_level']})" for s in weak_subjects[:3])
            summary_lines.append(f"Areas needing attention: {names}.")
        if strong_subjects:
            names = ", ".join(s["subject_code"] for s in strong_subjects[:3])
            summary_lines.append(f"Performing well in: {names}.")
        summary = " ".join(summary_lines)

        report_id = await self.parent_report_repository.persist_report(
            learner_id=learner_id,
            guardian_id=guardian_id,
            overall_mastery=learner.overall_mastery,
            summary=summary,
            subjects=subjects,
        )

        await AuditService().log_event(
            event_type="PARENT_REPORT_GENERATED",
            learner_id=learner_id,
            payload={"report_id": report_id, "guardian_id": guardian_id},
        )

        return {
            "report_id": report_id,
            "learner_id": learner.learner_id,
            "grade": learner.grade,
            "overall_mastery": learner.overall_mastery,
            "summary": summary,
            "subjects": subjects,
        }

    async def list_reports(self, learner_id: str, guardian_id: str, limit: int = 10) -> list[dict]:
        """Return stored parent reports for a learner (most recent first)."""
        learner = await self.learner_repository.get_by_id(learner_id)
        if learner is None:
            raise ValueError("Learner not found")
        is_linked = await self.parent_report_repository.verify_guardian_link(
            learner_id=learner_id, guardian_id=guardian_id
        )
        if not is_linked:
            raise PermissionError("Guardian is not linked to this learner")
        return await self.parent_report_repository.get_reports_for_learner(
            learner_id=learner_id, guardian_id=guardian_id, limit=limit
        )
