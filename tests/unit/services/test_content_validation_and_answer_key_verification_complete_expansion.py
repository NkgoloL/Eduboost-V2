"""Comprehensive unit tests covering content validation, answer-key verification, blueprint validation, and template validation."""
import json
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest
from pydantic import ValidationError

from app.models.content_factory import (
    ContentAnswerKeyVerification,
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
)
from app.services.content_answer_key_verification import (
    AnswerKeyVerificationResult,
    ContentAnswerKeyVerificationService,
)
from app.services.content_blueprint_validation import (
    AssessmentBlueprintValidationService,
    BlueprintValidationResult,
)
from app.services.content_template_validation import (
    StudyPlanTemplateValidationResult,
    StudyPlanTemplateValidationService,
)
from app.services.content_validator import ContentValidator, ValidationResult


# ============================================================================
# AssessmentBlueprintValidationService Tests
# ============================================================================
def test_assessment_blueprint_validation():
    service = AssessmentBlueprintValidationService()

    # 1. Missing json content
    res = service.validate({}, approved_diagnostic_item_ids=set())
    assert isinstance(res, BlueprintValidationResult)
    assert res.passed is False
    assert any("requires content_json or blueprint_json" in e for e in res.errors)

    # 2. Unapproved diagnostic item referenced
    res_missing = service.validate(
        {"blueprint_json": {"sections": []}, "referenced_artifact_ids": ["art1", "art2"]},
        approved_diagnostic_item_ids={"art1"},
    )
    assert res_missing.passed is False
    assert any("reference only approved diagnostic items: art2" in e for e in res_missing.errors)

    # 3. Valid blueprint
    res_valid = service.validate(
        {"content_json": {"title": "Math Quiz"}, "referenced_artifact_ids": ["art1"]},
        approved_diagnostic_item_ids={"art1", "art2"},
    )
    assert res_valid.passed is True
    assert len(res_valid.errors) == 0


# ============================================================================
# StudyPlanTemplateValidationService Tests
# ============================================================================
def test_study_plan_template_validation():
    service = StudyPlanTemplateValidationService()

    # 1. Missing json content
    res = service.validate({}, approved_reference_ids=set())
    assert isinstance(res, StudyPlanTemplateValidationResult)
    assert res.passed is False
    assert any("requires content_json or template_json" in e for e in res.errors)

    # 2. Unapproved reference id
    res_missing = service.validate(
        {"template_json": {"weeks": []}, "referenced_artifact_ids": ["ref1", "ref2"]},
        approved_reference_ids={"ref1"},
    )
    assert res_missing.passed is False
    assert any("reference only approved lessons or blueprints: ref2" in e for e in res_missing.errors)

    # 3. Valid template
    res_valid = service.validate(
        {"content_json": {"title": "Term 1 Plan"}, "referenced_artifact_ids": ["ref1"]},
        approved_reference_ids={"ref1"},
    )
    assert res_valid.passed is True
    assert len(res_valid.errors) == 0


# ============================================================================
# ContentAnswerKeyVerificationService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_answer_key_verification_latest_for_artifact():
    service = ContentAnswerKeyVerificationService()
    session = AsyncMock()

    art = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        version_number=1,
        artifact_hash="hash1",
    )
    mock_ver = ContentAnswerKeyVerification(
        verification_id=uuid.uuid4(),
        artifact_id=art.artifact_id,
        artifact_version=1,
        artifact_hash="hash1",
        method="deterministic_recompute",
        passed=True,
    )
    session.scalar.return_value = mock_ver

    latest = await service.latest_for_artifact(session, art)
    assert latest == mock_ver
    session.scalar.assert_awaited_once()


@pytest.mark.asyncio
async def test_content_answer_key_verification_record():
    service = ContentAnswerKeyVerificationService()
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()

    art_id = uuid.uuid4()

    # 1. Invalid method
    with pytest.raises(ValueError, match="Unsupported answer-key verification method"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="unsupported_method",
            passed=True,
            verifier_actor_id="actor1",
            idempotency_key="key1",
            details={"verification_basis": "computed"},
        )

    # 2. Empty idempotency key
    with pytest.raises(ValueError, match="An idempotency key is required"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="deterministic_recompute",
            passed=True,
            verifier_actor_id="actor1",
            idempotency_key="   ",
            details={"verification_basis": "computed"},
        )

    # 3. Passed without verification_basis
    with pytest.raises(ValueError, match="Passing verification requires details.verification_basis"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="deterministic_recompute",
            passed=True,
            verifier_actor_id="actor1",
            idempotency_key="key1",
            details={},
        )

    # 4. Idempotent replay with different artifact_id
    existing_other = ContentAnswerKeyVerification(
        verification_id=uuid.uuid4(),
        artifact_id=uuid.uuid4(),
        artifact_version=1,
        artifact_hash="hash1",
        method="deterministic_recompute",
        passed=True,
        verifier_actor_id="actor1",
        idempotency_key="key1",
    )
    session.scalar.return_value = existing_other
    with pytest.raises(ValueError, match="Idempotency key was already used for another artifact"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="deterministic_recompute",
            passed=True,
            verifier_actor_id="actor1",
            idempotency_key="key1",
            details={"verification_basis": "computed"},
        )

    # 5. Idempotent replay matching artifact_id
    existing_same = ContentAnswerKeyVerification(
        verification_id=uuid.uuid4(),
        artifact_id=art_id,
        artifact_version=1,
        artifact_hash="hash1",
        method="deterministic_recompute",
        passed=True,
        verifier_actor_id="actor1",
        idempotency_key="key1",
    )
    session.scalar.return_value = existing_same
    replay_res = await service.record(
        session,
        artifact_id=art_id,
        expected_version=1,
        expected_artifact_hash="hash1",
        method="deterministic_recompute",
        passed=True,
        verifier_actor_id="actor1",
        idempotency_key="key1",
        details={"verification_basis": "computed"},
    )
    assert replay_res.idempotent_replay is True
    assert replay_res.artifact_id == art_id

    # 6. Artifact not found
    session.scalar.side_effect = [None, None]  # existing=None, artifact=None
    with pytest.raises(LookupError, match="not found"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="deterministic_recompute",
            passed=False,
            verifier_actor_id="actor1",
            idempotency_key="key_new",
            details={},
        )

    # 7. Version mismatch
    art_rec = ContentGenerationArtifact(
        artifact_id=art_id,
        version_number=2,
        artifact_hash="hash1",
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
        status=ContentArtifactStatus.APPROVED,
    )
    session.scalar.side_effect = [None, art_rec]
    with pytest.raises(ValueError, match="Artifact version changed"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="deterministic_recompute",
            passed=False,
            verifier_actor_id="actor1",
            idempotency_key="key_new",
            details={},
        )

    # 8. Hash mismatch
    art_rec.version_number = 1
    art_rec.artifact_hash = "new_hash"
    session.scalar.side_effect = [None, art_rec]
    with pytest.raises(ValueError, match="Artifact hash changed"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="old_hash",
            method="deterministic_recompute",
            passed=False,
            verifier_actor_id="actor1",
            idempotency_key="key_new",
            details={},
        )

    # 9. Non diagnostic item layer
    art_rec.artifact_hash = "hash1"
    art_rec.content_layer = "lessons"
    art_rec.artifact_type = "lesson"
    session.scalar.side_effect = [None, art_rec]
    with pytest.raises(ValueError, match="Answer-key verification applies only to diagnostic items"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="deterministic_recompute",
            passed=False,
            verifier_actor_id="actor1",
            idempotency_key="key_new",
            details={},
        )

    # 10. Clean successful record (passed=True, publication_eligible updated)
    art_rec.content_layer = "diagnostic_items"
    art_rec.artifact_type = "diagnostic_item"
    art_rec.status = ContentArtifactStatus.APPROVED
    session.scalar.side_effect = [None, art_rec]
    rec_res = await service.record(
        session,
        artifact_id=art_id,
        expected_version=1,
        expected_artifact_hash="hash1",
        method="deterministic_recompute",
        passed=True,
        verifier_actor_id="actor1",
        idempotency_key="key_pass",
        details={"verification_basis": "deterministic math solver"},
        verifier_provider="custom_solver",
        verifier_model="v1",
    )
    assert isinstance(rec_res, AnswerKeyVerificationResult)
    assert rec_res.passed is True
    assert art_rec.answer_key_verified is True
    assert art_rec.publication_eligible is True


# ============================================================================
# ContentValidator Tests
# ============================================================================
def test_content_validator_unknown_type():
    validator = ContentValidator()
    res = validator.validate("{}", "unknown_type")
    assert res.passed is False
    assert any("Unknown content type" in e for e in res.errors)
    assert res.error_summary != ""


def test_content_validator_json_decode_error():
    validator = ContentValidator()
    res = validator.validate("{not valid json", "diagnostic_item")
    assert res.passed is False
    assert any("JSON parse error" in e for e in res.errors)


def test_content_validator_diagnostic_batch():
    validator = ContentValidator()

    # Not a list
    res_not_list = validator.validate('{"key": "value"}', "diagnostic_item")
    assert res_not_list.passed is False
    assert any("Expected a JSON array" in e for e in res_not_list.errors)

    # Empty list
    res_empty = validator.validate("[]", "diagnostic_item")
    assert res_empty.passed is False
    assert any("LLM returned empty array" in e for e in res_empty.errors)

    # Valid diagnostic items with markdown fence
    valid_items = [
        {
            "question": "What is 2 + 2 in elementary mathematics?",
            "options": ["3", "4", "5", "6"],
            "correct_answer_index": 1,
            "explanation": "Adding 2 and 2 equals 4 under standard arithmetic.",
            "bloom_level": "knowledge",
            "difficulty_band": "easy",
            "caps_ref": "4.M.1.1",
            "tags": ["addition"],
        }
    ]
    fenced_text = f"```json\n{json.dumps(valid_items)}\n```"
    res_valid = validator.validate(fenced_text, "diagnostic_item", caps_ref="4.M.1.1")
    assert res_valid.passed is True
    assert res_valid.validated_payload is not None
    assert len(res_valid.validated_payload.items) == 1

    # caps_ref mismatch in batch item
    res_mismatch = validator.validate(json.dumps(valid_items), "diagnostic_item", caps_ref="5.M.2.2")
    assert res_mismatch.passed is False
    assert any("does not match expected" in e for e in res_mismatch.errors)

    # Invalid item structure (e.g. out of range correct_answer_index)
    bad_items = [
        {
            "question": "What is 2 + 2 in elementary mathematics?",
            "options": ["3", "4"],
            "correct_answer_index": 5,
            "explanation": "Out of range index provided here for test.",
            "bloom_level": "knowledge",
            "difficulty_band": "easy",
            "caps_ref": "4.M.1.1",
        }
    ]
    res_bad = validator.validate(json.dumps(bad_items), "diagnostic_item")
    assert res_bad.passed is False
    assert any("correct_answer_index" in e for e in res_bad.errors)



def test_content_validator_lesson():
    validator = ContentValidator()

    # Null output
    res_null = validator.validate("null", "lesson")
    assert res_null.passed is False
    assert any("LLM returned null" in e for e in res_null.errors)

    # Not a dict
    res_not_dict = validator.validate("[\"not\", \"a\", \"dict\"]", "lesson")
    assert res_not_dict.passed is False
    assert any("Expected JSON object for lesson" in e for e in res_not_dict.errors)

    # Valid lesson
    valid_lesson = {
        "title": "Introduction to Fractions and Parts",
        "caps_ref": "4.M.1.1",
        "grade": 4,
        "subject_code": "MATH",
        "language": "en",
        "learning_objectives": ["Understand numerator and denominator in unit fractions."],
        "key_vocabulary": [{"term": "Numerator", "definition": "Top number of a fraction."}],
        "body_markdown": "Fractions represent parts of a whole shape or number. In this comprehensive lesson, learners explore real-world examples with pizzas and chocolate bars.",
        "worked_examples": [{"problem": "Divide a circle into 4 parts.", "solution": "Draw 2 orthogonal lines through the center.", "answer": "4 equal quadrants."}],
    }
    res_valid = validator.validate(json.dumps(valid_lesson), "lesson", caps_ref="4.M.1.1")
    assert res_valid.passed is True
    assert res_valid.validated_payload is not None

    # caps_ref mismatch in lesson
    res_mismatch = validator.validate(json.dumps(valid_lesson), "lesson", caps_ref="6.M.3.3")
    assert res_mismatch.passed is False
    assert any("does not match expected" in e for e in res_mismatch.errors)

    # ValidationError on lesson (e.g. body too short)
    bad_lesson = dict(valid_lesson)
    bad_lesson["body_markdown"] = "Too short"
    res_short = validator.validate(json.dumps(bad_lesson), "lesson")
    assert res_short.passed is False
    assert any("body_markdown" in e for e in res_short.errors)


def test_content_validator_custom_type_dispatch():
    from app.services.content_schemas import CONTENT_TYPE_SCHEMAS, CONTENT_TYPE_SCHEMA_VERSIONS
    from pydantic import BaseModel

    class CustomModel(BaseModel):
        field: str

    validator = ContentValidator()
    CONTENT_TYPE_SCHEMA_VERSIONS["custom"] = "1.0"

    # No schema registered
    res_no_schema = validator.validate('{"field": "val"}', "custom")
    assert res_no_schema.passed is False
    assert any("No validator for content type" in e for e in res_no_schema.errors)

    # Schema registered - valid
    CONTENT_TYPE_SCHEMAS["custom"] = CustomModel
    try:
        res_ok = validator.validate('{"field": "val"}', "custom")
        assert res_ok.passed is True
        assert res_ok.validated_payload.field == "val"

        # Schema registered - validation error
        res_fail = validator.validate('{"field": 123}', "custom")
        # In strict or type check mode:
        res_empty = validator.validate('{}', "custom")
        assert res_empty.passed is False
        assert any("field" in e for e in res_empty.errors)
    finally:
        CONTENT_TYPE_SCHEMAS.pop("custom", None)
        CONTENT_TYPE_SCHEMA_VERSIONS.pop("custom", None)

