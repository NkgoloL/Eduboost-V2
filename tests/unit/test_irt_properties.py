from hypothesis import given, strategies as st
import math
from app.modules.diagnostics.irt_engine import p_correct, fisher_information

@given(
    theta=st.floats(min_value=-5, max_value=5),
    a=st.floats(min_value=0.1, max_value=4),
    b=st.floats(min_value=-4, max_value=4)
)
def test_p_correct_bounds(theta, a, b):
    """P(correct) must always be between 0 and 1."""
    p = p_correct(theta, a, b)
    assert 0 <= p <= 1

@given(
    theta=st.floats(min_value=-5, max_value=5),
    a=st.floats(min_value=0.1, max_value=4),
    b=st.floats(min_value=-4, max_value=4)
)
def test_p_correct_monotonicity(theta, a, b):
    """P(correct) must be monotonic with respect to theta."""
    p1 = p_correct(theta, a, b)
    p2 = p_correct(theta + 0.1, a, b)
    assert p2 >= p1

@given(
    theta=st.floats(min_value=-5, max_value=5),
    a=st.floats(min_value=0.1, max_value=4),
    b=st.floats(min_value=-4, max_value=4)
)
def test_fisher_information_non_negative(theta, a, b):
    """Fisher information must be non-negative."""
    info = fisher_information(theta, a, b)
    assert info >= 0
