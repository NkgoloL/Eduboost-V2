"""Enhanced validation for generated lesson payloads."""
from __future__ import annotations

from app.services.content_generation.prompt_payloads import GeneratedLesson


class LessonGenerator:
    def validate(
        self,
        lesson: GeneratedLesson,
        *,
        caps_ref: str,
        existing_hashes: set[str] | None = None,
        artifact_hash: str | None = None,
    ) -> list[str]:
        errors: list[str] = []
        if not lesson.learning_objectives:
            errors.append("lesson requires learning objectives.")
        if lesson.practice_questions and not lesson.answer_key:
            errors.append("lesson requires an answer key for practice questions.")
        if lesson.caps_ref != caps_ref:
            errors.append(f"lesson caps_ref {lesson.caps_ref} does not match task caps_ref {caps_ref}.")
        if not lesson.source_chunk_ids:
            errors.append("lesson requires source citations.")
        if lesson.grade < 0 or lesson.grade > 12:
            errors.append("lesson grade must be age appropriate.")
        if artifact_hash and existing_hashes and artifact_hash in existing_hashes:
            errors.append("lesson duplicates an existing artifact hash.")
        return errors
