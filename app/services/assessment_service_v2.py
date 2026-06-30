from __future__ import annotations

from typing import Any

from app.services.audit_service import AuditService


class AssessmentServiceV2:
    def __init__(self, repository: Any | None = None) -> None:
        if repository is None:
            from app.repositories.assessment_repository import AssessmentRepository
            repository = AssessmentRepository()
        self.repository = repository

    async def list_assessments(self, limit: int = 20, offset: int = 0) -> dict:
        rows = await self.repository.list_assessments(limit=limit, offset=offset)
        await AuditService().log_event("ASSESSMENTS_LISTED", {"limit": limit, "offset": offset})
        return {"assessments": rows}

    async def submit_attempt(
        self,
        assessment_id: str,
        learner_id: str,
        responses: list[dict],
        time_taken_seconds: int = 0,
    ) -> dict:
        assessment = await self.repository.get_assessment(assessment_id)
        if assessment is None:
            raise ValueError("Assessment not found")
        questions = assessment.get("questions", [])
        answer_map = {}
        for response in responses:
            response_id = response.get("question_id") or response.get("item_id")
            answer = response.get("learner_answer") or response.get("selected_option") or response.get("answer") or ""
            if response_id:
                answer_map[str(response_id)] = str(answer).strip().lower()
        correct_count = 0
        marks_obtained = 0
        for question in questions:
            expected = str(question.get("correct_answer", "")).strip().lower()
            question_id = str(question.get("question_id") or question.get("item_id") or "")
            if answer_map.get(question_id) == expected:
                correct_count += 1
                marks_obtained += int(question.get("marks", 1))
        total_marks = int(assessment.get("total_marks") or sum(int(q.get("marks", 1)) for q in questions))
        score = round(marks_obtained / total_marks, 4) if total_marks else 0.0
        attempt_id = await self.repository.create_attempt(
            assessment_id=assessment_id,
            learner_id=learner_id,
            responses=responses,
            score=score,
            marks_obtained=marks_obtained,
            time_taken_seconds=time_taken_seconds,
        )
        await AuditService().log_event("ASSESSMENT_SUBMITTED", {"assessment_id": assessment_id}, learner_id)
        return {
            "attempt_id": attempt_id,
            "assessment_id": assessment_id,
            "learner_id": learner_id,
            "correct_count": correct_count,
            "marks_obtained": marks_obtained,
            "score": score,
            "total_marks": total_marks,
        }
