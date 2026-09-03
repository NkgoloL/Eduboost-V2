from unittest.mock import AsyncMock, MagicMock
import json
import pytest

from app.services.content_generation.prompt_payloads import (
    DiagnosticGenerationRequest,
    GeneratedDiagnosticItem,
    GeneratedLesson,
    LessonGenerationRequest,
    SourceContextChunk,
)
from app.services.content_generation.providers.deterministic import DeterministicContentGenerationProvider
from app.services.content_generation.providers.llm import (
    LLMContentGenerationProvider,
    _assert_safe,
    _json_items,
    _source_context,
    _string_list,
)


@pytest.mark.asyncio
async def test_deterministic_provider_all_methods():
    prov = DeterministicContentGenerationProvider()
    assert prov.provider_name == "deterministic"

    chunk = SourceContextChunk(
        source_document_id="doc_1",
        source_chunk_id="chunk_1",
        text="Content chunk text.",
    )

    # 1. Diagnostic items
    diag_req = DiagnosticGenerationRequest(
        scope_id="scope_1",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        language="en",
        topic_title="Fractions",
        required_count=2,
        approved_count=0,
        missing_count=2,
        source_chunks=[chunk],
    )
    items = await prov.generate_diagnostic_items(diag_req)
    assert len(items) == 2
    assert isinstance(items[0], GeneratedDiagnosticItem)
    assert items[0].caps_ref == "4.M.1.1"

    # 2. Lessons
    lesson_req = LessonGenerationRequest(
        scope_id="scope_1",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        language="en",
        topic_title="Fractions",
        required_count=1,
        approved_count=0,
        missing_count=1,
        source_chunks=[chunk],
    )
    lessons = await prov.generate_lessons(lesson_req)
    assert len(lessons) == 1
    assert isinstance(lessons[0], GeneratedLesson)
    assert lessons[0].title.startswith("Fractions lesson 1")

    # 3. Assessment Blueprints
    blueprints = await prov.generate_assessment_blueprints({
        "caps_ref": "4.M.1.1",
        "scope_id": "scope_1",
        "grade": 4,
        "subject_code": "MATH",
        "missing_count": 2,
    })
    assert len(blueprints) == 2
    assert blueprints[0]["caps_ref"] == "4.M.1.1"

    # 4. Study Plan Templates
    templates = await prov.generate_study_plan_templates({
        "caps_ref": "4.M.1.1",
        "scope_id": "scope_1",
        "grade": 4,
        "subject_code": "MATH",
        "missing_count": 1,
    })
    assert len(templates) == 1
    assert templates[0]["estimated_minutes"] == 45


@pytest.mark.asyncio
async def test_llm_provider_generation_and_helpers():
    # Helper unit tests
    assert _string_list(None) == []
    assert _string_list("single") == ["single"]
    assert _string_list(["a", {"key": "val"}]) == ["a", '{"key": "val"}']

    # _json_items parsing
    assert _json_items('{"items": [{"id": 1}]}', key="items") == [{"id": 1}]
    assert _json_items('```json\n{"lessons": [{"title": "T"}]}\n```', key="lessons") == [{"title": "T"}]
    assert _json_items('[{"direct": "array"}]', key="anything") == [{"direct": "array"}]

    with pytest.raises(ValueError, match="must contain a JSON array"):
        _json_items('{"items": "not a list"}', key="items")

    with pytest.raises(ValueError, match="Every generated entry must be a JSON object"):
        _json_items('{"items": ["string_entry"]}', key="items")

    # _source_context
    valid_chunk = SourceContextChunk(
        source_document_id="doc1",
        source_chunk_id="chunk1",
        text="Sample lesson text context",
        document_status="approved",
    )
    ctx_str = _source_context([valid_chunk])
    assert "[chunk1]" in ctx_str

    unapproved_chunk = SourceContextChunk(
        source_document_id="doc2",
        source_chunk_id="chunk2",
        text="Unapproved text",
        document_status="pending",
    )
    with pytest.raises(ValueError, match="approved source context"):
        _source_context([unapproved_chunk])

    # LLM generation flow
    mock_router = AsyncMock()
    mock_router.generate.return_value = MagicMock(
        text=json.dumps({
            "items": [
                {
                    "question_text": "What is half of 10?",
                    "options": ["2", "5", "8", "10"],
                    "correct_answer": "5",
                    "explanation": "10 / 2 = 5",
                    "difficulty": "easy",
                    "cognitive_level": "understand",
                }
            ]
        })
    )

    mock_safety = MagicMock()
    mock_safety.check_text.return_value = MagicMock(passed=True, violations=[])

    prov = LLMContentGenerationProvider(router=mock_router, safety_filter=mock_safety)
    req = DiagnosticGenerationRequest(
        scope_id="scope_1",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        language="en",
        topic_title="Fractions",
        required_count=1,
        approved_count=0,
        missing_count=1,
        source_chunks=[valid_chunk],
    )
    items = await prov.generate_diagnostic_items(req)
    assert len(items) == 1
    assert items[0].question_text == "What is half of 10?"
    assert items[0].correct_answer == "5"

    # Lessons generation flow
    mock_router.generate.return_value = MagicMock(
        text=json.dumps({
            "lessons": [
                {
                    "title": "Introduction to Halves",
                    "summary": "Understanding half parts",
                    "learning_objectives": ["Identify halves"],
                    "teacher_notes": "Use diagrams",
                    "learner_activity": "Draw half shapes",
                    "worked_examples": ["Cut pizza in 2"],
                    "practice_questions": ["What is half?"],
                    "answer_key": ["One of two equal parts"],
                }
            ]
        })
    )
    lesson_req = LessonGenerationRequest(
        scope_id="scope_1",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        language="en",
        topic_title="Fractions",
        required_count=1,
        approved_count=0,
        missing_count=1,
        source_chunks=[valid_chunk],
    )
    lessons = await prov.generate_lessons(lesson_req)
    assert len(lessons) == 1
    assert lessons[0].title == "Introduction to Halves"

    # Diagnostic item with correct_answer_index fallback
    mock_router.generate.return_value = MagicMock(
        text=json.dumps({
            "items": [
                {
                    "question": "Index question?",
                    "options": ["Opt0", "Opt1"],
                    "correct_answer_index": 1,
                    "explanation": "Opt1 is right",
                }
            ]
        })
    )
    items_idx = await prov.generate_diagnostic_items(req)
    assert items_idx[0].correct_answer == "Opt1"

    # Blueprints and study plan templates raise NotImplementedError
    with pytest.raises(NotImplementedError, match="outside the Phase 1"):
        await prov.generate_assessment_blueprints({})

    with pytest.raises(NotImplementedError, match="outside the Phase 1"):
        await prov.generate_study_plan_templates({})

    # Empty items error
    mock_router.generate.return_value = MagicMock(text=json.dumps({"items": []}))
    with pytest.raises(ValueError, match="no diagnostic items"):
        await prov.generate_diagnostic_items(req)

    # Empty lessons error
    mock_router.generate.return_value = MagicMock(text=json.dumps({"lessons": []}))
    with pytest.raises(ValueError, match="no lessons"):
        await prov.generate_lessons(lesson_req)

    # Safety violation failure
    violation = MagicMock(description="PII leak")
    mock_safety.check_text.return_value = MagicMock(passed=False, violations=[violation])
    with pytest.raises(ValueError, match="safety gate"):
        _assert_safe(mock_safety, {"unsafe": "data"})

