import os
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.content_generation.provider_factory import (
    GenerationSettings,
    get_generation_settings,
    get_content_generation_provider,
)
from app.services.content_generation.providers.deterministic import (
    DeterministicContentGenerationProvider,
)
from app.services.content_generation.providers.llm import (
    LLMContentGenerationProvider,
    _source_context,
    _json_items,
    _string_list,
    _assert_safe,
)
from app.services.content_generation.source_context import (
    ContentGenerationSourceContextService,
    source_rows_for_chunks,
    _quality,
    SourceContextChunk,
)
from app.services.content_generation.prompt_payloads import (
    DiagnosticGenerationRequest,
    LessonGenerationRequest,
    SourceContextChunk,
)


def test_generation_settings_and_provider_factory():
    # 1. get_generation_settings default
    with patch.dict(os.environ, {}, clear=True):
        settings = get_generation_settings()
        assert settings.enabled is False
        assert settings.provider == "deterministic"
        assert settings.max_artifacts_per_task == 10
        assert settings.max_scope_run_artifacts == 250

    # 2. get_content_generation_provider deterministic in production raises RuntimeError
    with patch.dict(os.environ, {"APP_ENV": "production"}):
        with pytest.raises(RuntimeError, match="forbidden in production"):
            get_content_generation_provider(GenerationSettings(False, "deterministic", 10, 250))

    # deterministic in dev returns provider
    with patch.dict(os.environ, {"APP_ENV": "development"}):
        prov = get_content_generation_provider(GenerationSettings(False, "deterministic", 10, 250))
        assert isinstance(prov, DeterministicContentGenerationProvider)

    # 3. provider == llm disabled raises RuntimeError
    with pytest.raises(RuntimeError, match="must be true before using the LLM provider"):
        get_content_generation_provider(GenerationSettings(False, "llm", 10, 250))

    # llm enabled returns provider
    with patch("app.services.content_generation.providers.llm.build_provider_router"):
        llm_prov = get_content_generation_provider(GenerationSettings(True, "llm", 10, 250))
        assert isinstance(llm_prov, LLMContentGenerationProvider)

    # 4. provider == disabled raises RuntimeError
    with pytest.raises(RuntimeError, match="provider is disabled"):
        get_content_generation_provider(GenerationSettings(False, "disabled", 10, 250))

    # 5. Unsupported provider raises ValueError
    with pytest.raises(ValueError, match="Unsupported content generation provider"):
        get_content_generation_provider(GenerationSettings(False, "custom_unknown", 10, 250))


@pytest.mark.asyncio
async def test_deterministic_provider_all_methods():
    provider = DeterministicContentGenerationProvider()
    chunk = SourceContextChunk(
        source_document_id="doc-1",
        source_chunk_id="chk-1",
        text="Sample text",
        document_status="approved",
    )

    # Diagnostic items
    req_diag = DiagnosticGenerationRequest(
        scope_id="scope-1",
        caps_ref="4.M.1",
        grade=4,
        subject_code="MATHS",
        language="en",
        topic_title="Fractions",
        required_count=2,
        approved_count=0,
        missing_count=2,
        source_chunks=[chunk],
    )
    diag_items = await provider.generate_diagnostic_items(req_diag)
    assert len(diag_items) == 2
    assert diag_items[0].caps_ref == "4.M.1"

    # Lessons
    req_lesson = LessonGenerationRequest(
        scope_id="scope-1",
        caps_ref="4.M.1",
        grade=4,
        subject_code="MATHS",
        language="en",
        topic_title="Fractions",
        required_count=2,
        approved_count=0,
        missing_count=2,
        source_chunks=[chunk],
    )
    lessons = await provider.generate_lessons(req_lesson)
    assert len(lessons) == 2
    assert lessons[0].title.startswith("Fractions lesson")

    # Assessment blueprints
    blueprints = await provider.generate_assessment_blueprints({
        "missing_count": 2,
        "caps_ref": "4.M.1",
        "scope_id": "scope-1",
        "grade": 4,
        "subject_code": "MATHS",
    })
    assert len(blueprints) == 2
    assert blueprints[0]["assessment_type"] == "summative"

    # Study plan templates
    templates = await provider.generate_study_plan_templates({
        "missing_count": 2,
        "caps_ref": "4.M.1",
        "scope_id": "scope-1",
        "grade": 4,
        "subject_code": "MATHS",
    })
    assert len(templates) == 2
    assert templates[0]["estimated_minutes"] == 45


@pytest.mark.asyncio
async def test_llm_provider_methods_and_helpers():
    mock_router = MagicMock()
    mock_safety = MagicMock()
    mock_safety.check_text.return_value = MagicMock(passed=True, violations=[])

    provider = LLMContentGenerationProvider(router=mock_router, safety_filter=mock_safety)

    chunk = SourceContextChunk(
        source_document_id="doc-1",
        source_chunk_id="chk-1",
        text="Approved mathematics reference content",
        document_status="approved",
    )

    # 1. generate_diagnostic_items with correct_answer_index
    llm_diag_json = json.dumps({
        "items": [
            {
                "question_text": "What is 1/2 + 1/2?",
                "options": ["1", "2", "0", "1/4"],
                "correct_answer_index": 0,
                "explanation": "Half plus half equals one.",
                "difficulty": "easy",
                "cognitive_level": "apply",
            }
        ]
    })
    mock_router.generate = AsyncMock(return_value=MagicMock(text=f"```json\n{llm_diag_json}\n```"))

    req_diag = DiagnosticGenerationRequest(
        scope_id="scope-1",
        caps_ref="4.M.1",
        grade=4,
        subject_code="MATHS",
        language="en",
        topic_title="Fractions",
        required_count=1,
        approved_count=0,
        missing_count=1,
        source_chunks=[chunk],
    )
    items = await provider.generate_diagnostic_items(req_diag)
    assert len(items) == 1
    assert items[0].correct_answer == "1"

    # 2. generate_lessons
    llm_lesson_json = json.dumps({
        "lessons": [
            {
                "title": "Adding Halves",
                "summary": "Learn to add simple fractions.",
                "learning_objectives": ["Add halves", {"note": "use shapes"}],
                "teacher_notes": "Use physical fraction discs.",
                "learner_activity": "Draw half circles and combine them.",
                "worked_examples": ["1/2 + 1/2 = 1"],
                "practice_questions": ["1/2 + 1/2 = ?"],
                "answer_key": ["1"],
            }
        ]
    })
    mock_router.generate = AsyncMock(return_value=MagicMock(text=llm_lesson_json))

    req_lesson = LessonGenerationRequest(
        scope_id="scope-1",
        caps_ref="4.M.1",
        grade=4,
        subject_code="MATHS",
        language="en",
        topic_title="Fractions",
        required_count=1,
        approved_count=0,
        missing_count=1,
        source_chunks=[chunk],
    )

    lessons = await provider.generate_lessons(req_lesson)
    assert len(lessons) == 1
    assert lessons[0].title == "Adding Halves"

    # 3. Not implemented methods
    with pytest.raises(NotImplementedError):
        await provider.generate_assessment_blueprints({})
    with pytest.raises(NotImplementedError):
        await provider.generate_study_plan_templates({})

    # 4. _source_context errors
    with pytest.raises(ValueError, match="requires approved source context"):
        _source_context([MagicMock(document_status="pending")])

    # 5. _json_items errors and alternative keys
    with pytest.raises(ValueError, match="must contain a JSON array"):
        _json_items(json.dumps({"items": "not a list"}), key="items")

    with pytest.raises(ValueError, match="Every generated entry must be a JSON object"):
        _json_items(json.dumps({"items": ["not_a_dict"]}), key="items")

    # List payload directly
    assert _json_items(json.dumps([{"q": "1"}]), key="items") == [{"q": "1"}]

    # diagnostic_items key fallback
    assert _json_items(json.dumps({"diagnostic_items": [{"q": "2"}]}), key="items") == [{"q": "2"}]

    # Empty items / lessons raises ValueError
    mock_router.generate = AsyncMock(return_value=MagicMock(text=json.dumps({"items": []})))
    with pytest.raises(ValueError, match="returned no diagnostic items"):
        await provider.generate_diagnostic_items(req_diag)

    mock_router.generate = AsyncMock(return_value=MagicMock(text=json.dumps({"lessons": []})))
    with pytest.raises(ValueError, match="returned no lessons"):
        await provider.generate_lessons(req_lesson)

    # 6. _string_list variations
    assert _string_list(None) == []
    assert _string_list("single_string") == ["single_string"]
    assert _string_list(["item1", {"k": "v"}]) == ["item1", '{"k": "v"}']

    # 7. _assert_safe failure
    mock_unsafe = MagicMock()
    mock_unsafe.check_text.return_value = MagicMock(
        passed=False,
        violations=[MagicMock(description="Toxic speech detected")]
    )
    with pytest.raises(ValueError, match="failed the safety gate"):
        _assert_safe(mock_unsafe, {"text": "harmful content"})


@pytest.mark.asyncio
async def test_source_context_service_and_helpers():
    from app.services.content_generation.source_context import (
        ContentGenerationSourceContextService as LegacyService,
    )
    from app.services.semantic_retrieval.generation_context import (
        LegacyContentGenerationSourceContextService,
    )

    service = LegacyService(min_quality_score=0.6)

    # 1. validate_source_rows error cases
    bad_sources = [
        # Unapproved status
        MagicMock(source_document_id="d1", source_metadata={"document_status": "draft"}),
        # Ineligible status
        MagicMock(source_document_id="d2", source_metadata={"document_status": "rejected"}),
        # Incompatible license
        MagicMock(source_document_id="d3", source_metadata={"document_status": "approved", "license_status": "all_rights_reserved"}),
        # Quality below threshold
        MagicMock(source_document_id="d4", source_quality_score=0.4, source_metadata={"document_status": "approved"}),
        # Missing source_chunk_id
        MagicMock(source_document_id="d5", source_quality_score=0.8, source_chunk_id=None, source_metadata={"document_status": "approved"}),
    ]
    res_bad = service.validate_source_rows(bad_sources, caps_ref="4.M.1")
    assert res_bad.passed is False
    assert len(res_bad.errors) >= 5

    # 2. validate_source_rows success case
    good_source = MagicMock(
        source_document_id="d-good",
        source_chunk_id="chk-good",
        source_title="Approved CAPS Guide",
        source_quality_score=0.9,
        source_hash="hash-good",
        curriculum_mapping_id="map-1",
        license_status="government_open",
        source_metadata={"document_status": "approved", "chunk_text": "Fractions foundation"},
    )
    res_good = service.validate_source_rows([good_source], caps_ref="4.M.1")
    assert res_good.passed is True
    assert len(res_good.chunks) == 1

    # 3. source_rows_for_chunks
    rows = source_rows_for_chunks(res_good.chunks, caps_ref="4.M.1", grade=4, subject_code="MATHS", language="en")
    assert len(rows) == 1
    assert rows[0]["source_document_id"] == "d-good"
    assert rows[0]["citation_text"] == "Fractions foundation"

    # 4. _quality helper fallback
    mock_src = MagicMock(spec=[])  # no source_quality_score attribute
    assert _quality(mock_src, {"source_quality_score": 0.85}) == 0.85
    assert _quality(mock_src, {"chunk_quality_score": 0.75}) == 0.75
    assert _quality(mock_src, {}) is None

    # 5. LegacyContentGenerationSourceContextService.build_context
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [good_source]
    mock_session.execute = AsyncMock(return_value=mock_result)

    ctx_res = await LegacyContentGenerationSourceContextService.build_context(
        service,
        mock_session,
        scope_id="scope-1",
        caps_ref="4.M.1",
        requested_chunk_ids=["chk-good"],
    )
    assert ctx_res.passed is True
    assert len(ctx_res.chunks) == 1

    # Missing requested chunk id
    ctx_res_missing = await LegacyContentGenerationSourceContextService.build_context(
        service,
        mock_session,
        scope_id="scope-1",
        caps_ref="4.M.1",
        requested_chunk_ids=["chk-missing"],
    )
    assert ctx_res_missing.passed is False
    assert "Requested source chunks were not found" in ctx_res_missing.errors[0]

