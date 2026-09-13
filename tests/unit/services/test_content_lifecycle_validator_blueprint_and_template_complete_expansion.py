"""Comprehensive unit tests covering content artifact lifecycle, validator, blueprint validation, and template validation."""
import json
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.models.content_factory import ContentArtifactStatus, ContentGenerationArtifact
from app.services.content_artifact_lifecycle import (
    ArtifactStatusTransition,
    ContentArtifactLifecycleService,
    _value,
)
from app.services.content_blueprint_validation import (
    AssessmentBlueprintValidationService,
    BlueprintValidationResult,
)
from app.services.content_template_validation import (
    StudyPlanTemplateValidationResult,
    StudyPlanTemplateValidationService,
)
from app.services.content_validator import (
    ContentValidator,
    ValidationResult,
)


# ============================================================================
# AssessmentBlueprintValidationService & StudyPlanTemplateValidationService
# ============================================================================
def test_blueprint_and_template_validation():
    bp_service = AssessmentBlueprintValidationService()

    # Blueprint without content_json or blueprint_json and missing referenced diagnostic items
    bp_invalid = {"referenced_artifact_ids": ["art_1", "art_2"]}
    res_bp_fail = bp_service.validate(bp_invalid, approved_diagnostic_item_ids={"art_1"})
    assert isinstance(res_bp_fail, BlueprintValidationResult)
    assert res_bp_fail.passed is False
    assert any("Blueprint requires content_json or blueprint_json" in e for e in res_bp_fail.errors)
    assert any("Blueprint may reference only approved diagnostic items" in e for e in res_bp_fail.errors)

    # Clean blueprint
    bp_valid = {"blueprint_json": {"sections": []}, "referenced_artifact_ids": ["art_1"]}
    res_bp_ok = bp_service.validate(bp_valid, approved_diagnostic_item_ids={"art_1", "art_2"})
    assert res_bp_ok.passed is True
    assert not res_bp_ok.errors

    tmpl_service = StudyPlanTemplateValidationService()

    # Template without content_json or template_json and missing referenced lessons
    tmpl_invalid = {"referenced_artifact_ids": ["lesson_1", "lesson_2"]}
    res_tmpl_fail = tmpl_service.validate(tmpl_invalid, approved_reference_ids={"lesson_1"})
    assert isinstance(res_tmpl_fail, StudyPlanTemplateValidationResult)
    assert res_tmpl_fail.passed is False
    assert any("Study plan template requires content_json or template_json" in e for e in res_tmpl_fail.errors)
    assert any("Study templates may reference only approved lessons" in e for e in res_tmpl_fail.errors)

    # Clean template
    tmpl_valid = {"template_json": {"weeks": []}, "referenced_artifact_ids": ["lesson_1"]}
    res_tmpl_ok = tmpl_service.validate(tmpl_valid, approved_reference_ids={"lesson_1"})
    assert res_tmpl_ok.passed is True
    assert not res_tmpl_ok.errors


# ============================================================================
# ContentValidator Tests
# ============================================================================
def test_content_validator():
    validator = ContentValidator()

    # 1. Unknown content type
    res_unk = validator.validate("{}", "unknown_content_type")
    assert isinstance(res_unk, ValidationResult)
    assert res_unk.passed is False
    assert "Unknown content type" in res_unk.errors[0]

    # 2. JSON parse error
    res_json_err = validator.validate("invalid json {", "diagnostic_item")
    assert res_json_err.passed is False
    assert "JSON parse error" in res_json_err.errors[0]

    # 3. Diagnostic item batch: not a list, empty array, invalid schema, caps_ref mismatch, valid batch
    res_not_list = validator.validate("{}", "diagnostic_item")
    assert res_not_list.passed is False
    assert "Expected a JSON array" in res_not_list.errors[0]

    res_empty_list = validator.validate("[]", "diagnostic_item")
    assert res_empty_list.passed is False
    assert "LLM returned empty array" in res_empty_list.errors[0]

    # Invalid items
    invalid_item = [{"question": "Too short"}]
    res_inv_item = validator.validate(json.dumps(invalid_item), "diagnostic_item")
    assert res_inv_item.passed is False
    assert any("item[0]" in e for e in res_inv_item.errors)

    # Caps_ref mismatch
    valid_diag_raw = {
        "question": "What is 2 + 2 in elementary mathematics?",
        "options": ["3", "4", "5", "6"],
        "correct_answer_index": 1,
        "explanation": "Adding two and two yields four in arithmetic.",
        "bloom_level": "comprehension",
        "difficulty_band": "easy",
        "caps_ref": "4.M.1",
    }
    res_caps_mismatch = validator.validate(
        json.dumps([valid_diag_raw]), "diagnostic_item", caps_ref="4.M.99"
    )
    assert res_caps_mismatch.passed is False
    assert "does not match expected" in res_caps_mismatch.errors[0]


    # Valid diagnostic batch with code fences
    fenced_diag = f"```json\n{json.dumps([valid_diag_raw])}\n```"
    res_valid_diag = validator.validate(fenced_diag, "diagnostic_item", caps_ref="4.M.1")
    assert res_valid_diag.passed is True
    assert res_valid_diag.error_summary == ""
    assert res_valid_diag.validated_payload is not None

    # 4. Lesson payload: null, not dict, schema validation fail, caps_ref mismatch, valid lesson
    res_lesson_null = validator.validate("null", "lesson")
    assert res_lesson_null.passed is False
    assert "LLM returned null" in res_lesson_null.errors[0]

    res_lesson_not_dict = validator.validate('["not a dict"]', "lesson")
    assert res_lesson_not_dict.passed is False
    assert "Expected JSON object" in res_lesson_not_dict.errors[0]

    res_lesson_inv = validator.validate('{"title": "Short"}', "lesson")
    assert res_lesson_inv.passed is False

    valid_lesson_raw = {
        "title": "Introduction to Fractions and Decimals",
        "caps_ref": "4.M.1",
        "grade": 4,
        "subject_code": "MATH",
        "language": "en",
        "learning_objectives": ["Understand fractions as equal parts of a whole"],
        "key_vocabulary": [{"term": "Numerator", "definition": "The top number of a fraction"}],
        "body_markdown": "# Introduction to Fractions\n\nFractions represent equal parts of a whole shape or number. In this comprehensive lesson, we will explore halves, thirds, and quarters.",
        "worked_examples": [{"problem": "Find half of 8", "solution": "Divide 8 by 2 to get 4", "answer": "4"}],
    }
    res_lesson_caps_mismatch = validator.validate(
        json.dumps(valid_lesson_raw), "lesson", caps_ref="4.M.99"
    )
    assert res_lesson_caps_mismatch.passed is False
    assert "does not match expected" in res_lesson_caps_mismatch.errors[0]

    res_lesson_valid = validator.validate(json.dumps(valid_lesson_raw), "lesson", caps_ref="4.M.1")
    assert res_lesson_valid.passed is True

    # 5. Generic content type dispatch and validation error
    res_no_val = validator._dispatch("custom_no_validator", "1.0", {}, None)
    assert res_no_val.passed is False
    assert "No validator for content type" in res_no_val.errors[0]

    from pydantic import BaseModel, Field
    class DummyModel(BaseModel):
        name: str = Field(min_length=5)

    from unittest.mock import patch
    with patch.dict("app.services.content_validator.CONTENT_TYPE_SCHEMAS", {"dummy": DummyModel}):
        res_dummy_ok = validator._dispatch("dummy", "1.0", {"name": "hello world"}, None)
        assert res_dummy_ok.passed is True
        res_dummy_err = validator._dispatch("dummy", "1.0", {"name": "hi"}, None)
        assert res_dummy_err.passed is False



# ============================================================================
# ContentArtifactLifecycleService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_artifact_lifecycle_service():
    factory_service = AsyncMock()
    governance_service = AsyncMock()

    service = ContentArtifactLifecycleService(
        factory_service=factory_service,
        governance_service=governance_service,
    )
    session = AsyncMock()
    session.flush = AsyncMock()

    art_id = uuid.uuid4()
    actor_id = "actor_1"

    # 1. create_artifact and validate_for_review
    factory_service.create_artifact.return_value = MagicMock(artifact_id=art_id)
    created = await service.create_artifact(session, payload={"sample": 1})
    assert created.artifact_id == art_id

    factory_service.validate_existing_artifact.return_value = MagicMock(passed=True)
    assert (await service.validate_for_review(session, art_id)).passed is True

    # 2. submit_for_review: invalid previous status, validation failure, clean submission
    art_approved = ContentGenerationArtifact(
        artifact_id=art_id,
        status=ContentArtifactStatus.APPROVED,
    )
    factory_service.get_artifact.return_value = art_approved
    with pytest.raises(ValueError, match="Only generated, validation_failed"):
        await service.submit_for_review(session, art_id, actor_id)

    art_gen = ContentGenerationArtifact(
        artifact_id=art_id,
        status=ContentArtifactStatus.GENERATED,
    )
    factory_service.get_artifact.return_value = art_gen
    service.validate_for_review = AsyncMock(return_value=MagicMock(passed=False, errors=["schema error"]))
    with pytest.raises(ValueError, match="Artifact validation failed"):
        await service.submit_for_review(session, art_id, actor_id)
    assert art_gen.status == ContentArtifactStatus.VALIDATION_FAILED

    service.validate_for_review = AsyncMock(return_value=MagicMock(passed=True))
    res_submit = await service.submit_for_review(session, art_id, actor_id)
    assert isinstance(res_submit, ArtifactStatusTransition)
    assert res_submit.new_status == ContentArtifactStatus.PENDING_REVIEW.value
    assert art_gen.status == ContentArtifactStatus.PENDING_REVIEW

    # 3. reject_artifact & retire_artifact input validation and transition
    with pytest.raises(ValueError, match="requires a reason"):
        await service.reject_artifact(session, art_id, actor_id, "   ")

    with pytest.raises(ValueError, match="requires a reason"):
        await service.retire_artifact(session, art_id, actor_id, "")

    res_rej = await service.reject_artifact(session, art_id, actor_id, "factual inaccuracies")
    assert res_rej.new_status == ContentArtifactStatus.REJECTED.value

    res_retire = await service.retire_artifact(session, art_id, actor_id, "curriculum updated")
    assert res_retire.new_status == ContentArtifactStatus.RETIRED.value

    # 4. quarantine_artifact
    governance_service.quarantine_artifact.return_value = MagicMock(artifact_id=art_id)
    res_quar = await service.quarantine_artifact(session, art_id, actor_id, "toxic content")
    assert res_quar.new_status == ContentArtifactStatus.QUARANTINED.value

    # 5. mark_seeded_staging (must be approved and publication_eligible)
    art_gen.status = ContentArtifactStatus.PENDING_REVIEW
    factory_service.get_artifact.return_value = art_gen
    with pytest.raises(ValueError, match="Only quorum-approved artifacts"):
        await service.mark_seeded_staging(session, art_id, actor_id)

    art_gen.status = ContentArtifactStatus.APPROVED
    art_gen.publication_eligible = False
    with pytest.raises(ValueError, match="not publication eligible"):
        await service.mark_seeded_staging(session, art_id, actor_id)

    art_gen.publication_eligible = True
    res_stg = await service.mark_seeded_staging(session, art_id, actor_id)
    assert res_stg.new_status == ContentArtifactStatus.SEEDED_STAGING.value
    assert art_gen.status == ContentArtifactStatus.SEEDED_STAGING

    # 6. mark_promoted_production (must be seeded_staging and publication_eligible)
    art_gen.status = ContentArtifactStatus.APPROVED
    with pytest.raises(ValueError, match="Only seeded_staging artifacts"):
        await service.mark_promoted_production(session, art_id, actor_id)

    art_gen.status = ContentArtifactStatus.SEEDED_STAGING
    art_gen.publication_eligible = False
    with pytest.raises(ValueError, match="not publication eligible"):
        await service.mark_promoted_production(session, art_id, actor_id)

    art_gen.publication_eligible = True
    res_prod = await service.mark_promoted_production(session, art_id, actor_id)
    assert res_prod.new_status == ContentArtifactStatus.PROMOTED_PRODUCTION.value
    assert art_gen.status == ContentArtifactStatus.PROMOTED_PRODUCTION

    assert _value(ContentArtifactStatus.PROMOTED_PRODUCTION) == "promoted_production"
    assert _value("raw_string") == "raw_string"
