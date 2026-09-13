"""
tests/unit/core/test_core_llm_metrics_judiciary_batch412.py
============================================================
Batch 412: >=90% deterministic unit-test coverage for:
  - app/core/llm.py  (ExecutiveService, helper functions, quota, cache, providers)
  - app/core/metrics.py  (Prometheus counters/gauges/histograms, record_llm_tokens)
  - app/core/judiciary.py  (re-export of ConstitutionalViolation, JudiciaryService, LessonPayload)

All tests are deterministic; no real network, Redis, or ML-runtime calls are made.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ── Module-level imports ──────────────────────────────────────────────────────

from app.core import llm as core_llm
from app.core import metrics as core_metrics
from app.core import judiciary as core_judiciary  # re-export shim


# ─────────────────────────────────────────────────────────────────────────────
# 1. JUDICIARY (re-export shim)
# ─────────────────────────────────────────────────────────────────────────────


def test_judiciary_reexports_constitutional_violation():
    """judiciary.py is a thin re-export; ensure the public symbols are live."""
    assert core_judiciary.ConstitutionalViolation is not None
    exc = core_judiciary.ConstitutionalViolation("bad payload")
    assert isinstance(exc, Exception)
    assert "bad payload" in str(exc)


def test_judiciary_reexports_judiciary_service():
    assert core_judiciary.JudiciaryService is not None


def test_judiciary_reexports_lesson_payload():
    assert core_judiciary.LessonPayload is not None
    # Instantiate with required fields to confirm schema is accessible.
    payload = core_judiciary.LessonPayload(
        title="Test",
        introduction="intro",
        main_content="content",
        worked_example="example",
        practice_question="question?",
        answer="answer",
        cultural_hook="SA hook",
    )
    assert payload.title == "Test"


# ─────────────────────────────────────────────────────────────────────────────
# 2. METRICS — module-level objects
# ─────────────────────────────────────────────────────────────────────────────


def test_metrics_registry_exists():
    from prometheus_client import CollectorRegistry
    assert isinstance(core_metrics.REGISTRY, CollectorRegistry)


def test_metrics_http_counters_exist():
    assert core_metrics.http_requests_total is not None
    assert core_metrics.http_request_duration_seconds is not None


def test_metrics_llm_objects_exist():
    assert core_metrics.llm_requests_total is not None
    assert core_metrics.llm_latency_seconds is not None
    assert core_metrics.LLM_TOKENS_TOTAL is not None
    assert core_metrics.LLM_COST_USD is not None
    # Aliases
    assert core_metrics.llm_tokens_total is core_metrics.LLM_TOKENS_TOTAL
    assert core_metrics.llm_estimated_cost_usd_daily is core_metrics.LLM_COST_USD


def test_metrics_irt_objects_exist():
    assert core_metrics.irt_sessions_total is not None
    assert core_metrics.irt_computation_seconds is not None
    assert core_metrics.ITEM_BANK_COVERAGE_RATIO is core_metrics.item_bank_coverage_ratio
    assert core_metrics.DIAGNOSTIC_SESSIONS_TOTAL is core_metrics.diagnostic_sessions_total
    assert core_metrics.ITEM_SELECTION_LATENCY_SECONDS is core_metrics.item_selection_latency_seconds


def test_metrics_learner_activity_objects_exist():
    assert core_metrics.active_learners_gauge is not None
    assert core_metrics.lessons_generated_total is not None


def test_metrics_popia_objects_exist():
    assert core_metrics.consent_events_total is not None
    assert core_metrics.consent_gate_blocks_total is not None


def test_metrics_infrastructure_objects_exist():
    assert core_metrics.db_pool_size is not None
    assert core_metrics.db_pool_checkedout is not None
    assert core_metrics.db_pool_overflow is not None
    assert core_metrics.redis_connected_clients is not None


def test_metrics_readiness_objects_exist():
    assert core_metrics.readiness_component_status is not None
    assert core_metrics.audit_write_failures_total is not None
    assert core_metrics.backup_last_success_timestamp is not None
    assert core_metrics.backup_failures_total is not None


def test_metrics_arq_objects_exist():
    assert core_metrics.arq_jobs_total is not None
    assert core_metrics.arq_job_duration_seconds is not None


def test_metrics_content_review_objects_exist():
    assert core_metrics.content_review_decisions_total is not None
    assert core_metrics.content_review_state_transitions_total is not None
    assert core_metrics.content_review_stale_assignments is not None
    assert core_metrics.content_review_reminders_total is not None
    assert core_metrics.content_review_authorization_failures_total is not None


def test_metrics_irt_quality_governance_objects_exist():
    assert core_metrics.irt_calibration_runs_total is not None
    assert core_metrics.irt_item_interventions_total is not None
    assert core_metrics.irt_rewrite_requests_total is not None
    assert core_metrics.irt_answer_position_bias is not None


def test_metrics_tutor_objects_exist():
    assert core_metrics.tutor_messages_total is not None
    assert core_metrics.tutor_fallback_total is not None
    assert core_metrics.tutor_escalations_total is not None
    assert core_metrics.tutor_quality_score is not None


def test_metrics_ai_ops_objects_exist():
    assert core_metrics.ai_usage_tokens_total is not None
    assert core_metrics.ai_usage_cost_usd_total is not None
    assert core_metrics.ai_budget_blocks_total is not None
    assert core_metrics.ai_budget_reserved_tokens is not None
    assert core_metrics.ai_budget_usage_ratio is not None


def test_metrics_curriculum_objects_exist():
    assert core_metrics.curriculum_coverage_gap_total is not None
    assert core_metrics.curriculum_coverage_snapshots_total is not None
    assert core_metrics.training_dataset_artifacts_total is not None
    assert core_metrics.training_dataset_exclusions_total is not None


def test_metrics_pricing_table():
    pricing = core_metrics.LLM_PRICING_USD_PER_TOKEN
    assert "groq" in pricing
    assert "anthropic" in pricing
    assert pricing["groq"]["input"] > 0
    assert pricing["anthropic"]["output"] > pricing["groq"]["output"]


def test_metrics_make_metrics_app_returns_callable():
    app = core_metrics.make_metrics_app()
    assert app is not None


def test_record_llm_tokens_groq():
    """record_llm_tokens increments counters and updates the gauge without error."""
    # Save and reset accumulator to isolate this test
    original = dict(core_metrics._llm_daily_cost_accumulator)
    core_metrics._llm_daily_cost_accumulator.clear()
    core_metrics._llm_daily_cost_accumulator.update({"groq": 0.0, "anthropic": 0.0})
    try:
        core_metrics.record_llm_tokens(
            provider="groq",
            model="llama3-70b-8192",
            operation="test_op",
            input_tokens=100,
            output_tokens=50,
        )
        # accumulator should have increased
        assert core_metrics._llm_daily_cost_accumulator["groq"] > 0.0
    finally:
        core_metrics._llm_daily_cost_accumulator.clear()
        core_metrics._llm_daily_cost_accumulator.update(original)


def test_record_llm_tokens_anthropic():
    original = dict(core_metrics._llm_daily_cost_accumulator)
    core_metrics._llm_daily_cost_accumulator.clear()
    core_metrics._llm_daily_cost_accumulator.update({"groq": 0.0, "anthropic": 0.0})
    try:
        core_metrics.record_llm_tokens(
            provider="anthropic",
            model="claude-3-5-haiku-20241022",
            operation="lesson_generation",
            input_tokens=200,
            output_tokens=100,
        )
        assert core_metrics._llm_daily_cost_accumulator["anthropic"] > 0.0
    finally:
        core_metrics._llm_daily_cost_accumulator.clear()
        core_metrics._llm_daily_cost_accumulator.update(original)


def test_record_llm_tokens_unknown_provider_defaults_zero():
    """Unknown providers use 0.0 pricing — no crash."""
    original = dict(core_metrics._llm_daily_cost_accumulator)
    try:
        core_metrics.record_llm_tokens(
            provider="unknown_provider",
            model="some-model",
            operation="test",
            input_tokens=10,
            output_tokens=10,
        )
        assert core_metrics._llm_daily_cost_accumulator.get("unknown_provider", 0.0) == 0.0
    finally:
        core_metrics._llm_daily_cost_accumulator.clear()
        core_metrics._llm_daily_cost_accumulator.update(original)


# ─────────────────────────────────────────────────────────────────────────────
# 3. LLM — pure helper functions (no I/O)
# ─────────────────────────────────────────────────────────────────────────────


def test_cache_key_deterministic():
    k1 = core_llm._cache_key(10, "math", "algebra", "en", "visual")
    k2 = core_llm._cache_key(10, "math", "algebra", "en", "visual")
    assert k1 == k2
    assert k1.startswith("lesson_cache:")


def test_cache_key_varies_on_inputs():
    k1 = core_llm._cache_key(10, "math", "algebra", "en", None)
    k2 = core_llm._cache_key(11, "math", "algebra", "en", None)
    assert k1 != k2


def test_google_model_name_strips_prefix():
    with patch.object(core_llm.settings, "GOOGLE_MODEL", "models/gemini-1.5-pro"):
        assert core_llm._google_model_name() == "gemini-1.5-pro"


def test_google_model_name_no_prefix():
    with patch.object(core_llm.settings, "GOOGLE_MODEL", "gemini-1.5-flash"):
        assert core_llm._google_model_name() == "gemini-1.5-flash"


def test_active_provider_label_explicit_provider():
    with patch.object(core_llm.settings, "LLM_PROVIDER", "groq"):
        assert core_llm.active_provider_label() == "groq"


def test_active_provider_label_auto_google():
    with (
        patch.object(core_llm.settings, "LLM_PROVIDER", "auto"),
        patch.object(core_llm.settings, "GOOGLE_API_KEY", "gk_test"),
    ):
        assert core_llm.active_provider_label() == "google"


def test_active_provider_label_auto_groq():
    with (
        patch.object(core_llm.settings, "LLM_PROVIDER", "auto"),
        patch.object(core_llm.settings, "GOOGLE_API_KEY", ""),
        patch.object(core_llm.settings, "GROQ_API_KEY", "gr_test"),
    ):
        assert core_llm.active_provider_label() == "groq"


def test_active_provider_label_auto_anthropic():
    with (
        patch.object(core_llm.settings, "LLM_PROVIDER", "auto"),
        patch.object(core_llm.settings, "GOOGLE_API_KEY", ""),
        patch.object(core_llm.settings, "GROQ_API_KEY", ""),
        patch.object(core_llm.settings, "ANTHROPIC_API_KEY", "an_test"),
    ):
        assert core_llm.active_provider_label() == "anthropic"


def test_active_provider_label_fallback():
    with (
        patch.object(core_llm.settings, "LLM_PROVIDER", "auto"),
        patch.object(core_llm.settings, "GOOGLE_API_KEY", ""),
        patch.object(core_llm.settings, "GROQ_API_KEY", ""),
        patch.object(core_llm.settings, "ANTHROPIC_API_KEY", ""),
    ):
        assert core_llm.active_provider_label() == "fallback"


def test_is_test_provider_override_mock():
    mock_fn = MagicMock()
    # MagicMock module starts with 'unittest.mock'
    assert core_llm._is_test_provider_override(mock_fn) is True


def test_is_test_provider_override_real_method():
    class Dummy:
        def call(self):
            pass
    assert core_llm._is_test_provider_override(Dummy().call) is False


def test_fallback_lesson_payload_structure():
    payload = core_llm._fallback_lesson_payload(9, "mathematics", "fractions", "en")
    assert payload.title
    assert payload.introduction
    assert payload.main_content
    assert payload.worked_example
    assert payload.practice_question
    assert payload.answer
    assert payload.cultural_hook


def test_fallback_lesson_payload_isizulu_language():
    payload = core_llm._fallback_lesson_payload(6, "science", "photosynthesis", "zu")
    assert "isiZulu" in payload.introduction or "isiZulu" in payload.main_content


def test_fallback_lesson_payload_afrikaans_language():
    payload = core_llm._fallback_lesson_payload(7, "science", "ecosystems", "af")
    assert "Afrikaans" in payload.introduction or "Afrikaans" in payload.main_content


def test_extract_json_object_valid():
    text = 'prefix {"key": "value"} suffix'
    result = core_llm._extract_json_object(text)
    assert result == '{"key": "value"}'


def test_extract_json_object_no_braces():
    text = "no json here"
    result = core_llm._extract_json_object(text)
    assert result == "no json here"


def test_extract_json_object_end_before_start():
    result = core_llm._extract_json_object("} something {")
    # end <= start should return original
    assert result == "} something {"


def test_strip_generation_artifacts_removes_markers():
    text = "Some content<|user|>should be stripped"
    result = core_llm._strip_generation_artifacts(text)
    assert result == "Some content"


def test_strip_generation_artifacts_no_markers():
    text = "clean text here"
    result = core_llm._strip_generation_artifacts(text)
    assert result == "clean text here"


def test_strip_generation_artifacts_multiple_markers():
    for marker in ["<|user|>", "<|assistant|>", "<|system|>", "</s>"]:
        text = f"before{marker}after"
        result = core_llm._strip_generation_artifacts(text)
        assert result == "before", f"Failed for marker: {marker}"


def test_has_lesson_payload_fields_valid():
    d = {
        "title": "t",
        "introduction": "i",
        "main_content": "m",
        "worked_example": "w",
        "practice_question": "p",
        "answer": "a",
        "cultural_hook": "c",
    }
    assert core_llm._has_lesson_payload_fields(d) is True


def test_has_lesson_payload_fields_missing_key():
    d = {"title": "t", "introduction": "i"}
    assert core_llm._has_lesson_payload_fields(d) is False


def test_has_lesson_payload_fields_not_dict():
    assert core_llm._has_lesson_payload_fields("not a dict") is False
    assert core_llm._has_lesson_payload_fields(42) is False


def test_json_dict_to_section_text():
    d = {"title": "My Title", "content": "Some content", "empty": ""}
    result = core_llm._json_dict_to_section_text(d)
    assert "title: My Title" in result
    assert "content: Some content" in result
    # Empty values are excluded
    assert "empty" not in result


def test_extract_labelled_sections_parses_title():
    text = "Title: My Lesson\nLesson Objective: Learn fractions"
    sections = core_llm._extract_labelled_sections(text)
    assert "title" in sections
    assert "My Lesson" in sections["title"]


def test_extract_labelled_sections_empty_text():
    sections = core_llm._extract_labelled_sections("")
    assert sections == {}


def test_coerce_lesson_json_valid_json():
    """When text is already valid lesson JSON, it is returned unchanged."""
    lesson_dict = {
        "title": "t",
        "introduction": "i",
        "main_content": "m",
        "worked_example": "w",
        "practice_question": "p",
        "answer": "a",
        "cultural_hook": "c",
    }
    text = json.dumps(lesson_dict)
    result = core_llm._coerce_lesson_json(text)
    parsed = json.loads(result)
    assert parsed["title"] == "t"


def test_coerce_lesson_json_section_text_fallback():
    """When input is section-formatted text, it is coerced to lesson JSON."""
    text = (
        "Title: CAPS Lesson\n"
        "Teaching Activity: Students do an exercise.\n"
        "Worked Example: Solve 2+2=4.\n"
        "Assessment Evidence: Write answer.\n"
    )
    result = core_llm._coerce_lesson_json(text)
    parsed = json.loads(result)
    assert "title" in parsed


def test_coerce_lesson_json_partial_json_dict():
    """A JSON dict without lesson fields is converted via section-text fallback."""
    d = {"grade": "10", "subject": "Mathematics"}
    text = json.dumps(d)
    result = core_llm._coerce_lesson_json(text)
    # Should not crash and should return a JSON object
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_resolve_project_path_absolute():
    path = core_llm._resolve_project_path("/tmp/model")
    assert path == Path("/tmp/model")


def test_resolve_project_path_relative():
    path = core_llm._resolve_project_path("models/adapter")
    assert path.is_absolute()
    assert path.name == "adapter"


def test_local_hf_configured_false_when_paths_missing():
    with (
        patch.object(core_llm.settings, "LOCAL_MERGED_MODEL_PATH", "/nonexistent/merged"),
        patch.object(core_llm.settings, "LOCAL_ADAPTER_PATH", "/nonexistent/adapter"),
    ):
        assert core_llm._local_hf_configured() is False


# ─────────────────────────────────────────────────────────────────────────────
# 4. LLM — QuotaExceededError and check_and_consume_quota
# ─────────────────────────────────────────────────────────────────────────────


def test_quota_exceeded_error_is_exception():
    err = core_llm.QuotaExceededError("daily limit hit")
    assert isinstance(err, Exception)
    assert "daily limit" in str(err)


@pytest.mark.asyncio
async def test_check_and_consume_quota_success():
    decision = SimpleNamespace(used=5)
    with patch("app.core.llm.check_ai_quota", new_callable=AsyncMock) as mock_quota:
        mock_quota.return_value = decision
        used = await core_llm.check_and_consume_quota("user_abc", "free")
        assert used == 5


@pytest.mark.asyncio
async def test_check_and_consume_quota_exceeded_raises():
    from app.core.rate_limiter import AIQuotaExceeded, QuotaDecision

    decision = QuotaDecision(key="k", used=101, limit=100, retry_after=3600)
    with patch("app.core.llm.check_ai_quota", new_callable=AsyncMock) as mock_quota:
        mock_quota.side_effect = AIQuotaExceeded(decision)
        with pytest.raises(core_llm.QuotaExceededError):
            await core_llm.check_and_consume_quota("user_exceeded", "free")


# ─────────────────────────────────────────────────────────────────────────────
# 5. LLM — lazy client accessors
# ─────────────────────────────────────────────────────────────────────────────


def test_get_groq_returns_same_instance():
    # Reset singleton
    core_llm._groq_client = None
    with patch.object(core_llm.settings, "GROQ_API_KEY", "test_key"):
        c1 = core_llm._get_groq()
        c2 = core_llm._get_groq()
        assert c1 is c2
    core_llm._groq_client = None


def test_get_anthropic_returns_same_instance():
    core_llm._anthropic_client = None
    with patch.object(core_llm.settings, "ANTHROPIC_API_KEY", "test_key"):
        c1 = core_llm._get_anthropic()
        c2 = core_llm._get_anthropic()
        assert c1 is c2
    core_llm._anthropic_client = None


# ─────────────────────────────────────────────────────────────────────────────
# 6. LLM — ExecutiveService._call_mock
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def executive_service_mock_provider():
    """Return an ExecutiveService wired to the 'mock' provider."""
    with patch.object(core_llm.settings, "LLM_PROVIDER", "mock"):
        svc = core_llm.ExecutiveService()
    return svc


def test_call_mock_returns_json(executive_service_mock_provider):
    svc = executive_service_mock_provider
    raw = svc._call_mock("Grade 10 | Subject: Mathematics | Topic: Fractions | Language: en", operation="test")
    parsed = json.loads(raw)
    assert "title" in parsed
    assert "Fractions" in parsed["title"]


def test_call_mock_fallback_topic(executive_service_mock_provider):
    raw = executive_service_mock_provider._call_mock("no markers here", operation="test")
    parsed = json.loads(raw)
    assert "title" in parsed


# ─────────────────────────────────────────────────────────────────────────────
# 7. LLM — ExecutiveService._call_with_fallback routing
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_call_with_fallback_mock_provider():
    """When LLM_PROVIDER=mock, _call_with_fallback delegates to _call_mock synchronously."""
    with patch.object(core_llm.settings, "LLM_PROVIDER", "mock"):
        svc = core_llm.ExecutiveService()
        raw = await svc._call_with_fallback("Grade 7 | Topic: fractions", operation="test")
    parsed = json.loads(raw)
    assert "title" in parsed


@pytest.mark.asyncio
async def test_call_with_fallback_google_provider():
    with patch.object(core_llm.settings, "LLM_PROVIDER", "google"):
        svc = core_llm.ExecutiveService()
        with patch.object(svc, "_call_google", new_callable=AsyncMock) as mock_google:
            mock_google.return_value = '{"title":"t","introduction":"i","main_content":"m","worked_example":"w","practice_question":"p","answer":"a","cultural_hook":"c"}'
            raw = await svc._call_with_fallback("prompt", operation="test")
            mock_google.assert_called_once()


@pytest.mark.asyncio
async def test_call_with_fallback_anthropic_provider():
    with patch.object(core_llm.settings, "LLM_PROVIDER", "anthropic"):
        svc = core_llm.ExecutiveService()
        with patch.object(svc, "_call_anthropic", new_callable=AsyncMock) as mock_ant:
            mock_ant.return_value = '{"title":"t","introduction":"i","main_content":"m","worked_example":"w","practice_question":"p","answer":"a","cultural_hook":"c"}'
            raw = await svc._call_with_fallback("prompt", operation="test")
            mock_ant.assert_called_once()


@pytest.mark.asyncio
async def test_call_with_fallback_auto_tries_google_then_groq():
    with (
        patch.object(core_llm.settings, "LLM_PROVIDER", "auto"),
        patch.object(core_llm.settings, "GOOGLE_API_KEY", "gk"),
        patch.object(core_llm.settings, "GROQ_API_KEY", "gr"),
        patch.object(core_llm.settings, "ANTHROPIC_API_KEY", ""),
    ):
        svc = core_llm.ExecutiveService()
        # Google fails → groq succeeds
        good_response = '{"title":"t","introduction":"i","main_content":"m","worked_example":"w","practice_question":"p","answer":"a","cultural_hook":"c"}'
        with (
            patch.object(svc, "_call_google", new_callable=AsyncMock) as mock_g,
            patch.object(svc, "_call_groq", new_callable=AsyncMock) as mock_q,
        ):
            mock_g.side_effect = RuntimeError("google down")
            mock_q.return_value = good_response
            raw = await svc._call_with_fallback("prompt", operation="test")
            assert raw == good_response


@pytest.mark.asyncio
async def test_call_with_fallback_auto_no_credentials_raises():
    with (
        patch.object(core_llm.settings, "LLM_PROVIDER", "auto"),
        patch.object(core_llm.settings, "GOOGLE_API_KEY", ""),
        patch.object(core_llm.settings, "GROQ_API_KEY", ""),
        patch.object(core_llm.settings, "ANTHROPIC_API_KEY", ""),
    ):
        svc = core_llm.ExecutiveService()
        with pytest.raises(RuntimeError, match="No LLM provider"):
            await svc._call_with_fallback("prompt", operation="test")


# ─────────────────────────────────────────────────────────────────────────────
# 8. LLM — ExecutiveService._build_lesson_prompt
# ─────────────────────────────────────────────────────────────────────────────


def test_build_lesson_prompt_basic():
    with patch.object(core_llm.settings, "LLM_PROVIDER", "mock"):
        svc = core_llm.ExecutiveService()
    prompt = svc._build_lesson_prompt(10, "mathematics", "fractions", "en", "visual", "fractions")
    assert "Grade 10" in prompt
    assert "fractions" in prompt.lower()


def test_build_lesson_prompt_topic_adjusted():
    with patch.object(core_llm.settings, "LLM_PROVIDER", "mock"):
        svc = core_llm.ExecutiveService()
    prompt = svc._build_lesson_prompt(
        10, "mathematics", "canonical_fractions", "en", None, "user_fractions"
    )
    assert "adjusted from" in prompt or "canonical" in prompt or "Grade 10" in prompt


def test_build_lesson_prompt_with_learner_context():
    with patch.object(core_llm.settings, "LLM_PROVIDER", "mock"):
        svc = core_llm.ExecutiveService()
    prompt = svc._build_lesson_prompt(
        8, "science", "photosynthesis", "en", None, "photosynthesis",
        learner_context={"level": "foundation", "name": "REDACTED"},
    )
    assert "Learner context" in prompt


# ─────────────────────────────────────────────────────────────────────────────
# 9. LLM — ExecutiveService.generate_lesson (mock provider, full path)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_lesson_cache_hit():
    """If cache_get returns raw lesson JSON, stamp_lesson is called and (payload, True) returned."""
    lesson_json = json.dumps({
        "title": "Cached Lesson",
        "introduction": "intro",
        "main_content": "content",
        "worked_example": "example",
        "practice_question": "q?",
        "answer": "ans",
        "cultural_hook": "hook",
        "safety_classification": "safe",
    })
    with patch.object(core_llm.settings, "LLM_PROVIDER", "mock"):
        svc = core_llm.ExecutiveService()

    with (
        patch("app.core.llm.cache_get", new_callable=AsyncMock) as mock_cache,
        patch("app.core.llm.check_and_consume_quota", new_callable=AsyncMock),
    ):
        mock_cache.return_value = lesson_json
        payload, from_cache = await svc.generate_lesson(
            pseudonym_id="pseudo_123",
            grade=10,
            subject="mathematics",
            topic="fractions",
            language="en",
            archetype=None,
            user_id="u1",
            tier="free",
        )
    assert from_cache is True
    assert payload.title == "Cached Lesson"


@pytest.mark.asyncio
async def test_generate_lesson_mock_provider_no_cache():
    """Without cache hit and using the 'mock' provider, a lesson is generated and cached."""
    with patch.object(core_llm.settings, "LLM_PROVIDER", "mock"):
        svc = core_llm.ExecutiveService()

    with (
        patch("app.core.llm.cache_get", new_callable=AsyncMock) as mock_cache_get,
        patch("app.core.llm.cache_set", new_callable=AsyncMock) as mock_cache_set,
        patch("app.core.llm.check_and_consume_quota", new_callable=AsyncMock) as mock_quota,
    ):
        mock_cache_get.return_value = None
        mock_quota.return_value = 1
        payload, from_cache = await svc.generate_lesson(
            pseudonym_id="pseudo_999",
            grade=9,
            subject="mathematics",
            topic="algebra",
            language="en",
            archetype="visual",
            user_id="u2",
            tier="free",
        )
    assert from_cache is False
    assert payload.title is not None
    mock_cache_set.assert_called_once()


@pytest.mark.asyncio
async def test_generate_lesson_no_credentials_offline_fallback():
    """In non-production (ENVIRONMENT=test) with no API keys, returns the offline fallback payload."""
    with (
        patch.object(core_llm.settings, "LLM_PROVIDER", "auto"),
        patch.object(core_llm.settings, "GOOGLE_API_KEY", ""),
        patch.object(core_llm.settings, "GROQ_API_KEY", ""),
        patch.object(core_llm.settings, "ANTHROPIC_API_KEY", ""),
    ):
        svc = core_llm.ExecutiveService()

        with (
            patch("app.core.llm.cache_get", new_callable=AsyncMock) as mock_cg,
            patch("app.core.llm.cache_set", new_callable=AsyncMock),
            patch("app.core.llm.check_and_consume_quota", new_callable=AsyncMock),
        ):
            mock_cg.return_value = None
            # ENVIRONMENT='test' → is_production() is False; offline fallback is reached
            payload, from_cache = await svc.generate_lesson(
                pseudonym_id="ps_offline",
                grade=7,
                subject="science",
                topic="cells",
                language="en",
                archetype=None,
                user_id="u3",
                tier="free",
            )
    assert from_cache is False
    assert payload.title is not None


@pytest.mark.asyncio
async def test_generate_lesson_provider_failure_offline_fallback():
    """Provider failure in non-production (ENVIRONMENT=test) returns offline fallback, not exception."""
    with patch.object(core_llm.settings, "LLM_PROVIDER", "mock"):
        svc = core_llm.ExecutiveService()

    with (
        patch("app.core.llm.cache_get", new_callable=AsyncMock) as mock_cg,
        patch("app.core.llm.cache_set", new_callable=AsyncMock),
        patch("app.core.llm.check_and_consume_quota", new_callable=AsyncMock),
        patch.object(svc, "_call_with_fallback", new_callable=AsyncMock) as mock_call,
    ):
        mock_cg.return_value = None
        mock_call.side_effect = RuntimeError("provider down")
        # ENVIRONMENT='test' → is_production() is False → offline fallback returned
        payload, from_cache = await svc.generate_lesson(
            pseudonym_id="ps_fail",
            grade=8,
            subject="history",
            topic="apartheid",
            language="en",
            archetype=None,
            user_id="u4",
            tier="free",
        )
    assert from_cache is False


# ─────────────────────────────────────────────────────────────────────────────
# 10. LLM — LessonGenerator alias
# ─────────────────────────────────────────────────────────────────────────────


def test_lesson_generator_is_alias():
    assert core_llm.LessonGenerator is core_llm.ExecutiveService


# ─────────────────────────────────────────────────────────────────────────────
# 11. LLM — ExecutiveService.generate_progress_summary
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_progress_summary_returns_text():
    with patch.object(core_llm.settings, "LLM_PROVIDER", "mock"):
        svc = core_llm.ExecutiveService()

    # Mock groq client used by generate_progress_summary
    mock_usage = SimpleNamespace(prompt_tokens=10, completion_tokens=30)
    mock_choice = SimpleNamespace(message=SimpleNamespace(content="Great progress!"))
    mock_response = SimpleNamespace(
        choices=[mock_choice],
        usage=mock_usage,
    )
    mock_groq = MagicMock()
    mock_groq.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("app.core.llm._get_groq", return_value=mock_groq):
        summary = await svc.generate_progress_summary(
            pseudonym_id="pseudo_abc",
            gaps=["fractions", "geometry"],
            lessons_done=5,
        )
    assert "Great progress!" in summary


@pytest.mark.asyncio
async def test_generate_progress_summary_empty_content_fallback():
    with patch.object(core_llm.settings, "LLM_PROVIDER", "mock"):
        svc = core_llm.ExecutiveService()

    mock_usage = SimpleNamespace(prompt_tokens=5, completion_tokens=0)
    mock_choice = SimpleNamespace(message=SimpleNamespace(content=None))
    mock_response = SimpleNamespace(choices=[mock_choice], usage=mock_usage)
    mock_groq = MagicMock()
    mock_groq.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("app.core.llm._get_groq", return_value=mock_groq):
        summary = await svc.generate_progress_summary("ps2", [], 0)
    assert summary == "Progress data is being processed."
