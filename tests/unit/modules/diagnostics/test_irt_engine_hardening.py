from __future__ import annotations

from types import SimpleNamespace

import pytest
from hypothesis import given, settings, strategies as st

from app.modules.diagnostics.irt_engine import (
    IrtParameterError,
    clamp_theta,
    eap_update_3pl,
    fisher_information_3pl,
    p_correct_3pl,
    standard_error_from_information,
    validate_irt_parameters,
)
from app.modules.diagnostics.item_selection_service import ItemSelectionService
from app.modules.diagnostics.termination_service import TerminationService


def item(a=1.0, b=0.0, c=0.25, item_id="i1"):
    return SimpleNamespace(discrimination_a=a, difficulty_b=b, guessing_c=c, item_id=item_id, review_status="approved", safety_passed=True, exposure_count=0, max_exposure=50)


def test_invalid_parameters_raise():
    with pytest.raises(IrtParameterError):
        validate_irt_parameters(0, 0.1, 0, 0.25)
    with pytest.raises(IrtParameterError):
        validate_irt_parameters(0, 1, 4, 0.25)
    with pytest.raises(IrtParameterError):
        validate_irt_parameters(float("nan"), 1, 0, 0.25)


def test_theta_clamp_and_empty_eap():
    assert clamp_theta(9) == 4.0
    assert eap_update_3pl([]) == (0.0, 1.0)


def test_all_correct_and_all_incorrect_are_finite():
    items = [item(b=-1, item_id="a"), item(b=0, item_id="b"), item(b=1, item_id="c")]
    high, se_high = eap_update_3pl([(i, True) for i in items])
    low, se_low = eap_update_3pl([(i, False) for i in items])
    assert -4 <= low < high <= 4
    assert se_high > 0 and se_low > 0


def test_standard_error_decreases_with_information():
    few = [item(item_id="a")]
    many = [item(item_id=str(i), b=(i - 5) / 5) for i in range(10)]
    assert standard_error_from_information(0, many) < standard_error_from_information(0, few)


def test_mfis_selection_and_termination():
    easy = item(a=0.8, b=-2, item_id="easy")
    target = item(a=2.0, b=0, item_id="target")
    result = ItemSelectionService().select_max_information_item([easy, target], theta=0)
    assert result.item is target
    terminator = TerminationService()
    assert terminator.evaluate(standard_error=0.39, items_served=8, pool_size=10).reason == "se_converged"
    assert terminator.evaluate(standard_error=0.8, items_served=15, pool_size=10).reason == "max_items_served"
    assert terminator.evaluate(standard_error=0.8, items_served=8, pool_size=2).reason == "item_pool_exhausted"


@given(
    theta=st.floats(min_value=-4, max_value=4, allow_nan=False, allow_infinity=False),
    a=st.floats(min_value=0.5, max_value=2.5, allow_nan=False, allow_infinity=False),
    b=st.floats(min_value=-3, max_value=3, allow_nan=False, allow_infinity=False),
    c=st.floats(min_value=0, max_value=0.35, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_probability_property_bounds(theta, a, b, c):
    p = p_correct_3pl(theta, a, b, c)
    assert c <= p < 1.0
    assert fisher_information_3pl(theta, a, b, c) >= 0
