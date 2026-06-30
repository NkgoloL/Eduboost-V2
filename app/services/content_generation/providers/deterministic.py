"""Safe deterministic generation provider for tests and local dry runs."""
from __future__ import annotations

from app.services.content_generation.prompt_payloads import (
    DiagnosticGenerationRequest,
    GeneratedDiagnosticItem,
    GeneratedLesson,
    LessonGenerationRequest,
)


class DeterministicContentGenerationProvider:
    provider_name = "deterministic"
    model_name = "deterministic-local-v1"

    async def generate_diagnostic_items(
        self,
        request: DiagnosticGenerationRequest,
    ) -> list[GeneratedDiagnosticItem]:
        count = max(0, request.missing_count)
        chunk_ids = request.source_chunk_ids or [chunk.source_chunk_id for chunk in request.source_chunks]
        return [
            GeneratedDiagnosticItem(
                question_text=f"{request.topic_title}: diagnostic question {index + 1} for {request.caps_ref}",
                options=["A", "B", "C", "D"],
                correct_answer="A",
                explanation=f"Grounded in source chunk {chunk_ids[index % len(chunk_ids)]}.",
                caps_ref=request.caps_ref,
                grade=request.grade,
                subject_code=request.subject_code,
                language=request.language,
                source_chunk_ids=[chunk_ids[index % len(chunk_ids)]],
            )
            for index in range(count)
        ]

    async def generate_lessons(
        self,
        request: LessonGenerationRequest,
    ) -> list[GeneratedLesson]:
        count = max(0, request.missing_count)
        chunk_ids = request.source_chunk_ids or [chunk.source_chunk_id for chunk in request.source_chunks]
        return [
            GeneratedLesson(
                title=f"{request.topic_title} lesson {index + 1}",
                summary=f"Grade {request.grade} {request.subject_code} lesson for {request.caps_ref}.",
                learning_objectives=[f"Understand {request.topic_title}", f"Apply {request.caps_ref}"],
                teacher_notes=f"Use source chunk {chunk_ids[index % len(chunk_ids)]} as the primary reference.",
                learner_activity=f"Complete a short activity about {request.topic_title}.",
                worked_examples=[f"Worked example {index + 1}"],
                practice_questions=[f"Practice question {index + 1}"],
                answer_key=[f"Practice answer {index + 1}"],
                caps_ref=request.caps_ref,
                grade=request.grade,
                subject_code=request.subject_code,
                language=request.language,
                source_chunk_ids=[chunk_ids[index % len(chunk_ids)]],
            )
            for index in range(count)
        ]

    async def generate_assessment_blueprints(
        self,
        request: dict,
    ) -> list[dict]:
        """Generate deterministic assessment blueprints."""
        count = request.get("missing_count", 1)
        caps_ref = request.get("caps_ref", "")
        scope_id = request.get("scope_id", "")
        return [
            {
                "scope_id": scope_id,
                "caps_ref": caps_ref,
                "grade": request.get("grade"),
                "subject_code": request.get("subject_code"),
                "language": request.get("language", "en"),
                "title": f"Assessment Blueprint for {caps_ref}",
                "assessment_type": "summative",
                "question_mix": {"multiple_choice": 10, "short_answer": 5},
                "cognitive_level_distribution": {"recall": 3, "application": 7, "analysis": 5},
                "linked_diagnostic_item_ids": [],
                "rubric": {"criteria": ["accuracy", "completeness"]},
                "answer_key_policy": "provided",
                "source_chunk_ids": request.get("source_chunk_ids", []),
            }
            for _ in range(count)
        ]

    async def generate_study_plan_templates(
        self,
        request: dict,
    ) -> list[dict]:
        """Generate deterministic study-plan templates."""
        count = request.get("missing_count", 1)
        caps_ref = request.get("caps_ref", "")
        scope_id = request.get("scope_id", "")
        return [
            {
                "scope_id": scope_id,
                "caps_ref": caps_ref,
                "grade": request.get("grade"),
                "subject_code": request.get("subject_code"),
                "language": request.get("language", "en"),
                "title": f"Study Plan Template for {caps_ref}",
                "diagnostic_trigger_conditions": {"score_below": 60},
                "recommended_lesson_ids": [],
                "practice_item_ids": [],
                "remediation_steps": ["review_concepts", "practice_exercises"],
                "extension_steps": ["advanced_problems", "real_world_applications"],
                "estimated_minutes": 45,
                "source_chunk_ids": request.get("source_chunk_ids", []),
            }
            for _ in range(count)
        ]
