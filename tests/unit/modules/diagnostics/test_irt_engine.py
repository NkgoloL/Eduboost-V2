"""
EduBoost SA — IRT Engine Unit Tests
Statistical correctness validation for ability estimation.
"""
from __future__ import annotations

import math
import pytest

from app.modules.diagnostics.irt_engine import IRTEngine, IRTItem, IRTSession


@pytest.fixture
def engine() -> IRTEngine:
    return IRTEngine()


@pytest.fixture
def item_bank() -> list[IRTItem]:
    return [
        IRTItem(item_id=f"item_{i}", difficulty=d, discrimination=1.0)
        for i, d in enumerate([-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0])
    ]


# ── probability_correct ────────────────────────────────────────────────────────

class TestProbabilityCorrect:
    def test_at_equal_ability_and_difficulty_probability_is_half(self, engine: IRTEngine) -> None:
        p = engine.probability_correct(ability=0.0, difficulty=0.0, discrimination=1.0)
        assert abs(p - 0.5) < 0.01

    def test_high_ability_gives_high_probability(self, engine: IRTEngine) -> None:
        p = engine.probability_correct(ability=3.0, difficulty=0.0)
        assert p > 0.95

    def test_low_ability_gives_low_probability(self, engine: IRTEngine) -> None:
        p = engine.probability_correct(ability=-3.0, difficulty=0.0)
        assert p < 0.05

    def test_probability_bounds(self, engine: IRTEngine) -> None:
        for ability in [-4.0, -2.0, 0.0, 2.0, 4.0]:
            p = engine.probability_correct(ability, 0.0)
            assert 0.0 < p < 1.0

    def test_higher_discrimination_steeper_curve(self, engine: IRTEngine) -> None:
        p_low = engine.probability_correct(1.0, 0.0, discrimination=0.5)
        p_high = engine.probability_correct(1.0, 0.0, discrimination=2.0)
        assert p_high > p_low


# ── estimate_ability ──────────────────────────────────────────────────────────

class TestEstimateAbility:
    def test_all_correct_returns_high_ability(self, engine: IRTEngine) -> None:
        responses = [True] * 8
        difficulties = [0.0] * 8
        ability = engine.estimate_ability(responses, difficulties)
        assert ability > 1.5

    def test_all_wrong_returns_low_ability(self, engine: IRTEngine) -> None:
        responses = [False] * 8
        difficulties = [0.0] * 8
        ability = engine.estimate_ability(responses, difficulties)
        assert ability < -1.5

    def test_empty_responses_returns_zero(self, engine: IRTEngine) -> None:
        assert engine.estimate_ability([], []) == 0.0

    def test_known_calibration_point(self, engine: IRTEngine) -> None:
        """At theta=0, a balanced response pattern on b=0 items → theta near 0."""
        responses = [True, False, True, False, True, False]
        difficulties = [0.0] * 6
        ability = engine.estimate_ability(responses, difficulties)
        assert abs(ability) < 0.5

    def test_hard_items_all_correct_gives_very_high_ability(self, engine: IRTEngine) -> None:
        responses = [True] * 5
        difficulties = [2.0, 2.5, 3.0, 2.0, 2.5]
        ability = engine.estimate_ability(responses, difficulties)
        assert ability > 2.5

    def test_easy_items_all_wrong_gives_very_low_ability(self, engine: IRTEngine) -> None:
        responses = [False] * 5
        difficulties = [-2.0, -2.5, -1.5, -2.0, -1.5]
        ability = engine.estimate_ability(responses, difficulties)
        assert ability < -2.0

    def test_ability_increases_with_more_correct_answers(self, engine: IRTEngine) -> None:
        difficulties = [0.0] * 10
        ability_low = engine.estimate_ability([True, False, False, False, False] * 2, difficulties)
        ability_high = engine.estimate_ability([True, True, True, True, False] * 2, difficulties)
        assert ability_high > ability_low


# ── standard_error ────────────────────────────────────────────────────────────

class TestStandardError:
    def test_more_items_reduces_standard_error(self, engine: IRTEngine) -> None:
        difficulties_5 = [0.0] * 5
        difficulties_20 = [0.0] * 20
        se_5 = engine.standard_error(0.0, difficulties_5)
        se_20 = engine.standard_error(0.0, difficulties_20)
        assert se_20 < se_5

    def test_standard_error_positive(self, engine: IRTEngine) -> None:
        se = engine.standard_error(0.0, [0.0, 0.5, -0.5])
        assert se > 0.0

    def test_empty_items_returns_large_error(self, engine: IRTEngine) -> None:
        se = engine.standard_error(0.0, [])
        assert se == 99.0

    def test_optimal_items_at_ability_reduce_se_fastest(self, engine: IRTEngine) -> None:
        """Items at ability = difficulty provide most information."""
        se_matched = engine.standard_error(0.0, [0.0, 0.0, 0.0])
        se_mismatched = engine.standard_error(0.0, [3.0, 3.0, 3.0])
        assert se_matched < se_mismatched


# ── select_next_item ──────────────────────────────────────────────────────────

class TestItemSelection:
    def test_selects_item_closest_to_ability(self, engine: IRTEngine, item_bank: list[IRTItem]) -> None:
        """At ability=0, the item with b≈0 should be selected."""
        selected = engine.select_next_item(0.0, item_bank, administered_ids=set())
        assert selected is not None
        assert abs(selected.difficulty - 0.0) < 0.6

    def test_skips_administered_items(self, engine: IRTEngine, item_bank: list[IRTItem]) -> None:
        administered = {item.item_id for item in item_bank[:-1]}
        selected = engine.select_next_item(0.0, item_bank, administered_ids=administered)
        assert selected is not None
        assert selected.item_id == item_bank[-1].item_id

    def test_returns_none_when_bank_exhausted(self, engine: IRTEngine, item_bank: list[IRTItem]) -> None:
        administered = {item.item_id for item in item_bank}
        selected = engine.select_next_item(0.0, item_bank, administered_ids=administered)
        assert selected is None


# ── session lifecycle ─────────────────────────────────────────────────────────

class TestIRTSession:
    def test_session_not_complete_with_few_items(self, engine: IRTEngine, item_bank: list[IRTItem]) -> None:
        session = IRTSession()
        for item in item_bank[:3]:
            session = engine.update_session(session, item, response=True)
        assert not session.is_complete

    def test_session_complete_at_max_items(self, engine: IRTEngine) -> None:
        session = IRTSession()
        for i in range(30):
            item = IRTItem(item_id=f"x{i}", difficulty=0.0, discrimination=1.0)
            session = engine.update_session(session, item, response=bool(i % 2))
        assert session.is_complete

    def test_ability_estimates_update_per_item(self, engine: IRTEngine, item_bank: list[IRTItem]) -> None:
        session = IRTSession()
        for item in item_bank[:4]:
            session = engine.update_session(session, item, response=True)
        assert len(session.ability_estimates) == 4

    def test_current_ability_reflects_latest_estimate(self, engine: IRTEngine, item_bank: list[IRTItem]) -> None:
        session = IRTSession()
        session = engine.update_session(session, item_bank[0], response=True)
        assert session.current_ability == session.ability_estimates[-1]


# ── interpret_ability ─────────────────────────────────────────────────────────

class TestAbilityInterpretation:
    @pytest.mark.parametrize("theta,expected_band", [
        (3.0, "advanced"),
        (1.0, "proficient"),
        (0.0, "developing"),
        (-1.0, "foundational"),
        (-3.0, "beginning"),
    ])
    def test_bands(self, theta: float, expected_band: str) -> None:
        result = IRTEngine.interpret_ability(theta)
        assert result["band"] == expected_band

    def test_all_bands_have_emoji(self) -> None:
        for theta in [3.0, 1.0, 0.0, -1.0, -3.0]:
            result = IRTEngine.interpret_ability(theta)
            assert "emoji" in result
            assert len(result["emoji"]) > 0
