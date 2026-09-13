"""Comprehensive unit test suite for 100% coverage of app/modules/diagnostics/irt_engine.py."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.domain.models import IRTItem
from app.models import DiagnosticItem
from app.modules.diagnostics.irt_engine import (
    DiagnosticEngine,
    DiagnosticSessionState,
    IRTEngine,
    _eap_estimate_3pl,
    _normal_pdf,
    eap_update_3pl,
    fisher_information,
    p_correct,
    update_theta_mle,
)


class TestIRTEngineComprehensive:
    def test_fisher_information(self):
        info = fisher_information(theta=0.0, a=1.5, b=0.0)
        assert info > 0.0

    def test_update_theta_mle(self):
        item1 = IRTItem(
            id="q1",
            grade=4,
            subject="Maths",
            topic="Numbers",
            caps_reference="4.M.1.1",
            question_text="Stem 1",
            options={"A": "A", "B": "B"},
            correct_option="A",
            a_param=1.5,
            b_param=-0.5,
        )
        item2 = IRTItem(
            id="q2",
            grade=4,
            subject="Maths",
            topic="Numbers",
            caps_reference="4.M.1.1",
            question_text="Stem 2",
            options={"A": "A", "B": "B"},
            correct_option="B",
            a_param=1.2,
            b_param=0.5,
        )
        # Convergence
        theta = update_theta_mle(0.0, [(item1, True), (item2, False)], max_iter=20)
        assert -4.0 <= theta <= 4.0

        # Zero/near-zero hessian break
        zero_a_item = IRTItem(
            id="q0",
            grade=4,
            subject="Maths",
            topic="Numbers",
            caps_reference="4.M.1.1",
            question_text="Stem 0",
            options={"A": "A"},
            correct_option="A",
            a_param=0.0,
            b_param=0.0,
        )
        theta_zero = update_theta_mle(0.0, [(zero_a_item, True)], max_iter=5)
        assert theta_zero == 0.0

    def test_diagnostic_engine_full(self):
        engine = DiagnosticEngine()
        item1 = IRTItem(
            id="q1",
            grade=4,
            subject="Maths",
            topic="Numbers",
            caps_reference="4.M.1.1",
            question_text="Stem 1",
            options={"A": "A", "B": "B"},
            correct_option="A",
            a_param=1.5,
            b_param=-0.5,
        )
        item2 = IRTItem(
            id="q2",
            grade=4,
            subject="Maths",
            topic="Fractions",
            caps_reference="4.M.1.1",
            question_text="Stem 2",
            options={"A": "A", "B": "B"},
            correct_option="B",
            a_param=1.0,
            b_param=1.5,
        )
        items = [item1, item2]

        # compute_theta
        theta = engine.compute_theta(0.0, items, {"q1"})
        assert -4.0 <= theta <= 4.0

        # identify_gaps
        gaps = engine.identify_gaps(items, {"q1"})
        assert len(gaps) == 1
        assert gaps[0]["topic"] == "Fractions"

        # select_next_item
        next_item = engine.select_next_item(0.0, {"q1"}, items)
        assert next_item is item2

        next_item_none = engine.select_next_item(0.0, {"q1", "q2"}, items)
        assert next_item_none is None

        # should_stop
        assert engine.should_stop(20, 0.5) is True
        assert engine.should_stop(10, 0.25) is True
        assert engine.should_stop(10, 0.5) is False

        # map_grade_equivalent all branches
        assert engine.map_grade_equivalent(-2.0, 4) == 2  # shift -2
        assert engine.map_grade_equivalent(-1.0, 4) == 3  # shift -1
        assert engine.map_grade_equivalent(2.0, 4) == 6   # shift 2
        assert engine.map_grade_equivalent(1.0, 4) == 5   # shift 1
        assert engine.map_grade_equivalent(0.0, 4) == 4   # shift 0

        # run_gap_probe_cascade
        res = engine.run_gap_probe_cascade(4, items, {"q1"}, starting_theta=0.0)
        assert "theta" in res
        assert "standard_error" in res
        assert "grade_equivalent" in res
        assert "ranked_gaps" in res
        assert "knowledge_gap_topics" in res
        assert "stopped" in res
        assert "mean_difficulty" in res

    def test_normal_pdf_and_eap_estimate_3pl(self):
        val = _normal_pdf(0.0)
        assert val > 0.0

        d_item = DiagnosticItem(
            item_id=uuid4(),
            caps_ref="4.M.1.1",
            grade=4,
            subject="M",
            term=1,
            topic="Numbers",
            subtopic="Counting",
            skill="Counting",
            item_type="mcq",
            stem="What is 1+1?",
            answer_key="2",
            options=[{"label": "A", "text": "2"}],
            discrimination_a=1.2,
            difficulty_b=0.0,
            guessing_c=0.25,
        )
        theta_hat, se = _eap_estimate_3pl([(d_item, True)], prior_mean=0.0, prior_sd=1.0)
        assert -3.0 <= theta_hat <= 3.0
        assert se > 0.0

        # Empty weights / underflow fallback
        with patch("app.modules.diagnostics.irt_engine._normal_pdf", return_value=0.0):
            t_fallback, se_fallback = _eap_estimate_3pl([(d_item, True)], prior_mean=0.5, prior_sd=1.2)
            assert t_fallback == 0.5
            assert se_fallback == 1.2

    def test_diagnostic_session_state_redis(self):
        s_id = uuid4()
        l_id = uuid4()
        state = DiagnosticSessionState(
            session_id=s_id,
            learner_id=l_id,
            caps_ref="4.M.1.1",
            responses=[("item-1", True), ("item-2", False)],
            served_ids={uuid4()},
            theta=0.25,
            standard_error=0.35,
            started_at=datetime.now(timezone.utc),
            completed=False,
        )
        data = state.to_redis_dict()
        assert data["session_id"] == str(s_id)
        assert data["theta"] == 0.25

        restored = DiagnosticSessionState.from_redis_dict(data)
        assert restored.session_id == s_id
        assert restored.learner_id == l_id
        assert restored.caps_ref == "4.M.1.1"
        assert len(restored.responses) == 2
        assert len(restored.served_ids) == 1
        assert restored.theta == 0.25

    @pytest.mark.asyncio
    async def test_irt_engine_class(self):
        mock_bank_svc = AsyncMock()
        engine = IRTEngine(item_bank_service=mock_bank_svc)

        s_id = uuid4()
        l_id = uuid4()
        state = engine.new_session(s_id, l_id, "4.M.1.1", prior_theta=0.1)
        assert state.theta == 0.1
        assert state.session_id == s_id

        # next_item: max items reached
        state.responses = [("item", True)] * 15
        assert await engine.next_item(state) is None
        assert state.completed is True

        # next_item: min items + low SE reached
        state.completed = False
        state.responses = [("item", True)] * 8
        state.standard_error = 0.3
        assert await engine.next_item(state) is None
        assert state.completed is True

        # next_item: select_item_for_learner returns None
        state.completed = False
        state.responses = []
        mock_bank_svc.select_item_for_learner.return_value = None
        assert await engine.next_item(state) is None
        assert state.completed is True

        # next_item: item found
        mock_item = MagicMock(spec=DiagnosticItem, item_id=uuid4())
        mock_bank_svc.select_item_for_learner.return_value = mock_item
        state.completed = False
        item_found = await engine.next_item(state)
        assert item_found is mock_item

        # record_response
        mock_bank_svc.record_item_served = AsyncMock()
        # First response
        await engine.record_response(state, mock_item, is_correct=True, session_id=s_id)
        assert len(state.responses) == 1
        assert (str(mock_item.item_id), True) in state.responses
        mock_bank_svc.record_item_served.assert_called_once()

        # Second response (to test _ItemProxy in _build_proxy_responses)
        mock_item2 = MagicMock(spec=DiagnosticItem, item_id=uuid4(), discrimination_a=1.2, difficulty_b=0.5, guessing_c=0.2)
        await engine.record_response(state, mock_item2, is_correct=False)
        assert len(state.responses) == 2

        # session_result
        res = engine.session_result(state)
        assert res["session_id"] == str(s_id)
        assert res["items_attempted"] == 2
        assert res["items_correct"] == 1
        assert "accuracy" in res
        assert "below_grade_level" in res

    def test_irt_parameter_errors_and_helpers(self):
        from app.modules.diagnostics.irt_engine import (
            IrtParameterError,
            clamp_theta,
            standard_error_from_information,
            validate_irt_parameters,
        )

        # clamp_theta non-finite
        with pytest.raises(IrtParameterError, match="theta must be finite"):
            clamp_theta(float("nan"))

        # validate_irt_parameters non-finite
        with pytest.raises(IrtParameterError, match="must be finite"):
            validate_irt_parameters(theta=float("inf"), a=1.0, b=0.0)

        # invalid bounds
        with pytest.raises(IrtParameterError, match="guessing c"):
            validate_irt_parameters(theta=0.0, a=1.0, b=0.0, c=0.5)

        with pytest.raises(IrtParameterError, match="difficulty b"):
            validate_irt_parameters(theta=0.0, a=1.0, b=5.0, c=0.2)

        # standard_error_from_information: total <= 0
        se_empty = standard_error_from_information(theta=0.0, items=[])
        assert se_empty == 1.0

    def test_eap_update_3pl_wrapper(self):
        d_item = DiagnosticItem(
            item_id=uuid4(),
            caps_ref="4.M.1.1",
            grade=4,
            subject="M",
            term=1,
            topic="Numbers",
            subtopic="Counting",
            skill="Counting",
            item_type="mcq",
            stem="1+1",
            answer_key="2",
            options=[{"label": "A", "text": "2"}],
            discrimination_a=1.0,
            difficulty_b=0.0,
            guessing_c=0.2,
        )
        theta, se = eap_update_3pl([(d_item, True)], prior_mean=0.0)
        assert isinstance(theta, float)
        assert isinstance(se, float)
