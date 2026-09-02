import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from app.core.config import settings
from app.core.judiciary import ConstitutionalViolation, LessonPayload
from app.core.llm import (
    ExecutiveService,
    LessonGenerator,
    QuotaExceededError,
    _get_groq,
    _get_anthropic,
    _resolve_project_path,
    _local_hf_configured,
    _get_local_hf_runtime,
    check_and_consume_quota,
    _cache_key,
    _google_model_name,
    active_provider_label,
    _is_test_provider_override,
    _fallback_lesson_payload,
    _extract_json_object,
    _coerce_lesson_json,
    _strip_generation_artifacts,
    _has_lesson_payload_fields,
    _json_dict_to_section_text,
    _extract_labelled_sections,
)
from app.core.rate_limiter import AIQuotaExceeded, QuotaDecision


@pytest.mark.asyncio
async def test_llm_clients_and_env_paths(monkeypatch, tmp_path):
    import app.core.llm as llm_mod

    llm_mod._groq_client = None
    llm_mod._anthropic_client = None
    llm_mod._local_hf_runtime = None

    monkeypatch.setattr(settings, "GROQ_API_KEY", "g-key-123")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "a-key-123")

    c1 = _get_groq()
    c2 = _get_groq()
    assert c1 is c2

    a1 = _get_anthropic()
    a2 = _get_anthropic()
    assert a1 is a2

    p = _resolve_project_path("some/relative/path")
    assert not p.is_absolute() or p.name == "path"

    abs_p = tmp_path / "models"
    resolved_abs = _resolve_project_path(str(abs_p))
    assert resolved_abs == abs_p

    monkeypatch.setattr(settings, "LOCAL_MERGED_MODEL_PATH", str(tmp_path / "nonexistent1"))
    monkeypatch.setattr(settings, "LOCAL_ADAPTER_PATH", str(tmp_path / "nonexistent2"))
    assert not _local_hf_configured()

    model_dir = tmp_path / "test_model"
    model_dir.mkdir()
    monkeypatch.setattr(settings, "LOCAL_MERGED_MODEL_PATH", str(model_dir))
    assert _local_hf_configured()


def test_get_local_hf_runtime_cached_and_branches(monkeypatch, tmp_path):
    import app.core.llm as llm_mod

    llm_mod._local_hf_runtime = {"cached": True}
    assert _get_local_hf_runtime() == {"cached": True}

    llm_mod._local_hf_runtime = None
    monkeypatch.setattr(settings, "LOCAL_MERGED_MODEL_PATH", str(tmp_path / "missing1"))
    monkeypatch.setattr(settings, "LOCAL_ADAPTER_PATH", str(tmp_path / "missing2"))

    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = False
    mock_torch.float32 = "float32"
    mock_torch.bfloat16 = "bfloat16"

    mock_auto_model = MagicMock()
    mock_auto_tok = MagicMock()
    mock_peft = MagicMock()

    with patch.dict("sys.modules", {
        "torch": mock_torch,
        "transformers": MagicMock(AutoModelForCausalLM=mock_auto_model, AutoTokenizer=mock_auto_tok),
        "peft": MagicMock(PeftModel=mock_peft),
    }):
        with pytest.raises(RuntimeError, match="No local model found"):
            _get_local_hf_runtime()

        # Merged model branch
        merged_dir = tmp_path / "merged"
        merged_dir.mkdir()
        (merged_dir / "config.json").write_text("{}")
        monkeypatch.setattr(settings, "LOCAL_MERGED_MODEL_PATH", str(merged_dir))

        dummy_tok = MagicMock()
        dummy_tok.pad_token = None
        dummy_tok.eos_token = "<eos>"
        mock_auto_tok.from_pretrained.return_value = dummy_tok

        runtime = _get_local_hf_runtime()
        assert runtime["model_source"] == str(merged_dir)
        assert dummy_tok.pad_token == "<eos>"

        # Adapter path branch
        llm_mod._local_hf_runtime = None
        monkeypatch.setattr(settings, "LOCAL_MERGED_MODEL_PATH", str(tmp_path / "no_merged"))
        adapter_dir = tmp_path / "adapter"
        adapter_dir.mkdir()
        monkeypatch.setattr(settings, "LOCAL_ADAPTER_PATH", str(adapter_dir))
        monkeypatch.setattr(settings, "LOCAL_BASE_MODEL_ID", "base-model-id")

        runtime2 = _get_local_hf_runtime()
        assert runtime2["model_source"] == "base-model-id"


@pytest.mark.asyncio
async def test_quota_and_cache_and_labels(monkeypatch):
    with patch("app.core.llm.check_ai_quota") as mock_quota:
        mock_quota.return_value = QuotaDecision(key="k1", used=10, limit=20, retry_after=0)
        used = await check_and_consume_quota("u1", "free")
        assert used == 10

        decision_exceeded = QuotaDecision(key="k1", used=21, limit=20, retry_after=3600)
        mock_quota.side_effect = AIQuotaExceeded(decision_exceeded)
        with pytest.raises(QuotaExceededError):
            await check_and_consume_quota("u1", "free")

    k = _cache_key(4, "Maths", "Fractions", "en", "visual")
    assert k.startswith("lesson_cache:")

    monkeypatch.setattr(settings, "GOOGLE_MODEL", "models/gemini-2.0-flash")
    assert _google_model_name() == "gemini-2.0-flash"

    monkeypatch.setattr(settings, "LLM_PROVIDER", "custom_provider")
    assert active_provider_label() == "custom_provider"

    monkeypatch.setattr(settings, "LLM_PROVIDER", "auto")
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "g-key")
    assert active_provider_label() == "google"

    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "gr-key")
    assert active_provider_label() == "groq"

    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "a-key")
    assert active_provider_label() == "anthropic"

    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    assert active_provider_label() == "fallback"


def test_helper_payload_and_parsing():
    # Languages
    for lang, name in [("zu", "isiZulu"), ("af", "Afrikaans"), ("xh", "isiXhosa"), ("en", "English")]:
        payload = _fallback_lesson_payload(4, "Mathematics", "Fractions", lang)
        assert isinstance(payload, LessonPayload)

    # JSON extraction
    assert _extract_json_object("no json here") == "no json here"
    assert _extract_json_object("prefix {'a': 1} suffix") == "{'a': 1}"

    # Artifact stripping
    assert _strip_generation_artifacts("hello world<|user|>some user text") == "hello world"
    assert _strip_generation_artifacts("clean text") == "clean text"

    # Schema checks
    full_dict = {
        "title": "T",
        "introduction": "I",
        "main_content": "M",
        "worked_example": "W",
        "practice_question": "P",
        "answer": "A",
        "cultural_hook": "C",
    }
    assert _has_lesson_payload_fields(full_dict)
    assert not _has_lesson_payload_fields({"title": "T"})
    assert not _has_lesson_payload_fields("not a dict")

    # Dict to section text
    sec_txt = _json_dict_to_section_text({"title": "T", "objective": "O", "empty": ""})
    assert "title: T" in sec_txt
    assert "objective: O" in sec_txt

    # Labelled sections extraction
    sample_text = (
        "Title: Grade 4 Fractions\n"
        "Grade: Grade 4 Intermediate Phase\n"
        "Subject: Mathematics\n"
        "CAPS alignment: Numbers, Operations and Relationships\n"
        "Lesson objective: Understand halves and quarters\n"
        "Teaching activity: Slice an apple into 4 pieces\n"
        "Worked example: 1/2 = 2/4\n"
        "Assessment evidence: Learners identify equivalent fractions\n"
        "Support and extension: Use pizza slices for visual support\n"
        "Practice question: What is 1/4 + 1/4?\n"
        "Answer: 2/4 or 1/2\n"
    )
    sections = _extract_labelled_sections(sample_text)
    assert sections["title"] == "Grade 4 Fractions"
    assert "Grade" in sections["grade"]
    assert sections["subject"] == "Mathematics"

    # Coerce lesson json
    json_candidate = json.dumps(full_dict)
    assert _coerce_lesson_json(json_candidate) == json_candidate
    assert _coerce_lesson_json(sample_text).startswith("{")


@pytest.mark.asyncio
async def test_executive_service_generate_lesson_flows(monkeypatch):
    svc = ExecutiveService()
    assert isinstance(svc, LessonGenerator)

    # 1. Cache hit
    sample_payload = _fallback_lesson_payload(4, "Mathematics", "Fractions", "en")
    with patch("app.core.llm.cache_get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = sample_payload.model_dump_json()
        payload, hit = await svc.generate_lesson(
            "p1", 4, "Mathematics", "Fractions", "en", "visual", "u1", "free"
        )
        assert hit is True
        assert payload.title == sample_payload.title

    # 2. Offline fallback when no credentials configured
    monkeypatch.setattr(settings, "LLM_PROVIDER", "auto")
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")

    with patch("app.core.llm.cache_get", new_callable=AsyncMock) as mock_get, \
         patch("app.core.llm.cache_set", new_callable=AsyncMock) as mock_set, \
         patch("app.core.llm.check_and_consume_quota", new_callable=AsyncMock):
        mock_get.return_value = None
        payload, hit = await svc.generate_lesson(
            "p1", 4, "Mathematics", "Fractions", "en", None, "u1", "free"
        )
        assert hit is False
        assert "Mathematics" in payload.title

    # 3. Provider execution and topic correction
    monkeypatch.setattr(settings, "LLM_PROVIDER", "mock")
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "dummy-active-key")
    with patch("app.core.llm.cache_get", new_callable=AsyncMock) as mock_get, \
         patch("app.core.llm.cache_set", new_callable=AsyncMock) as mock_set, \
         patch("app.core.llm.check_and_consume_quota", new_callable=AsyncMock):
        mock_get.return_value = None
        payload, hit = await svc.generate_lesson(
            "p1", 4, "Mathematics", "Fractions", "en", "story", "u1", "free",
            learner_context={"user_name": "Alice", "score": 85},
        )
        assert hit is False
        assert payload.title.startswith("EduBoost")

    # 4. Exception in _call_with_fallback fallback on non-prod
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    with patch.object(svc, "_call_with_fallback", side_effect=RuntimeError("Provider exploded")), \
         patch("app.core.llm.cache_get", new_callable=AsyncMock) as mock_get, \
         patch("app.core.llm.cache_set", new_callable=AsyncMock), \
         patch("app.core.llm.check_and_consume_quota", new_callable=AsyncMock):
        mock_get.return_value = None
        payload, hit = await svc.generate_lesson(
            "p1", 4, "Mathematics", "Fractions", "en", None, "u1", "free"
        )
        assert hit is False

    # 5. Exception in _call_with_fallback reraised in production
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    with patch.object(svc, "_call_with_fallback", side_effect=RuntimeError("Production outage")), \
         patch("app.core.llm.cache_get", new_callable=AsyncMock) as mock_get, \
         patch("app.core.llm.check_and_consume_quota", new_callable=AsyncMock):
        mock_get.return_value = None
        with pytest.raises(RuntimeError, match="Production outage"):
            await svc.generate_lesson(
                "p1", 4, "Mathematics", "Fractions", "en", None, "u1", "free"
            )


@pytest.mark.asyncio
async def test_executive_service_provider_dispatch(monkeypatch):
    svc = ExecutiveService()

    # Mock provider
    monkeypatch.setattr(settings, "LLM_PROVIDER", "mock")
    res = await svc._call_with_fallback("Topic: Fractions | Grade 4", operation="test")
    assert "EduBoost lesson" in res

    # Local HF provider
    monkeypatch.setattr(settings, "LLM_PROVIDER", "local_hf")
    with patch.object(svc, "_call_local_hf", new_callable=AsyncMock) as mock_local:
        mock_local.return_value = "{}"
        assert await svc._call_with_fallback("prompt", operation="test") == "{}"

    # Google provider
    monkeypatch.setattr(settings, "LLM_PROVIDER", "google")
    with patch.object(svc, "_call_google", new_callable=AsyncMock) as mock_g:
        mock_g.return_value = "{}"
        assert await svc._call_with_fallback("prompt", operation="test") == "{}"

    # Anthropic provider
    monkeypatch.setattr(settings, "LLM_PROVIDER", "anthropic")
    with patch.object(svc, "_call_anthropic", new_callable=AsyncMock) as mock_a:
        mock_a.return_value = "{}"
        assert await svc._call_with_fallback("prompt", operation="test") == "{}"

    # Auto cascading: Google -> Groq -> Anthropic
    monkeypatch.setattr(settings, "LLM_PROVIDER", "auto")
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "g-key")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "gr-key")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "a-key")

    with patch.object(svc, "_call_google", side_effect=RuntimeError("Google down")), \
         patch.object(svc, "_call_groq", side_effect=RuntimeError("Groq down")), \
         patch.object(svc, "_call_anthropic", new_callable=AsyncMock) as mock_a:
        mock_a.return_value = '{"provider": "anthropic"}'
        res = await svc._call_with_fallback("prompt", operation="test")
        assert res == '{"provider": "anthropic"}'

    # No credentials at all
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    with pytest.raises(RuntimeError, match="No LLM provider credentials configured"):
        await svc._call_with_fallback("prompt", operation="test")


@pytest.mark.asyncio
async def test_executive_service_groq_google_anthropic_calls(monkeypatch):
    svc = ExecutiveService()

    # _call_groq
    mock_groq_resp = MagicMock()
    mock_groq_resp.choices = [MagicMock(message=MagicMock(content='{"result": "groq"}'))]
    mock_groq_resp.usage = MagicMock(prompt_tokens=10, completion_tokens=20)
    with patch("app.core.llm._get_groq") as mock_get_g:
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_groq_resp
        mock_get_g.return_value = mock_client
        res = await svc._call_groq("prompt", operation="test")
        assert res == '{"result": "groq"}'

    # _call_google
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "test-gkey")
    monkeypatch.setattr(settings, "GOOGLE_MODEL", "models/gemini-2.0-flash")
    mock_post_resp = MagicMock()
    mock_post_resp.json.return_value = {
        "usageMetadata": {"promptTokenCount": 15, "candidatesTokenCount": 25},
        "candidates": [{"content": {"parts": [{"text": '{"result": "google"}'}]}}],
    }
    mock_post_resp.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_post_resp
        res = await svc._call_google("prompt", operation="test")
        assert res == '{"result": "google"}'

    # _call_anthropic tool use
    mock_tool_block = MagicMock()
    mock_tool_block.type = "tool_use"
    mock_tool_block.name = "submit_lesson"
    mock_tool_block.input = {"title": "Anthropic lesson"}
    mock_anthropic_resp = MagicMock(content=[mock_tool_block], usage=MagicMock(input_tokens=12, output_tokens=24))

    with patch("app.core.llm._get_anthropic") as mock_get_a:
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = mock_anthropic_resp
        mock_get_a.return_value = mock_client
        res = await svc._call_anthropic("prompt", operation="test")
        assert "Anthropic lesson" in res

    # generate_progress_summary
    with patch("app.core.llm._get_groq") as mock_get_g:
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Learner is doing great!"))],
            usage=MagicMock(prompt_tokens=5, completion_tokens=10),
        )
        mock_get_g.return_value = mock_client
        summary = await svc.generate_progress_summary("p1", ["fractions"], 5)
        assert "Learner is doing great!" in summary


def test_call_local_hf_sync(monkeypatch):
    svc = ExecutiveService()

    mock_torch = MagicMock()
    mock_torch.no_grad.return_value.__enter__ = MagicMock()
    mock_torch.no_grad.return_value.__exit__ = MagicMock()

    mock_tensor = MagicMock()
    mock_tensor.__getitem__.return_value = MagicMock(shape=[3])

    mock_model = MagicMock()
    mock_model.device = "cpu"
    mock_model.generate.return_value = [mock_tensor]

    mock_tokenizer = MagicMock()
    mock_inputs = {"input_ids": MagicMock(shape=[1, 2])}
    mock_tokenizer.return_value.to.return_value = mock_inputs
    mock_tokenizer.decode.return_value = 'Title: Fractions\nTeaching activity: Cut cake\n'

    with patch("app.core.llm._get_local_hf_runtime") as mock_runtime, \
         patch.dict("sys.modules", {"torch": mock_torch}):
        mock_runtime.return_value = {
            "model": mock_model,
            "tokenizer": mock_tokenizer,
            "model_source": "test-source",
        }
        res = svc._call_local_hf_sync("test prompt", operation="test")
        assert res.startswith("{")


@pytest.mark.asyncio
async def test_executive_service_retries_and_caps_validations(monkeypatch):
    svc = ExecutiveService()
    monkeypatch.setattr(settings, "LLM_PROVIDER", "mock")
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "dummy-key")

    valid_json = _fallback_lesson_payload(4, "Mathematics", "Fractions", "en").model_dump_json()

    # 1. Schema repair retry
    with patch("app.core.llm.cache_get", new_callable=AsyncMock) as mock_get, \
         patch("app.core.llm.cache_set", new_callable=AsyncMock), \
         patch("app.core.llm.check_and_consume_quota", new_callable=AsyncMock):
        mock_get.return_value = None
        svc._call_with_fallback = AsyncMock(side_effect=["not a valid json {", valid_json])
        payload, _ = await svc.generate_lesson("p1", 4, "Mathematics", "Fractions", "en", None, "u1", "free")
        assert payload.title is not None

    # 2. CAPS retry failure raises ConstitutionalViolation
    with patch("app.core.llm.cache_get", new_callable=AsyncMock) as mock_get, \
         patch("app.core.llm.cache_set", new_callable=AsyncMock), \
         patch("app.core.llm.check_and_consume_quota", new_callable=AsyncMock), \
         patch.object(svc._caps_validator, "validate_generated_content") as mock_val:
        mock_get.return_value = None
        mock_val.return_value = MagicMock(caps_aligned=False, reason="Out of CAPS scope")
        svc._call_with_fallback = AsyncMock(return_value=valid_json)
        with pytest.raises(ConstitutionalViolation, match="Out of CAPS scope"):
            await svc.generate_lesson("p1", 4, "Mathematics", "Fractions", "en", None, "u1", "free")


@pytest.mark.asyncio
async def test_executive_service_google_and_helper_edge_cases(monkeypatch):
    svc = ExecutiveService()

    # Google error: No API key
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "")
    with pytest.raises(RuntimeError, match="API key not configured"):
        await svc._call_google("prompt", operation="test")

    # Google error: No candidates
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "gkey")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"candidates": []}
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        with pytest.raises(RuntimeError, match="returned no candidates"):
            await svc._call_google("prompt", operation="test")

    # Google error: Empty text parts
    mock_resp.json.return_value = {"candidates": [{"content": {"parts": [{"text": ""}]}}]}
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        with pytest.raises(RuntimeError, match="returned an empty response"):
            await svc._call_google("prompt", operation="test")

    # Coerce json with dict not having lesson payload fields
    dict_json = json.dumps({"title": "A short title", "topic": "Fractions", "custom": "info"})
    coerced = _coerce_lesson_json(dict_json)
    assert "title" in coerced

