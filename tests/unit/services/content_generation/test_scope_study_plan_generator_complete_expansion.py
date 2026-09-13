import pytest

from app.services.content_generation.scope_study_plan_generator import (
    ScopeStudyPlanGenerator,
    _cycle,
    _slug,
    _teacher_cue,
)


def test_scope_study_plan_generator_complete():
    generator = ScopeStudyPlanGenerator()

    scope_id = "phase02_term1_math"
    caps_refs = ["CAPS.MATH.G4.T1", "CAPS.MATH.G4.T2"]
    contexts = {
        "CAPS.MATH.G4.T1": {
            "grade": 4,
            "subject": "Mathematics",
            "topic": "Whole Numbers",
            "common_misconceptions": ["place_value"],
            "assessment_standards": ["std1", "std2", "std3"],
        },
        "CAPS.MATH.G4.T2": {
            "grade": 4,
            "subject": "Mathematics",
            "topic": "Addition",
            "common_misconceptions": [],
        },
    }
    hashes = {"CAPS.MATH.G4.T1": "sha256:abcd"}

    plan = generator.generate(scope_id, caps_refs, contexts, source_context_hashes=hashes)

    assert plan["schema_version"] == "1.0"
    assert plan["scope"] == scope_id
    assert plan["grade"] == 4
    assert plan["subject"] == "Mathematics"

    assert len(plan["weekly_template"]) == 5
    assert len(plan["topic_sequence"]) == 2
    assert len(plan["remediation_mappings"]) >= 2
    assert len(plan["extension_mappings"]) == 2


def test_helper_functions():
    assert _slug("scope_with_underscores") == "scope-with-underscores"
    assert _cycle(("a", "b"), 0) == "a"
    assert _cycle(("a", "b"), 1) == "b"
    assert _cycle(("a", "b"), 2) == "a"

    cue_lesson = _teacher_cue("lesson", "Fractions")
    assert "Teach Fractions" in cue_lesson
    cue_practice = _teacher_cue("practice", "Fractions")
    assert "Run the short practice quiz" in cue_practice
    cue_review = _teacher_cue("review", "Fractions")
    assert "Use the recheck blueprint" in cue_review
