import pytest

from app.services.content_generation.scope_blueprint_generator import (
    ScopeBlueprintGenerator,
    _safe_ref,
    _slug,
)


def test_scope_blueprint_generator_complete():
    gen = ScopeBlueprintGenerator()

    scope_id = "phase02_term1_math"
    caps_refs = ["CAPS.MATH.G4.T1", "CAPS.MATH.G4.T2"]
    contexts = {
        "CAPS.MATH.G4.T1": {
            "grade": 4,
            "subject": "Mathematics",
            "topic": "Whole Numbers",
            "common_misconceptions": ["place_value_confusion"],
        },
        "CAPS.MATH.G4.T2": {
            "grade": 4,
            "subject": "Mathematics",
            "topic": "Addition and Subtraction",
            "common_misconceptions": [],
        },
    }
    hashes = {"CAPS.MATH.G4.T1": "sha256:abcd1234"}

    result = gen.generate(scope_id, caps_refs, contexts, source_context_hashes=hashes)

    assert result["schema_version"] == "1.0"
    assert result["scope"] == scope_id
    assert result["grade"] == 4
    assert result["subject"] == "Mathematics"

    blueprints = result["blueprints"]
    # 1 baseline + 3 per caps_ref (topic_diagnostic, short_practice, mastery_check) = 1 + 2*3 = 7
    assert len(blueprints) == 7

    # Check baseline
    baseline = blueprints[0]
    assert baseline["type"] == "baseline_diagnostic"
    assert baseline["selection_rules"]["item_count"] == 4

    # Check _recheck method directly
    recheck = gen._recheck(
        slug=_slug(scope_id),
        safe_ref=_safe_ref("CAPS.MATH.G4.T1"),
        ref="CAPS.MATH.G4.T1",
        context=contexts["CAPS.MATH.G4.T1"],
        misconception_tags=["tag1"],
    )
    assert recheck["type"] == "recheck_assessment"
    assert recheck["linked_lesson_variant"] == "step_by_step"
