"""
tests/unit/modules/diagnostics/test_item_validator.py
─────────────────────────────────────────────────────────────────────────────
Phase 2/3: Unit Tests for ItemValidator (P2-09)

Tests every validation rule independently:
  - Valid item passes all rules
  - Each rule catches its specific failure mode
  - Boundary conditions for IRT params and readability
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import pytest
from copy import deepcopy

from app.modules.diagnostics.item_validator import (
    ItemValidator,
    ValidationError,
    flesch_kincaid_grade,
    MAX_FK_GRADE,
    MIN_OPTIONS,
    VALID_IRT_BOUNDS,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MOCK_TOPIC_MAP = {
    "topics": {
        "4.M.1.1": {
            "grade": 4, "subject": "Mathematics", "term": 1,
            "topic": "Whole Numbers",
            "subtopic": "Count, Order and Compare 4-digit Numbers",
            "skill": "place_value_ordering",
            "learning_outcomes": ["Count forwards and backwards up to 10 000"],
        },
        "4.M.1.2": {
            "grade": 4, "subject": "Mathematics", "term": 1,
            "topic": "Common Fractions",
            "subtopic": "Name, Order and Compare Fractions",
            "skill": "fraction_comparison",
            "learning_outcomes": ["Name and write fractions: halves, quarters"],
        },
    }
}


def _valid_item(**overrides) -> dict:
    """Returns a fully valid item dict. Use overrides to test specific failures."""
    item = {
        "item_id":        "aaaabbbb-0000-1111-2222-ccccddddeeee",
        "caps_ref":       "4.M.1.1",
        "grade":          4,
        "subject":        "Mathematics",
        "term":           1,
        "topic":          "Whole Numbers",
        "subtopic":       "Count, Order and Compare 4-digit Numbers",
        "skill":          "place_value_ordering",
        "stem":           "Sipho counts apples in groups of ten. He has 3 000 apples, then gets 400 more. How many does he have?",
        "answer_key":     "B",
        "options": [
            {"label": "A", "text": "3 040"},
            {"label": "B", "text": "3 400"},
            {"label": "C", "text": "3 004"},
            {"label": "D", "text": "7 000"},
        ],
        "explanation":    "You add the hundreds to the thousands. 3 000 plus 400 equals 3 400. The digit 4 is in the hundreds place, not the ones place.",
        "distractor_rationale": {
            "A": "A learner might confuse 400 with 40, placing the digit in the wrong column.",
            "C": "A learner might put 4 in the ones place instead of the hundreds place.",
            "D": "A learner might multiply instead of add.",
        },
        "misconception_tags": ["place_value_confusion", "addition_error"],
        "item_type":       "mcq",
        "language":        "en",
        "difficulty_b":    -0.5,
        "discrimination_a": 1.0,
        "guessing_c":      0.25,
        "safety_passed":   True,
        "review_status":   "approved",
    }
    item.update(overrides)
    return item


@pytest.fixture
def validator():
    return ItemValidator(topic_map=MOCK_TOPIC_MAP)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

class TestValidItemPasses:

    def test_valid_item_passes_all_rules(self, validator):
        """A fully correct item must pass without raising."""
        item = _valid_item()
        # Should not raise
        validator.validate(item)

    def test_validate_all_returns_empty_list_for_valid_item(self, validator):
        item = _valid_item()
        errors = validator.validate_all(item)
        assert errors == [], f"Expected no errors, got: {errors}"


# ---------------------------------------------------------------------------
# Rule 1: CAPS ref exists in topic map
# ---------------------------------------------------------------------------

class TestCapsRefExists:

    def test_missing_caps_ref_fails(self, validator):
        item = _valid_item(caps_ref="")
        errors = validator.validate_all(item)
        assert any(e.rule == "caps_ref" for e in errors)

    def test_unknown_caps_ref_fails(self, validator):
        item = _valid_item(caps_ref="9.Z.9.9")
        errors = validator.validate_all(item)
        assert any(e.rule == "caps_ref" for e in errors)

    def test_known_caps_ref_passes(self, validator):
        item = _valid_item(caps_ref="4.M.1.2")
        errors = validator.validate_all(item)
        assert not any(e.rule == "caps_ref" for e in errors)

    def test_no_topic_map_skips_caps_ref_check(self):
        """Without a topic map, caps_ref validation is skipped (not blocking)."""
        validator_no_map = ItemValidator(topic_map={})
        item = _valid_item(caps_ref="4.M.9.9")  # unknown ref
        errors = validator_no_map.validate_all(item)
        assert not any(e.rule == "caps_ref" for e in errors)


# ---------------------------------------------------------------------------
# Rule 2: answer_key matches one of options[].label
# ---------------------------------------------------------------------------

class TestAnswerKeyMatchesOption:

    def test_correct_answer_key_passes(self, validator):
        item = _valid_item(answer_key="B")
        errors = validator.validate_all(item)
        assert not any(e.rule == "answer_key" for e in errors)

    def test_missing_answer_key_fails(self, validator):
        item = _valid_item(answer_key="")
        errors = validator.validate_all(item)
        assert any(e.rule == "answer_key" for e in errors)

    def test_answer_key_not_in_options_fails(self, validator):
        item = _valid_item(answer_key="E")  # No option E
        errors = validator.validate_all(item)
        assert any(e.rule == "answer_key" for e in errors)

    def test_case_insensitive_answer_key(self, validator):
        item = _valid_item(answer_key="b")  # lowercase
        errors = validator.validate_all(item)
        assert not any(e.rule == "answer_key" for e in errors)


# ---------------------------------------------------------------------------
# Rule 3: stem readability ≤ Grade 6 FK
# ---------------------------------------------------------------------------

class TestStemReadability:

    def test_simple_stem_passes(self, validator):
        item = _valid_item(stem="Nomsa has 5 apples. She gives away 2. How many are left?")
        errors = validator.validate_all(item)
        assert not any(e.rule == "stem_readability" for e in errors)

    def test_empty_stem_fails(self, validator):
        item = _valid_item(stem="")
        errors = validator.validate_all(item)
        assert any(e.rule == "stem_readability" for e in errors)

    def test_complex_stem_fails_readability(self, validator):
        # Deliberately complex academic language
        complex_stem = (
            "Given the aforementioned mathematical configuration, determine the "
            "quantitative relationship between the multiplicative decomposition and "
            "the subsequently derived positional notation representation thereof."
        )
        fk = flesch_kincaid_grade(complex_stem)
        assert fk > MAX_FK_GRADE, f"Expected FK > {MAX_FK_GRADE}, got {fk}"
        item = _valid_item(stem=complex_stem)
        errors = validator.validate_all(item)
        assert any(e.rule == "stem_readability" for e in errors)

    def test_fk_grade_calculation(self):
        # Simple sentence — should be low grade level
        simple = "The cat sat on the mat."
        fk = flesch_kincaid_grade(simple)
        assert fk < 4.0, f"Simple sentence should have FK < 4.0, got {fk}"


# ---------------------------------------------------------------------------
# Rule 4: No PII or harmful content
# ---------------------------------------------------------------------------

class TestNoPiiOrHarmful:

    def test_email_in_stem_fails(self, validator):
        item = _valid_item(stem="Send your answer to sipho@school.co.za for marking.")
        errors = validator.validate_all(item)
        assert any(e.rule == "no_pii" for e in errors)

    def test_sa_id_number_in_stem_fails(self, validator):
        item = _valid_item(stem="The learner with ID 9001015009087 answered first.")
        errors = validator.validate_all(item)
        assert any(e.rule == "no_pii" for e in errors)

    def test_harmful_keyword_in_stem_fails(self, validator):
        item = _valid_item(stem="Sipho found a bomb in the schoolyard.")
        errors = validator.validate_all(item)
        assert any(e.rule == "no_harmful" for e in errors)

    def test_brand_name_in_stem_fails(self, validator):
        item = _valid_item(stem="Sipho bought 3 Coca-Cola cans at R8 each. How much did he pay?")
        errors = validator.validate_all(item)
        assert any(e.rule == "no_brands" for e in errors)

    def test_clean_stem_passes(self, validator):
        item = _valid_item()
        errors = validator.validate_all(item)
        assert not any(e.rule in ("no_pii", "no_harmful", "no_brands") for e in errors)


# ---------------------------------------------------------------------------
# Rule 5: IRT parameters within valid bounds
# ---------------------------------------------------------------------------

class TestIRTParamsInBounds:

    @pytest.mark.parametrize("param,lo,hi", [
        ("difficulty_b",     -3.0,  3.0),
        ("discrimination_a",  0.5,  2.5),
        ("guessing_c",        0.0,  0.35),
    ])
    def test_boundary_values_pass(self, validator, param, lo, hi):
        for val in (lo, hi, (lo + hi) / 2):
            item = _valid_item(**{param: val})
            errors = validator.validate_all(item)
            assert not any(e.rule == "irt_params" for e in errors), (
                f"{param}={val} should be within bounds [{lo}, {hi}]"
            )

    @pytest.mark.parametrize("param,bad_value", [
        ("difficulty_b",      -4.0),
        ("difficulty_b",       4.0),
        ("discrimination_a",   0.1),
        ("discrimination_a",   3.0),
        ("guessing_c",        -0.1),
        ("guessing_c",         0.5),
    ])
    def test_out_of_bounds_value_fails(self, validator, param, bad_value):
        item = _valid_item(**{param: bad_value})
        errors = validator.validate_all(item)
        assert any(e.rule == "irt_params" for e in errors), (
            f"{param}={bad_value} should fail IRT bounds check"
        )

    def test_missing_irt_param_fails(self, validator):
        item = _valid_item()
        del item["difficulty_b"]
        errors = validator.validate_all(item)
        assert any(e.rule == "irt_params" for e in errors)

    def test_non_numeric_irt_param_fails(self, validator):
        item = _valid_item(difficulty_b="moderate")
        errors = validator.validate_all(item)
        assert any(e.rule == "irt_params" for e in errors)


# ---------------------------------------------------------------------------
# Rule 6: At least 4 MCQ options
# ---------------------------------------------------------------------------

class TestMinOptions:

    def test_four_options_passes(self, validator):
        item = _valid_item()  # has 4 options
        errors = validator.validate_all(item)
        assert not any(e.rule == "min_options" for e in errors)

    def test_three_options_fails(self, validator):
        item = _valid_item()
        item["options"] = item["options"][:3]
        errors = validator.validate_all(item)
        assert any(e.rule == "min_options" for e in errors)

    def test_option_with_empty_text_fails(self, validator):
        item = _valid_item()
        item["options"][0]["text"] = ""
        errors = validator.validate_all(item)
        assert any(e.rule == "min_options" for e in errors)

    def test_non_mcq_skips_options_check(self, validator):
        item = _valid_item(item_type="short_answer", options=[])
        errors = validator.validate_all(item)
        assert not any(e.rule == "min_options" for e in errors)


# ---------------------------------------------------------------------------
# Rule 7: explanation non-empty
# ---------------------------------------------------------------------------

class TestExplanationNonEmpty:

    def test_good_explanation_passes(self, validator):
        item = _valid_item()
        errors = validator.validate_all(item)
        assert not any(e.rule == "explanation" for e in errors)

    def test_empty_explanation_fails(self, validator):
        item = _valid_item(explanation="")
        errors = validator.validate_all(item)
        assert any(e.rule == "explanation" for e in errors)

    def test_too_short_explanation_fails(self, validator):
        item = _valid_item(explanation="B is correct.")
        errors = validator.validate_all(item)
        assert any(e.rule == "explanation" for e in errors)


# ---------------------------------------------------------------------------
# Rule 8: distractor_rationale covers all wrong options
# ---------------------------------------------------------------------------

class TestDistractorRationaleComplete:

    def test_complete_rationale_passes(self, validator):
        item = _valid_item()
        errors = validator.validate_all(item)
        assert not any(e.rule == "distractor_rationale" for e in errors)

    def test_missing_rationale_entry_fails(self, validator):
        item = _valid_item()
        del item["distractor_rationale"]["A"]   # answer_key is B; A is wrong → must have rationale
        errors = validator.validate_all(item)
        assert any(e.rule == "distractor_rationale" for e in errors)

    def test_empty_rationale_text_fails(self, validator):
        item = _valid_item()
        item["distractor_rationale"]["A"] = ""
        errors = validator.validate_all(item)
        assert any(e.rule == "distractor_rationale" for e in errors)

    def test_correct_option_not_required_in_rationale(self, validator):
        """The answer_key option (B) does not need a distractor rationale."""
        item = _valid_item()
        # Remove B from rationale (B is the correct answer)
        item["distractor_rationale"].pop("B", None)
        errors = validator.validate_all(item)
        assert not any(e.rule == "distractor_rationale" for e in errors)


# ---------------------------------------------------------------------------
# Safety and additional rules
# ---------------------------------------------------------------------------

class TestSafetyAndAdditionalRules:

    def test_safety_not_passed_fails(self, validator):
        item = _valid_item(safety_passed=False)
        errors = validator.validate_all(item)
        assert any(e.rule == "safety_passed" for e in errors)

    def test_safety_missing_fails(self, validator):
        item = _valid_item()
        del item["safety_passed"]
        errors = validator.validate_all(item)
        assert any(e.rule == "safety_passed" for e in errors)

    def test_invalid_item_type_fails(self, validator):
        item = _valid_item(item_type="essay")
        errors = validator.validate_all(item)
        assert any(e.rule == "item_type" for e in errors)

    def test_empty_misconception_tags_fails(self, validator):
        item = _valid_item(misconception_tags=[])
        errors = validator.validate_all(item)
        assert any(e.rule == "misconception_tags" for e in errors)

    def test_validate_raises_on_first_error(self, validator):
        """validate() (not validate_all) must raise on the first failure."""
        item = _valid_item(caps_ref="", answer_key="", explanation="")
        with pytest.raises(ValidationError):
            validator.validate(item)


# ---------------------------------------------------------------------------
# validate_all collects multiple errors
# ---------------------------------------------------------------------------

class TestValidateAllCollectsErrors:

    def test_multiple_errors_collected(self, validator):
        item = _valid_item(
            caps_ref="",
            answer_key="Z",
            explanation="",
            misconception_tags=[],
            safety_passed=False,
        )
        errors = validator.validate_all(item)
        assert len(errors) >= 4, (
            f"Expected ≥ 4 errors for badly formed item, got {len(errors)}: "
            + str([e.rule for e in errors])
        )

    def test_error_repr_includes_rule_and_detail(self, validator):
        item = _valid_item(caps_ref="bad.ref")
        errors = validator.validate_all(item)
        assert errors
        e = errors[0]
        assert e.rule in str(e)
        assert e.detail in str(e)
