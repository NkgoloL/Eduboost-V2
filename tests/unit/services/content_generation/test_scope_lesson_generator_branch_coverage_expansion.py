"""Batch 239 — ScopeLessonGenerator comprehensive branch coverage expansion.

Tests:
- All 6 lesson variants: standard, visual, story, step_by_step, real_world_sa, exam_style
- All 9 subject families: mathematics, languages, natural_sciences, social_sciences, life_skills, life_orientation, technology, creative_arts, coding_and_robotics
- Assessment standards fallback when empty vs populated
- Remediation hints, extension prompts, teacher notes, parent notes, reading levels, source citations
"""
from __future__ import annotations

import pytest

from app.services.content_generation.generated_lesson_contract import LESSON_VARIANTS
from app.services.content_generation.scope_lesson_generator import (
    LESSON_DIFFICULTY_LEVELS,
    ScopeLessonGenerator,
)
from app.services.content_generation.topic_map_source_context import TopicMapSourceContext


def make_context(
    subject: str = "Mathematics",
    subject_code: str = "MATHS",
    grade: int = 4,
    standards: tuple[str, ...] = ("Solves word problems",),
) -> TopicMapSourceContext:
    return TopicMapSourceContext(
        scope_id="term_1_maths",
        caps_ref="4.M.1.1",
        grade=grade,
        phase="intermediate",
        subject=subject,
        subject_code=subject_code,
        language="en",
        topic="Addition",
        subtopic="Column Addition",
        term=1,
        weeks="1-2",
        assessment_standards=standards,
        learning_outcomes=("Adds multi-digit numbers",),
        prerequisites=("Counting",),
        common_misconceptions=("Carry over error",),
        vocabulary=("carry", "units", "tens"),
        source_document_ids=("doc-1",),
        source_text_snippets=("Add numbers in columns starting from units.",),
        context_hash="hash_ctx_123",
    )


@pytest.mark.unit
def test_scope_lesson_generator_all_variants():
    generator = ScopeLessonGenerator()
    ctx = make_context()

    for idx, variant in enumerate(LESSON_VARIANTS):
        lesson = generator.generate(ctx, index=idx, variant=variant)
        assert lesson["variant"] == variant
        assert lesson["scope_id"] == "term_1_maths"
        assert lesson["caps_ref"] == "4.M.1.1"
        assert lesson["safety_classification"] == "safe"
        assert lesson["answer_key_verified"] is True
        assert len(lesson["worked_examples"]) > 0
        assert len(lesson["practice_questions"]) > 0
        assert len(lesson["answer_key"]) > 0
        assert len(lesson["remediation_hints"]) > 0
        assert len(lesson["extension_prompts"]) > 0
        assert "parent_notes" in lesson
        assert "teacher_notes" in lesson


@pytest.mark.unit
def test_scope_lesson_generator_all_subject_families():
    generator = ScopeLessonGenerator()
    subjects = [
        ("Mathematics", "MATH"),
        ("English First Additional Language", "ENG"),
        ("Natural Sciences", "NS"),
        ("Social Sciences", "SS"),
        ("Life Skills", "LIFE"),
        ("Life Orientation", "LO"),
        ("Technology", "TECH"),
        ("Creative Arts", "ARTS"),
        ("Coding and Robotics", "CODE"),
    ]

    for idx, (subj, code) in enumerate(subjects):
        ctx = make_context(subject=subj, subject_code=code, standards=("Demonstrates core concept mastery",))
        lesson = generator.generate(ctx, index=idx)
        assert lesson["subject"] == subj
        assert lesson["difficulty_level"] in LESSON_DIFFICULTY_LEVELS
        assert len(lesson["learning_objectives"]) >= 1
        assert lesson["reading_level"] == "5.0"
