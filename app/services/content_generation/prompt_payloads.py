"""Typed payloads for grounded Content Factory generation."""
from __future__ import annotations

from pydantic import BaseModel, Field


class SourceContextChunk(BaseModel):
    source_document_id: str
    source_chunk_id: str
    text: str
    source_title: str | None = None
    source_hash: str | None = None
    curriculum_mapping_id: str | None = None
    source_quality_score: float | None = None
    license_status: str | None = None
    document_status: str = "approved"


class GenerationRequestBase(BaseModel):
    scope_id: str
    caps_ref: str
    grade: int
    subject_code: str
    language: str
    topic_title: str
    required_count: int
    approved_count: int
    missing_count: int
    source_chunks: list[SourceContextChunk]
    source_document_ids: list[str] = Field(default_factory=list)
    source_chunk_ids: list[str] = Field(default_factory=list)
    source_quality_scores: list[float] = Field(default_factory=list)
    license_statuses: list[str] = Field(default_factory=list)
    prompt_version: str = "cf-gen-v1"


class DiagnosticGenerationRequest(GenerationRequestBase):
    pass


class LessonGenerationRequest(GenerationRequestBase):
    pass


class GeneratedDiagnosticItem(BaseModel):
    question_text: str
    options: list[str]
    correct_answer: str
    explanation: str
    caps_ref: str
    grade: int
    subject_code: str
    language: str
    difficulty: str = "medium"
    cognitive_level: str = "understand"
    source_chunk_ids: list[str]
    item_type: str = "single_choice"
    safety_status: str = "passed"

    def to_artifact_json(self) -> dict:
        return {
            "question_text": self.question_text,
            "options": self.options,
            "answer_key": {"correct_answer": self.correct_answer},
            "explanation": self.explanation,
            "caps_ref": self.caps_ref,
            "grade": self.grade,
            "subject_code": self.subject_code,
            "language": self.language,
            "difficulty": self.difficulty,
            "cognitive_level": self.cognitive_level,
            "source_chunk_ids": self.source_chunk_ids,
            "item_type": self.item_type,
            "safety_status": self.safety_status,
        }


class GeneratedLesson(BaseModel):
    title: str
    summary: str
    learning_objectives: list[str]
    teacher_notes: str
    learner_activity: str
    worked_examples: list[str]
    practice_questions: list[str]
    answer_key: list[str]
    caps_ref: str
    grade: int
    subject_code: str
    language: str
    source_chunk_ids: list[str]
    safety_status: str = "passed"

    def to_artifact_json(self) -> dict:
        return {
            "title": self.title,
            "summary": self.summary,
            "learning_objectives": self.learning_objectives,
            "teacher_notes": self.teacher_notes,
            "learner_activity": self.learner_activity,
            "worked_examples": self.worked_examples,
            "practice_questions": self.practice_questions,
            "answer_key": self.answer_key,
            "caps_ref": self.caps_ref,
            "grade": self.grade,
            "subject_code": self.subject_code,
            "language": self.language,
            "source_chunk_ids": self.source_chunk_ids,
            "safety_status": self.safety_status,
        }
