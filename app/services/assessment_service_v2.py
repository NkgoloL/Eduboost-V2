from __future__ import annotations

from typing import Any

from app.services.audit_service import AuditService


class AssessmentServiceV2:
    def __init__(self, repository: Any) -> None:
        self.repository = repository

    async def list_assessments(self, limit: int = 20, offset: int = 0) -> dict:
        rows = await self.repository.list_assessments(limit=limit, offset=offset)
        await AuditService().log_event("ASSESSMENTS_LISTED", {"limit": limit, "offset": offset})
        return {"assessments": rows}

    async def submit_attempt(self, assessment_id: str, learner_id: str, responses: list[dict]) -> dict:
        assessment = await self.repository.get_assessment(assessment_id)
        if assessment is None:
            raise ValueError("Assessment not found")
        questions = assessment.get("questions", [])
        answer_map = {r["question_id"]: str(r.get("learner_answer", "")).strip().lower() for r in responses}
        correct_count = 0
        marks_obtained = 0
        for question in questions:
            expected = str(question.get("correct_answer", "")).strip().lower()
            if answer_map.get(question.get("question_id")) == expected:
                correct_count += 1
                marks_obtained += int(question.get("marks", 1))
        attempt_id = await self.repository.create_attempt(
            assessment_id=assessment_id,
            learner_id=learner_id,
            responses=responses,
            marks_obtained=marks_obtained,
        )
        await AuditService().log_event("ASSESSMENT_SUBMITTED", {"assessment_id": assessment_id}, learner_id)
        return {
            "attempt_id": attempt_id,
            "assessment_id": assessment_id,
            "learner_id": learner_id,
            "correct_count": correct_count,
            "marks_obtained": marks_obtained,
            "total_marks": assessment.get("total_marks", sum(int(q.get("marks", 1)) for q in questions)),
        }
