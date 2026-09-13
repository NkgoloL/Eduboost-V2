import json
from pathlib import Path
import pytest

from app.services.content_generation.topic_map_source_context import (
    MIN_CONTEXT_TEXT_LENGTH,
    TopicMapSourceContext,
    TopicMapSourceContextBuilder,
    TopicMapSourceContextResult,
    _extract_vocabulary,
    _paragraphs,
)


def test_topic_map_source_context_model():
    ctx = TopicMapSourceContext(
        scope_id="scope_1",
        caps_ref="CAPS.MATH.G4.T1",
        grade=4,
        phase="intermediate",
        subject="Mathematics",
        subject_code="MATH",
        language="en",
        topic="Fractions",
        subtopic="Equivalent Fractions",
        term=1,
        weeks="1-2",
        assessment_standards=("std1",),
        learning_outcomes=("out1",),
        prerequisites=("pre1",),
        common_misconceptions=("misc1",),
        vocabulary=("fraction", "half"),
        source_document_ids=("doc1",),
        source_text_snippets=("snippet1 that is long enough",),
        context_hash="hash1",
    )
    assert ctx.passed is True
    d = ctx.to_dict()
    assert d["scope_id"] == "scope_1"
    assert d["grade"] == 4
    assert d["assessment_standards"] == ["std1"]


def test_builder_successful(tmp_path):
    # Prepare topic map file
    extract_file = tmp_path / "extract.txt"
    extract_content = (
        "Fractions represent equal parts of a whole object or collection.\n\n"
        "When students learn about fractions, they compare numerators and denominators.\n\n"
        "Equivalent fractions have the same value even though they look different."
    )
    extract_file.write_text(extract_content, encoding="utf-8")

    topic_map_file = tmp_path / "topic_map.json"
    topic_map_data = {
        "_meta": {
            "source_document_ids": ["doc_meta_1"],
            "source_text_extract_paths": [str(extract_file.relative_to(tmp_path))],
        }
    }
    topic_map_file.write_text(json.dumps(topic_map_data), encoding="utf-8")

    builder = TopicMapSourceContextBuilder(project_root=tmp_path)
    res = builder.build(
        scope_id="sc_01",
        caps_ref="CAPS.MATH.G4.FRAC",
        topic_context={
            "grade": 4,
            "subject": "Mathematics",
            "subject_code": "MATH",
            "topic": "Fractions",
            "subtopic": "Comparing Fractions",
            "term": 1,
            "weeks": "Week 1",
            "assessment_standards": ["Compare fractions with the same denominator and solve word problems."],
            "learning_outcomes": ["Identify equivalent fractions."],
            "prerequisites": ["Whole numbers"],
            "common_misconceptions": ["Larger denominator means larger number."],
        },
        topic_map_path=str(topic_map_file.relative_to(tmp_path)),
        source_document_ids=["doc_custom"],
        phase="intermediate",
        language="en",
    )

    assert res.passed is True
    assert res.errors == []
    assert res.context is not None
    assert res.context.grade == 4
    assert res.context.subtopic == "Comparing Fractions"
    assert len(res.context.source_text_snippets) > 0


def test_builder_errors_and_fallbacks(tmp_path):
    # 1. Nonexistent extract path and empty standards / docs
    topic_map_file = tmp_path / "empty_map.json"
    topic_map_file.write_text(json.dumps({
        "_meta": {
            "source_text_extract_paths": ["nonexistent_extract.txt"],
        }
    }), encoding="utf-8")

    builder = TopicMapSourceContextBuilder(project_root=tmp_path)
    res = builder.build(
        scope_id="sc_02",
        caps_ref="CAPS.EMPTY",
        topic_context={
            # No standards or learning_outcomes
            "topic": "Short",
        },
        topic_map_path=str(topic_map_file.relative_to(tmp_path)),
        source_document_ids=[],
    )

    assert res.passed is False
    assert any("lacks assessment standards" in err for err in res.errors)
    assert any("lacks source document ids" in err for err in res.errors)
    assert any("too thin for grounded generation" in err for err in res.errors)


def test_paragraphs_and_vocabulary():
    # Double newline splits paragraphs
    multi_p = "Paragraph one\n\nParagraph two"
    assert len(_paragraphs(multi_p)) == 2

    # When chunks is empty after stripping:
    assert _paragraphs("   \n\n   ") == []

    # _extract_vocabulary
    vocab = _extract_vocabulary(
        {"topic": "Algebraic Expressions", "subtopic": "Variables and Constants", "skill": "Substitution"},
        snippets=("Evaluation of mathematical equations requires understanding.",),
    )
    assert "Algebraic" in vocab
    assert "Expressions" in vocab

