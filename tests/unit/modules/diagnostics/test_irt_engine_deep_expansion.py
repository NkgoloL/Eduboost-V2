"""Comprehensive unit tests for IRT 2PL mathematical functions and adaptive diagnostic engine."""
from __future__ import annotations

import math
import pytest

from app.modules.diagnostics.irt_engine import (
    p_correct,
    DiagnosticEngine,
)


class TestIRTEngineMaths:
    def test_p_correct_at_difficulty_inflection_point(self):
        # When theta == b, p_correct should equal exactly 0.5
        p = p_correct(theta=1.5, a=1.0, b=1.5)
        assert pytest.approx(p, abs=1e-6) == 0.5

    def test_p_correct_high_ability(self):
        # High ability learner vs low difficulty item
        p = p_correct(theta=3.0, a=1.5, b=-1.0)
        assert p > 0.99

    def test_p_correct_low_ability(self):
        # Low ability learner vs high difficulty item
        p = p_correct(theta=-3.0, a=1.5, b=1.0)
        assert p < 0.01

    def test_p_correct_overflow_clamping(self):
        # Extreme ability bounds are safely clamped without OverflowError
        p_high = p_correct(theta=100.0, a=2.0, b=0.0)
        assert p_high > 0.999

        p_low = p_correct(theta=-100.0, a=2.0, b=0.0)
        assert p_low < 0.001


class TestDiagnosticEngineInitialization:
    def test_engine_init(self):
        engine = DiagnosticEngine()
        assert engine is not None
