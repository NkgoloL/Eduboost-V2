from unittest.mock import AsyncMock, MagicMock
import pytest

from app.models.content_factory import ContentArtifactStatus
from app.services.content_generation.scope_item_generator import (
    ITEM_DIFFICULTY_BANDS,
    ScopeItemGenerator,
    _compact_stem,
    _learner_explanation,
    _rewrite_young_stem,
)
from app.services.content_generation.scope_lesson_generator import ScopeLessonGenerator
from app.services.content_generation.study_plan_template_generator import (
    StudyPlanTemplateGenerationResult,
    StudyPlanTemplateGenerator,
)
from app.services.content_generation.topic_map_source_context import TopicMapSourceContext


def _make_context(grade: int = 4, subject: str = "Mathematics", subject_code: str = "MATH") -> TopicMapSourceContext:
    return TopicMapSourceContext(
        scope_id="scope_grade4_math",
        caps_ref="4.M.1.1",
        grade=grade,
        phase="intermediate",
        subject=subject,
        subject_code=subject_code,
        language="en",
        topic="Numbers and Operations",
        subtopic="Place Value",
        term=1,
        weeks="1-2",
        assessment_standards=("Identify place value", "Compare whole numbers"),
        learning_outcomes=("Understand place values",),
        prerequisites=("Count to 1000",),
        common_misconceptions=("Confusing tens and units", "Reversing digits"),
        vocabulary=("place value", "thousands", "hundreds", "tens", "units"),
        source_document_ids=("doc1",),
        source_text_snippets=("Evidence text from Grade 4 curriculum",),
        context_hash="hash_12345",
    )



def test_scope_item_generator_components():
    gen = ScopeItemGenerator()
    ctx = _make_context(grade=4)

    # 1. Stem rewriting, compacting, and FK shortening
    from app.services.content_generation.scope_item_generator import _finalize_item_stem
    stem_raw = "Which option best summarises a paragraph when solving a Grade 4 problem about whole numbers?"
    rewritten = _rewrite_young_stem(stem_raw)
    assert "best summary" in rewritten or "sums up" in rewritten

    compacted = _compact_stem("What is 5 + 5 for learners in a Grade 4 question about place value?", grade=4)
    assert "for learners" not in compacted

    long_stem = "A very sophisticated and extraordinarily complicated apparatus inquiry for experimental procedures on scientific observations linked to atmospheric chemistry."
    finalized_seq0 = _finalize_item_stem(long_stem, grade=4, sequence=0)
    assert finalized_seq0.endswith("?")

    finalized_seq1 = _finalize_item_stem(long_stem, grade=4, sequence=1)
    assert finalized_seq1.startswith("Q2.")

    # Grade > 6 returns stem untouched
    stem_older = _compact_stem("Complex Grade 10 calculus stem?", grade=10)
    assert stem_older == "Complex Grade 10 calculus stem?"

    # Short explanation gets padded
    expl_short = _learner_explanation("4 is correct.")
    assert "Read the question carefully" in expl_short
    expl_long = _learner_explanation("This explanation has more than ten words in total so it remains as is.")
    assert expl_long.startswith("This explanation")


    # 2. Generate item across bands with sequence and duplicate text formatting
    for idx, band in enumerate(ITEM_DIFFICULTY_BANDS):
        item = gen.generate(ctx, index=idx, band=band, scope_id="scope_test", sequence=idx + 1)
        assert item["item_type"] == "mcq"
        assert item["difficulty_band"] == band
        assert len(item["options"]) == 4
        assert item["answer_key"] in {"A", "B", "C", "D"}
        assert item["review_status"] == "approved"
        assert item["stem"].startswith(f"Q{idx + 2}.")



def test_scope_lesson_generator_components():
    gen = ScopeLessonGenerator()

    # Test across multiple subject families
    families = [
        ("Mathematics", "MATH"),
        ("English First Additional Language", "EFAL"),
        ("Natural Sciences", "NS"),
        ("Social Sciences", "SS"),
        ("Life Skills", "LS"),
        ("Creative Arts", "CA"),
    ]
    for subject, code in families:
        ctx = _make_context(grade=4, subject=subject, subject_code=code)
        lesson = gen.generate(ctx, index=0)
        assert len(lesson["worked_examples"]) >= 1
        assert len(lesson["practice_questions"]) >= 1
        assert len(lesson["answer_key"]) >= 1



@pytest.mark.asyncio
async def test_study_plan_template_generator():
    gen = StudyPlanTemplateGenerator()
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()

    # 1. Successful deterministic generation
    res = await gen.generate(
        session,
        scope_id="scope_test",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        language="en",
    )
    assert isinstance(res, StudyPlanTemplateGenerationResult)
    assert res.status == ContentArtifactStatus.PENDING_REVIEW.value
    assert session.add.called
    assert session.flush.await_count == 1

    # 2. Validation failure case
    bad_payload = {"caps_ref": "different_ref"}
    errors = gen._validate_template(bad_payload, "scope_test", "4.M.1.1")
    assert len(errors) >= 2
    assert any("mismatch" in e for e in errors)
    assert any("diagnostic_trigger_conditions" in e for e in errors)
