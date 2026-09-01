"""Batch 240 — ScopeItemGenerator comprehensive branch coverage expansion.

Tests:
- _compact_stem: grade > 6 vs grade <= 6 with various regex simplifications
- _rewrite_young_stem: replacement patterns and dictionary lookups
- _finalize_item_stem: sequence=0 vs sequence>0, question mark appending, readability shortening
- _learner_explanation: short explanations (<10 words) vs standard explanations
- ScopeItemGenerator:
  - all difficulty bands (easy, moderate, on_level, challenging, unknown)
  - option text deduplication loop
  - distractor rationale dictionary
  - IRT parameter verification (difficulty_b, discrimination_a, guessing_c)
"""
from __future__ import annotations

import pytest

from app.services.content_generation.scope_item_generator import (
    ITEM_DIFFICULTY_BANDS,
    ScopeItemGenerator,
    _compact_stem,
    _finalize_item_stem,
    _learner_explanation,
    _rewrite_young_stem,
)
from app.services.content_generation.topic_map_source_context import TopicMapSourceContext


def make_context(grade: int = 4) -> TopicMapSourceContext:
    return TopicMapSourceContext(
        scope_id="term_1_maths",
        caps_ref="4.M.1.1",
        grade=grade,
        phase="intermediate",
        subject="Mathematics",
        subject_code="MATH",
        language="en",
        topic="Addition",
        subtopic="Column Addition",
        term=1,
        weeks="1-2",
        assessment_standards=("Demonstrates addition mastery",),
        learning_outcomes=("Adds multi-digit numbers",),
        prerequisites=("Counting",),
        common_misconceptions=("Carry over error",),
        vocabulary=("carry", "units", "tens"),
        source_document_ids=("doc-1",),
        source_text_snippets=("Add numbers in columns starting from units.",),
        context_hash="hash_ctx_123",
    )


# ---------------------------------------------------------------------------
# Stem and Explanation Helpers
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_compact_and_rewrite_young_stem():
    # Grade > 6 returns original
    stem_g8 = "Which option best summarises a paragraph when solving a Grade 8 problem about integers?"
    assert _compact_stem(stem_g8, grade=8) == stem_g8

    # Grade <= 6 simplifies
    stem_g4 = "Which option best summarises a paragraph when solving a Grade 4 problem about addition?"
    compacted = _compact_stem(stem_g4, grade=4)
    assert "Grade 4" not in compacted

    # _rewrite_young_stem replacements and single word dictionary
    rewritten = _rewrite_young_stem("Which option best summarises a paragraph about fractions?")
    assert "summary" in rewritten or "sums up" in rewritten

    rewritten_words = _rewrite_young_stem("The apparatus was appropriate for the algorithm.")
    assert "tool" in rewritten_words
    assert "right" in rewritten_words
    assert "plan" in rewritten_words


@pytest.mark.unit
def test_finalize_item_stem_and_learner_explanation():
    # Sequence 0 vs Sequence 1
    raw = "What is 2 + 2"
    stem_0 = _finalize_item_stem(raw, grade=4, sequence=0)
    assert stem_0.endswith("?")
    assert not stem_0.startswith("Q")

    stem_1 = _finalize_item_stem(raw, grade=4, sequence=1)
    assert stem_1.startswith("Q2. ")
    assert stem_1.endswith("?")

    # _learner_explanation (< 10 words vs >= 10 words)
    exp_short = _learner_explanation("Correct answer is 4.")
    assert "Read the question carefully" in exp_short

    exp_long = _learner_explanation(
        "First add the ones column, carry the tens over, and then sum the tens column correctly."
    )
    assert "Read the question carefully" not in exp_long


# ---------------------------------------------------------------------------
# ScopeItemGenerator Generation Flow
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_scope_item_generator_bands_and_options():
    generator = ScopeItemGenerator()
    ctx = make_context(grade=4)

    for idx, band in enumerate(ITEM_DIFFICULTY_BANDS):
        item = generator.generate(
            ctx,
            index=idx,
            band=band,
            scope_id="term_1_maths",
            sequence=idx,
        )
        assert item["difficulty_band"] == band
        assert item["item_type"] == "mcq"
        assert item["safety_passed"] is True
        assert len(item["options"]) == 4
        assert item["answer_key"] in {"A", "B", "C", "D"}
        assert len(item["distractor_rationale"]) == 3
        assert isinstance(item["difficulty_b"], float)
        assert isinstance(item["discrimination_a"], float)
        assert item["guessing_c"] == 0.25

    # Unknown band fallback to on_level
    item_unknown = generator.generate(
        ctx,
        index=0,
        band="unknown_band",
        scope_id="term_1_maths",
    )
    assert item_unknown["difficulty_band"] == "unknown_band"
