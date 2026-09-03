import pytest

from app.services.content_generation.scope_mcq_templates import (
    base_mcq_templates,
    content_family,
    extended_mcq_templates,
    options_for_template,
    pick_template,
    topic_phrase,
)
from app.services.content_generation.topic_map_source_context import TopicMapSourceContext


def _make_context(grade: int = 4, subtopic: str = "Numbers, Operations and Relationships") -> TopicMapSourceContext:
    return TopicMapSourceContext(
        scope_id="sc_01",
        caps_ref="CAPS.TEST",
        grade=grade,
        phase="intermediate",
        subject="Subject",
        subject_code="SUBJ",
        language="en",
        topic="General Topic",
        subtopic=subtopic,
        term=1,
        weeks="1-2",
        assessment_standards=("std1",),
        learning_outcomes=("out1",),
        prerequisites=("pre1",),
        common_misconceptions=("misc1",),
        vocabulary=("word1",),
        source_document_ids=("doc1",),
        source_text_snippets=("snippet text",),
        context_hash="hash",
    )


def test_content_family_aliases_and_topic_phrase():
    assert content_family("life_orientation") == "life_skills"
    assert content_family("technology") == "natural_sciences"
    assert content_family("mathematics") == "mathematics"

    # Short topic phrase
    assert topic_phrase("Fractions") == "fractions"
    # Long topic phrase with commas and multiple words
    long_topic = "Numbers, Operations and Relationships in Mathematics"
    phrase = topic_phrase(long_topic)
    assert len(phrase) <= 28


def test_options_for_template():
    tpl = {
        "answers": {"A": "Correct Answer", "B": "Distractor B", "C": "Distractor C", "D": "Distractor D"},
        "explanations": {"A": "Exp A", "B": "Exp B", "C": "Exp C", "D": "Exp D"},
    }
    # When correct option should be 'A'
    opts_a, exp_a = options_for_template(tpl, correct="A")
    assert opts_a["A"] == "Correct Answer"
    assert exp_a == "Exp A"

    # When correct option should be placed at 'C'
    opts_c, exp_c = options_for_template(tpl, correct="C")
    assert opts_c["C"] == "Correct Answer"
    assert exp_c == "Exp A"


@pytest.mark.parametrize(
    "family",
    [
        "mathematics",
        "languages",
        "natural_sciences",
        "social_sciences",
        "coding_and_robotics",
        "life_skills",
    ],
)
def test_all_families_base_and_extended_templates(family):
    ctx = _make_context(grade=4, subtopic="Addition and Subtraction of Whole Numbers")

    # Base templates
    base = base_mcq_templates(ctx, family=family, sequence=1)
    assert len(base) >= 3
    for t in base:
        assert "question_text" in t
        assert "answers" in t
        assert "explanations" in t

    # Extended templates
    ext = extended_mcq_templates(ctx, family=family, sequence=2, band="moderate")
    assert len(ext) >= len(base)

    # Pick template
    picked = pick_template(ctx, family=family, sequence=0, band="on_level", extended=True)
    assert "question_text" in picked
    assert "answers" in picked

    picked_base = pick_template(ctx, family=family, sequence=0, band="on_level", extended=False)
    assert "question_text" in picked_base
