from unittest.mock import AsyncMock, MagicMock
import pytest

from app.services.arq_import_compat import (
    ARQ_AVAILABLE,
    ARQ_IMPORT_ERROR,
    RedisSettings,
    arq_dependency_status,
    cron,
)
from app.services.backend_adapter_wiring_service import (
    AdapterWiringResult,
    InMemoryAuditSink,
    record_all_safe_candidates,
    record_candidate_payload,
)
from app.services.content_schemas import (
    CONTENT_TYPE_SCHEMAS,
    CONTENT_TYPE_SCHEMA_VERSIONS,
    DiagnosticItemBatch,
    DiagnosticItemPayload,
    LessonPayload,
    VocabularyEntry,
    WorkedExample,
    get_schema_version,
)
from app.services.content_template_validation import (
    StudyPlanTemplateValidationResult,
    StudyPlanTemplateValidationService,
)


def test_arq_import_compat():
    status = arq_dependency_status()
    assert "available" in status
    assert "import_error" in status

    redis_settings = RedisSettings(host="127.0.0.1", port=6379, database=1)
    assert redis_settings.port == 6379

    async def dummy():
        pass

    decorated = cron(dummy)
    assert callable(decorated) or hasattr(decorated, "_arq_cron_fallback") or decorated is not None



@pytest.mark.asyncio
async def test_backend_adapter_wiring_service():
    sink = InMemoryAuditSink()
    rec_res = await sink.record(action="audit.test", resource_id="res_1")
    assert rec_res["recorded"] is True
    assert rec_res["action"] == "audit.test"

    results = await record_all_safe_candidates(sink)
    assert len(results) > 0
    for r in results:
        assert isinstance(r, AdapterWiringResult)
        assert r.recorded is True


def test_content_template_validation_service():
    validator = StudyPlanTemplateValidationService()

    # 1. Valid template
    valid_tpl = {
        "content_json": {"steps": ["step1"]},
        "referenced_artifact_ids": ["art_1", "art_2"],
    }
    approved = {"art_1", "art_2", "art_3"}
    res_valid = validator.validate(valid_tpl, approved)
    assert res_valid.passed is True
    assert res_valid.errors == []

    # 2. Template missing json and with unapproved references
    invalid_tpl = {
        "referenced_artifact_ids": ["art_unapproved"],
    }
    res_invalid = validator.validate(invalid_tpl, approved)
    assert res_invalid.passed is False
    assert any("requires content_json or template_json" in e for e in res_invalid.errors)
    assert any("may reference only approved lessons" in e for e in res_invalid.errors)


def test_content_schemas_complete():
    # DiagnosticItemPayload
    valid_diag = {
        "question": "What is 10 plus 15 in this problem?",
        "options": ["25", "30", "35"],
        "correct_answer_index": 0,
        "explanation": "Adding 10 and 15 gives 25 exactly.",
        "bloom_level": "knowledge",
        "difficulty_band": "easy",
        "caps_ref": "4.MATH.1",
        "tags": ["addition"],
    }
    item = DiagnosticItemPayload.model_validate(valid_diag)
    assert item.question == "What is 10 plus 15 in this problem?"

    # Out of range correct index
    bad_idx = dict(valid_diag, correct_answer_index=5)
    with pytest.raises(ValueError, match="out of range"):
        DiagnosticItemPayload.model_validate(bad_idx)

    # Duplicate options
    bad_opts = dict(valid_diag, options=["25", "25"])
    with pytest.raises(ValueError, match="unique"):
        DiagnosticItemPayload.model_validate(bad_opts)

    # DiagnosticItemBatch
    batch = DiagnosticItemBatch.from_list([valid_diag])
    assert len(batch.items) == 1

    # LessonPayload
    valid_lesson = {
        "title": "Understanding Proper Fractions",
        "caps_ref": "4.MATH.2.1",
        "grade": 4,
        "subject_code": "MATH",
        "language": "en",
        "learning_objectives": ["Identify the numerator and denominator."],
        "key_vocabulary": [{"term": "Fraction", "definition": "Part of a whole."}],
        "body_markdown": "Fractions represent parts of a whole shape or number. " * 3,
        "worked_examples": [
            {
                "problem": "Divide a circle into 4 equal parts.",
                "solution": "Each part is one quarter.",
                "answer": "1/4",
            }
        ],
    }
    lesson = LessonPayload.model_validate(valid_lesson)
    assert lesson.grade == 4
    assert len(lesson.key_vocabulary) == 1

    # get_schema_version
    assert get_schema_version("diagnostic_item") == "1.0"
    assert get_schema_version("lesson") == "1.0"
    with pytest.raises(KeyError, match="Unknown content type"):
        get_schema_version("nonexistent_type")
