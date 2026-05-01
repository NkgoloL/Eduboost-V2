"""V2 assessments service."""

from __future__ import annotations

from app.repositories.assessment_repository import AssessmentRepository
from app.services.audit_service import AuditService


class AssessmentServiceV2:
    def __init__(self, repository: AssessmentRepository | None = None) -> None:
        self.repository = repository or AssessmentRepository()

    async def list_assessments(self, limit: int = 50, offset: int = 0) -> dict:
        rows = await self.repository.list_assessments(limit=limit, offset=offset)
        await AuditService().log_event(event_type="ASSESSMENTS_LIST_READ", payload={"count": len(rows)})
        return {"assessments": rows, "limit": limit, "offset": offset}

    async def submit_attempt(self, assessment_id: str, learner_id: str, responses: list[dict], time_taken_seconds: int = 0) -> dict:
        assessment = await self.repository.get_assessment(assessment_id)
        if assessment is None:
            raise ValueError("Assessment not found")
        questions = assessment["questions"] or []
        answers = {r["question_id"]: str(r["learner_answer"]).strip().lower() for r in responses}
        marks_obtained = 0
        correct_count = 0
        for q in questions:
            expected = str(q.get("correct_answer", "")).strip().lower()
            if answers.get(q.get("question_id")) == expected:
                marks_obtained += int(q.get("marks", 1))
                correct_count += 1
        total_marks = int(assessment["total_marks"] or 0)
        score = (marks_obtained / total_marks) if total_marks else 0.0
        attempt_id = await self.repository.create_attempt(
            assessment_id=assessment_id,
            learner_id=learner_id,
            score=score,
            marks_obtained=marks_obtained,
            time_taken_seconds=time_taken_seconds,
            responses=responses,
        )
        await AuditService().log_event(event_type="ASSESSMENT_ATTEMPT_SUBMITTED", learner_id=learner_id, payload={"assessment_id": assessment_id, "score": score})
        return {
            "attempt_id": attempt_id,
            "assessment_id": assessment_id,
            "learner_id": learner_id,
            "score": score,
            "marks_obtained": marks_obtained,
            "total_marks": total_marks,
            "correct_count": correct_count,
            "incorrect_count": max(0, len(questions) - correct_count),
        }
