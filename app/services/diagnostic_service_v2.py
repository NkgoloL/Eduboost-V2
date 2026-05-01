"""V2 diagnostic service using the existing 2PL IRT engine under modular-monolith boundaries."""

from __future__ import annotations

from typing import Any

from app.api.ml.irt_engine import (
    AssessmentSession,
    SAMPLE_ITEMS,
    SubjectCode,
    activate_gap_probe,
    build_gap_report,
    check_gap_trigger,
    compute_mastery_score,
    select_next_item,
    should_stop,
    update_theta_mle,
)
from app.repositories.diagnostic_repository import DiagnosticRepository
from app.repositories.learner_repository import LearnerRepository
from app.services.quota_service import QuotaService


class DiagnosticServiceV2:
    def __init__(
        self,
        learner_repository: LearnerRepository | None = None,
        quota_service: QuotaService | None = None,
        diagnostic_repository: DiagnosticRepository | None = None,
    ) -> None:
        self.learner_repository = learner_repository or LearnerRepository()
        self.quota_service = quota_service or QuotaService()
        self.diagnostic_repository = diagnostic_repository or DiagnosticRepository()

    async def run_diagnostic(self, learner_id: str, subject_code: str, max_questions: int = 10) -> dict[str, Any]:
        learner = await self.learner_repository.get_by_id(learner_id)
        if learner is None:
            raise ValueError("Learner not found")

        await self.quota_service.assert_within_quota(f"diagnostic:{learner_id}")
        cache_payload = {"learner_id": learner_id, "subject_code": subject_code, "max_questions": max_questions}
        cached = await self.quota_service.get_cached("diagnostic", cache_payload)
        if cached is not None:
            return cached

        subject = SubjectCode(subject_code)
        session = AssessmentSession(learner_grade=learner.grade, subject=subject)
        items_by_id = {item.item_id: item for item in SAMPLE_ITEMS}
        administered = set()

        while not should_stop(session, max_questions=max_questions):
            item = select_next_item(session, SAMPLE_ITEMS, administered)
            if item is None:
                break
            administered.add(item.item_id)
            synthetic_correct = learner.overall_mastery >= 0.5 or item.grade <= learner.grade
            response = type("Resp", (), {"item_id": item.item_id, "is_correct": synthetic_correct, "time_on_task_ms": 1200})
            session.responses.append(response)
            session.theta, session.sem = update_theta_mle(session.responses, items_by_id)
            if check_gap_trigger(session):
                activate_gap_probe(session)

        report = build_gap_report(session)
        await self.diagnostic_repository.create_session(
            learner_id=learner_id,
            subject_code=subject_code,
            grade_level=learner.grade,
            theta=session.theta,
            sem=session.sem,
            items_administered=len(session.responses),
            items_correct=sum(1 for r in session.responses if r.is_correct),
            items_total=max_questions,
            final_mastery_score=compute_mastery_score(session.theta),
            knowledge_gaps=report.get("probe_grades_visited", []),
        )

        result = {
            "learner_id": learner_id,
            "subject_code": subject_code,
            "questions_administered": len(session.responses),
            "theta": session.theta,
            "sem": session.sem,
            "gap_report": report,
        }
        await self.quota_service.set_cached("diagnostic", cache_payload, result)
        return result
