"""Unit tests for Batch 426:
- app/modules/diagnostics/diagnostic_session_service.py
- app/modules/lessons/llm_gateway_v2.py
- app/modules/diagnostics/item_bank_service.py
- app/modules/diagnostics/item_validator.py
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

# ---------------------------------------------------------------------------
# Target 1: app/modules/diagnostics/diagnostic_session_service.py
# ---------------------------------------------------------------------------
from app.modules.diagnostics.diagnostic_session_service import (
    DiagnosticResponseResult,
    DiagnosticSessionService,
)
from app.modules.diagnostics.session_recovery_service import DiagnosticSessionSnapshot


class TestDiagnosticSessionService:
    @pytest.mark.asyncio
    async def test_start_session_with_and_without_repo(self):
        # With session repository
        mock_repo = AsyncMock()
        mock_row = MagicMock(id=uuid4())
        mock_repo.create_session.return_value = mock_row
        mock_recovery = AsyncMock()

        svc = DiagnosticSessionService(
            session_repository=mock_repo,
            recovery_service=mock_recovery,
        )
        snap = await svc.start_session("learner-1", "4.M.1.1", theta=0.5)
        assert snap.session_id == str(mock_row.id)
        assert snap.theta == 0.5
        mock_repo.create_session.assert_called_once_with("learner-1", theta=0.5, se=1.0, caps_ref="4.M.1.1")
        mock_recovery.write_session_snapshot.assert_called_once()

        # Without session repository
        svc_no_repo = DiagnosticSessionService(recovery_service=mock_recovery)
        snap2 = await svc_no_repo.start_session("learner-2", "4.M.1.2")
        assert snap2.session_id is not None
        assert snap2.caps_ref == "4.M.1.2"

    @pytest.mark.asyncio
    async def test_recover_session(self):
        mock_recovery = AsyncMock()
        svc = DiagnosticSessionService(recovery_service=mock_recovery)

        # Snap found
        snap = DiagnosticSessionSnapshot(session_id="s-1", learner_id="l-1", caps_ref="4.M.1.1")
        mock_recovery.read_session_snapshot.return_value = snap
        res = await svc.recover_session("s-1")
        assert res is snap
        assert res.session_state == "recovered"
        mock_recovery.write_session_snapshot.assert_called_once_with("s-1", snap)

        # Snap not found
        mock_recovery.read_session_snapshot.return_value = None
        assert await svc.recover_session("s-missing") is None

    @pytest.mark.asyncio
    async def test_get_next_item(self):
        mock_recovery = AsyncMock()
        svc = DiagnosticSessionService(recovery_service=mock_recovery)

        # Snap None
        mock_recovery.read_session_snapshot.return_value = None
        assert await svc.get_next_item("s-1") is None

        # Pool empty / selector returns None
        snap = DiagnosticSessionSnapshot(session_id="s-1", learner_id="l-1", caps_ref="4.M.1.1", served_item_ids=[])
        mock_recovery.read_session_snapshot.return_value = snap
        svc.selector = MagicMock()
        svc.selector.select_max_information_item.return_value = SimpleNamespace(item=None)

        assert await svc.get_next_item("s-1") is None
        assert snap.session_state == "completing"

        # Selector returns item
        item = SimpleNamespace(item_id="item-101")
        svc.selector.select_max_information_item.return_value = SimpleNamespace(item=item)

        res = await svc.get_next_item("s-1", items=[item])
        assert res is item
        assert snap.session_state == "awaiting_response"
        assert "item-101" in snap.served_item_ids

    @pytest.mark.asyncio
    async def test_submit_response(self):
        mock_recovery = AsyncMock()
        svc = DiagnosticSessionService(recovery_service=mock_recovery)

        # Snap None -> ValueError
        mock_recovery.read_session_snapshot.return_value = None
        with pytest.raises(ValueError, match="diagnostic session snapshot not found"):
            await svc.submit_response("s-1", SimpleNamespace(), correct=True)

        # Response submitted: incorrect response, adds gap_topics and misconception tags
        snap = DiagnosticSessionSnapshot(
            session_id="s-1",
            learner_id="l-1",
            caps_ref="4.M.1.1",
            responses=[],
            gap_topics=["4.M.1.1"],
            misconception_tags=["tag-1"],
        )
        mock_recovery.read_session_snapshot.return_value = snap
        item = SimpleNamespace(
            item_id="item-1",
            caps_ref="4.M.1.2",
            misconception_tags=["tag-1", "tag-2"],
            difficulty_b=0.0,
            discrimination_a=1.0,
            guessing_c=0.25,
        )

        with patch("app.modules.diagnostics.diagnostic_session_service.eap_update_3pl", return_value=(0.2, 0.4)):
            svc.terminator = MagicMock()
            svc.terminator.evaluate.return_value = SimpleNamespace(should_stop=False, reason=None)

            res = await svc.submit_response("s-1", item, correct=False, response="B")
            assert isinstance(res, DiagnosticResponseResult)
            assert res.theta == 0.2
            assert res.se_estimate == 0.4
            assert res.should_complete is False
            assert "4.M.1.2" in snap.gap_topics
            assert "tag-2" in snap.misconception_tags

    @pytest.mark.asyncio
    async def test_complete_session(self):
        mock_recovery = AsyncMock()
        mock_sessions = AsyncMock()
        mock_mastery = AsyncMock()
        svc = DiagnosticSessionService(
            session_repository=mock_sessions,
            mastery_repository=mock_mastery,
            recovery_service=mock_recovery,
        )

        # Snap None -> ValueError
        mock_recovery.read_session_snapshot.return_value = None
        with pytest.raises(ValueError, match="diagnostic session snapshot not found"):
            await svc.complete_session("s-1")

        # Success path: se_estimate=1.0 gives confidence = 1.0 - 0.5 = 0.5 <= MAX_CONFIDENCE_THRESHOLD (0.6)
        snap = DiagnosticSessionSnapshot(
            session_id="s-1",
            learner_id="l-1",
            caps_ref="4.M.1.1",
            theta=0.5,
            se_estimate=1.0,
            items_served=5,
            gap_topics=["4.M.1.1"],
            misconception_tags=["tag-1"],
        )
        mock_recovery.read_session_snapshot.return_value = snap

        res = await svc.complete_session("s-1")
        assert res["session_id"] == "s-1"
        assert res["theta"] == 0.5
        mock_sessions.update_session_state.assert_called_once()
        mock_mastery.upsert_topic_mastery.assert_called_once()
        mock_mastery.create_snapshot.assert_called_once()
        mock_recovery.invalidate_session_snapshot.assert_called_once_with("s-1")

    @pytest.mark.asyncio
    async def test_abandon_session(self):
        mock_sessions = AsyncMock()
        mock_recovery = AsyncMock()
        svc = DiagnosticSessionService(
            session_repository=mock_sessions,
            recovery_service=mock_recovery,
        )
        await svc.abandon_session("s-1")
        mock_sessions.update_session_state.assert_called_once_with("s-1", "abandoned")
        mock_recovery.invalidate_session_snapshot.assert_called_once_with("s-1")


# ---------------------------------------------------------------------------
# Target 2: app/modules/lessons/llm_gateway_v2.py
# ---------------------------------------------------------------------------
from app.modules.lessons.llm_gateway_v2 import (
    AnthropicAdapter,
    CircuitBreaker,
    CircuitState,
    GroqAdapter,
    LLMGatewayError,
    LLMGatewayV2,
)


class TestLLMGatewayV2:
    def test_circuit_breaker_transitions(self):
        cb = CircuitBreaker(name="test", failure_threshold=2, recovery_timeout_s=0.1)
        assert cb.state == CircuitState.CLOSED
        assert cb.is_available() is True

        # First failure
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED

        # Second failure -> OPENS
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.is_available() is False

        # Simulate timeout passage
        opened = cb._opened_at or 0.0
        with patch("time.monotonic", return_value=opened + 0.2):
            assert cb.state == CircuitState.HALF_OPEN
            assert cb.is_available() is True

            # Record failure in HALF_OPEN -> immediately OPENS
            cb.record_failure()
            assert cb._state == CircuitState.OPEN

        # Record success closes circuit
        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.is_available() is True

    @pytest.mark.asyncio
    async def test_groq_adapter(self):
        adapter = GroqAdapter(api_key="test-key", model="llama-3")
        mock_client = MagicMock()
        mock_choice = MagicMock(message=MagicMock(content="Groq output"))
        mock_resp = MagicMock(
            choices=[mock_choice],
            model="llama-3",
            usage=MagicMock(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

        with patch("groq.AsyncGroq", return_value=mock_client):
            res = await adapter.complete("Hi", system="Sys")
            assert res["content"] == "Groq output"
            assert res["provider"] == "groq"
            assert res["total_tokens"] == 30

        # Timeout error
        mock_client.chat.completions.create = AsyncMock(side_effect=asyncio.TimeoutError())
        with patch("groq.AsyncGroq", return_value=mock_client):
            with pytest.raises(LLMGatewayError, match="Groq call timed out"):
                await adapter.complete("Hi")

    @pytest.mark.asyncio
    async def test_anthropic_adapter(self):
        adapter = AnthropicAdapter(api_key="test-key", model="claude-3")
        mock_client = MagicMock()
        mock_block = MagicMock(text="Claude output")
        mock_resp = MagicMock(
            content=[mock_block],
            model="claude-3",
            usage=MagicMock(input_tokens=15, output_tokens=25),
        )
        mock_client.messages.create = AsyncMock(return_value=mock_resp)

        with patch("anthropic.AsyncAnthropic", return_value=mock_client):
            res = await adapter.complete("Hi", system="Sys")
            assert res["content"] == "Claude output"
            assert res["provider"] == "anthropic"
            assert res["used_fallback"] is True
            assert res["total_tokens"] == 40

        # Timeout error
        mock_client.messages.create = AsyncMock(side_effect=asyncio.TimeoutError())
        with patch("anthropic.AsyncAnthropic", return_value=mock_client):
            with pytest.raises(LLMGatewayError, match="Anthropic call timed out"):
                await adapter.complete("Hi")

    @pytest.mark.asyncio
    async def test_llm_gateway_v2_fallback_and_static(self):
        mock_groq = AsyncMock()
        mock_anth = AsyncMock()
        gateway = LLMGatewayV2(groq_adapter=mock_groq, anthropic_adapter=mock_anth)
        gateway.RETRY_BASE_DELAY_S = 0.001  # Instant retries for testing

        # 1. Primary succeeds
        mock_groq.complete.return_value = {
            "content": "Groq success",
            "provider": "groq",
            "model": "llama",
            "prompt_tokens": 5,
            "completion_tokens": 5,
            "total_tokens": 10,
        }
        res1 = await gateway.complete("Test", metadata={"user": "u1", "prompt": "ignored"})
        assert res1["content"] == "Groq success"
        assert len(gateway._token_log) == 1
        assert gateway._token_log[0]["meta"] == {"user": "u1"}

        # 2. Primary fails (all retries), fallback to Anthropic
        mock_groq.complete.side_effect = LLMGatewayError("Groq down")
        mock_anth.complete.return_value = {
            "content": "Anthropic success",
            "provider": "anthropic",
            "model": "claude",
            "prompt_tokens": 8,
            "completion_tokens": 8,
            "total_tokens": 16,
        }
        res2 = await gateway.complete("Test")
        assert res2["content"] == "Anthropic success"

        # 3. Both fail -> static fallback
        mock_anth.complete.side_effect = LLMGatewayError("Anthropic down")
        res3 = await gateway.complete("Test")
        assert res3["provider"] == "static"
        assert "temporarily unavailable" in res3["content"]

        # Check circuit breaker states
        states = gateway.circuit_breaker_states()
        assert "groq" in states
        assert "anthropic" in states

    def test_llm_gateway_v2_from_settings(self):
        settings_both = SimpleNamespace(GROQ_API_KEY="g-key", ANTHROPIC_API_KEY="a-key")
        gw = LLMGatewayV2.from_settings(settings_both)
        assert len(gw._providers) == 2

        settings_none = SimpleNamespace(GROQ_API_KEY=None, ANTHROPIC_API_KEY=None)
        gw_none = LLMGatewayV2.from_settings(settings_none)
        assert len(gw_none._providers) == 0


# ---------------------------------------------------------------------------
# Target 3: app/modules/diagnostics/item_bank_service.py
# ---------------------------------------------------------------------------
from app.models import DiagnosticItem
from app.modules.diagnostics.item_bank_service import (
    ItemBankService,
    _3pl_probability,
    _fisher_information,
    _irt_item_is_learner_eligible,
    fisher_information_3pl,
    select_maximum_information_item,
)


class TestItemBankService:
    def test_irt_item_is_learner_eligible(self):
        # uncalibrated, healthy, monitor
        assert _irt_item_is_learner_eligible(SimpleNamespace(irt_quality_state="uncalibrated")) is True
        assert _irt_item_is_learner_eligible(SimpleNamespace(irt_quality_state="healthy")) is True
        assert _irt_item_is_learner_eligible(SimpleNamespace(irt_quality_state="monitor")) is True
        assert _irt_item_is_learner_eligible(SimpleNamespace(irt_quality_state=None)) is True

        # flagged or other non-overridden
        assert _irt_item_is_learner_eligible(SimpleNamespace(irt_quality_state="flagged")) is False

        # overridden: no expires_at
        assert _irt_item_is_learner_eligible(SimpleNamespace(irt_quality_state="overridden", irt_manual_override_until=None)) is False

        # overridden: naive future datetime vs past
        now = datetime.now(timezone.utc)
        future_naive = datetime.now() + timedelta(days=2)
        past_naive = datetime.now() - timedelta(days=2)
        assert _irt_item_is_learner_eligible(SimpleNamespace(irt_quality_state="overridden", irt_manual_override_until=future_naive), now=now) is True
        assert _irt_item_is_learner_eligible(SimpleNamespace(irt_quality_state="overridden", irt_manual_override_until=past_naive), now=now) is False

    def test_fisher_information(self):
        info = _fisher_information(theta=0.0, a=1.0, b=0.0, c=0.25)
        assert info > 0.0

        # extreme probabilities
        assert _fisher_information(theta=100.0, a=10.0, b=0.0, c=0.0) == 0.0

    def test_select_maximum_information_item(self):
        with pytest.raises(ValueError, match="Candidate pool is empty"):
            select_maximum_information_item([], theta=0.0)

        i1 = SimpleNamespace(discrimination_a=1.0, difficulty_b=-1.0, guessing_c=0.2)
        i2 = SimpleNamespace(discrimination_a=2.0, difficulty_b=0.0, guessing_c=0.2)
        best = select_maximum_information_item([i1, i2], theta=0.0)
        assert best is i2

    @pytest.mark.asyncio
    async def test_item_bank_service_methods(self):
        mock_repo = AsyncMock()
        mock_repo.get_exposure_heatmap.return_value = [{"item_id": "1", "exposure": 5}]
        mock_repo.update_review_status.return_value = SimpleNamespace(id=uuid4())

        svc = ItemBankService(repo=mock_repo)
        assert await svc.get_exposure_heatmap("4.M.1.1") == [{"item_id": "1", "exposure": 5}]

        # mark_item_reviewed: reviewer_id required for approved
        with pytest.raises(ValueError, match="reviewer_id is required"):
            await svc.mark_item_reviewed(uuid4(), "approved", reviewer_id=None)

        # mark_item_reviewed with swapped argument types (lines 212-213)
        rev_id = uuid4()
        await svc.mark_item_reviewed(uuid4(), rev_id, reviewer_id="approved")
        mock_repo.update_review_status.assert_called_with(
            item_id=pytest.approx(mock_repo.update_review_status.call_args[1]["item_id"]),
            new_status="approved",
            reviewer_id=rev_id,
            quality_score=None,
        )

        # mark_item_reviewed success
        item_id = uuid4()
        reviewer_id = uuid4()
        res = await svc.mark_item_reviewed(item_id, "approved", reviewer_id=reviewer_id)
        assert res is not None

        # is_launch_ready & is_scope_ready
        with patch.object(svc, "get_coverage_summary", new_callable=AsyncMock) as mock_cov:
            mock_cov.return_value = {"4.M.1.1": {"coverage_ratio": 1.2}}
            with patch.object(svc.coverage_targets, "get_scope_caps_refs", return_value=["4.M.1.1"]):
                assert await svc.is_scope_ready("scope-1") is True
                assert await svc.is_launch_ready() is True

                mock_cov.return_value = {"4.M.1.1": {"coverage_ratio": 0.8}}
                assert await svc.is_scope_ready("scope-1") is False

        # from_session factory
        with patch("app.modules.diagnostics.item_bank_service.ItemBankRepository") as mock_repo_cls:
            inst = ItemBankService.from_session(AsyncMock())
            assert isinstance(inst, ItemBankService)


# ---------------------------------------------------------------------------
# Target 4: app/modules/diagnostics/item_validator.py
# ---------------------------------------------------------------------------
from app.modules.diagnostics.item_validator import (
    ItemValidator,
    ValidationError,
    _count_syllables,
    flesch_kincaid_grade,
)


class TestItemValidator:
    def test_count_syllables_and_flesch_kincaid(self):
        assert _count_syllables("") == 0
        assert _count_syllables("the") == 1
        assert _count_syllables("banana") == 3

        assert flesch_kincaid_grade("") == 0.0
        assert flesch_kincaid_grade("   ... ! ?  ") == 0.0
        assert isinstance(flesch_kincaid_grade("The cat sat on the mat."), float)

    def test_validator_topic_map_indexing(self):
        # Index with dict topics
        v_dict = ItemValidator(topic_map={"topics": {"4.M.1.1": {}, "4.M.1.2": {}}})
        assert "4.M.1.1" in v_dict._valid_caps_refs

        # Index with term list topics
        v_terms = ItemValidator(topic_map={
            "terms": [
                {
                    "topics": [
                        {"caps_ref": "4.M.1.1", "subtopics": [{"caps_ref": "4.M.1.1.1"}]}
                    ]
                }
            ]
        })
        assert "4.M.1.1" in v_terms._valid_caps_refs
        assert "4.M.1.1.1" in v_terms._valid_caps_refs

    def test_rule_grade_formatting_and_fk_enforcement(self):
        validator = ItemValidator()

        # Grade "R"
        item_r = {
            "stem": "Short stem.",
            "grade": "R",
        }
        validator._rule_stem_readability(item_r)

        # Grade numeric string " 4 "
        item_4 = {
            "stem": "Short stem.",
            "grade": " 4 ",
        }
        validator._rule_stem_readability(item_4)

        # Grade invalid string fallback
        item_inv = {
            "stem": "Short stem.",
            "grade": "invalid",
        }
        validator._rule_stem_readability(item_inv)

        # Grade > 6 (e.g. 8) skips FK check
        item_8 = {
            "stem": "Very complex sentence with incomprehensible multifaceted vocabulary for older learners.",
            "grade": 8,
        }
        validator._rule_stem_readability(item_8)

    def test_rule_min_options_empty_label_or_text(self):
        validator = ItemValidator()

        # Missing label
        item_no_label = {
            "item_type": "mcq",
            "options": [
                {"label": "", "text": "A"},
                {"label": "B", "text": "B"},
                {"label": "C", "text": "C"},
                {"label": "D", "text": "D"},
            ],
        }
        with pytest.raises(ValidationError, match="Option is missing a label"):
            validator._rule_min_options(item_no_label)

        # Empty text
        item_no_text = {
            "item_type": "mcq",
            "options": [
                {"label": "A", "text": "   "},
                {"label": "B", "text": "B"},
                {"label": "C", "text": "C"},
                {"label": "D", "text": "D"},
            ],
        }
        with pytest.raises(ValidationError, match="has an empty text field"):
            validator._rule_min_options(item_no_text)
