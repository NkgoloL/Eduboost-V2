"""Comprehensive unit tests covering content factory orchestrator, schemas, and factory service."""
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest

from app.domain.content_coverage import ContentLayer
from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentReviewAction,
)
from app.services.content_factory import (
    ContentFactoryService,
    ContentValidationService,
    ETLProvenanceService,
    _enum_value,
    _source_to_bundle_item,
)
from app.services.content_factory_orchestrator import (
    ContentFactoryOrchestrator,
    OrchestratorPlan,
    PIPELINE_STATES,
)
from app.services.content_schemas import (
    DiagnosticItemBatch,
    DiagnosticItemPayload,
    LessonPayload,
    VocabularyEntry,
    WorkedExample,
    get_schema_version,
)


# ============================================================================
# ContentSchemas Tests
# ============================================================================
def test_content_schemas():
    # 1. get_schema_version
    assert get_schema_version("diagnostic_item") == "1.0"
    assert get_schema_version("lesson") == "1.0"
    with pytest.raises(KeyError, match="Unknown content type"):
        get_schema_version("invalid_type")

    # 2. DiagnosticItemPayload model validation rules
    # valid payload
    diag_valid = DiagnosticItemPayload(
        question="What is the result of adding 3 and 7?",
        options=["8", "9", "10", "11"],
        correct_answer_index=2,
        explanation="Three plus seven equals exactly ten.",
        bloom_level="knowledge",
        difficulty_band="easy",
        caps_ref="4.M.1",
        tags=["addition", "integers"],
    )
    assert diag_valid.question.startswith("What is")

    # out-of-range correct_answer_index
    with pytest.raises(ValueError, match="out of range"):
        DiagnosticItemPayload(
            question="What is the result of adding 3 and 7?",
            options=["8", "9", "10"],
            correct_answer_index=5,
            explanation="Three plus seven equals exactly ten.",
            bloom_level="knowledge",
            difficulty_band="easy",
            caps_ref="4.M.1",
        )

    # non-unique options
    with pytest.raises(ValueError, match="options must be unique"):
        DiagnosticItemPayload(
            question="What is the result of adding 3 and 7?",
            options=["10", "10", "11"],
            correct_answer_index=0,
            explanation="Three plus seven equals exactly ten.",
            bloom_level="knowledge",
            difficulty_band="easy",
            caps_ref="4.M.1",
        )

    # 3. DiagnosticItemBatch from_list
    batch = DiagnosticItemBatch.from_list([diag_valid.model_dump(mode="json")])
    assert len(batch.items) == 1

    # 4. LessonPayload, VocabularyEntry, WorkedExample
    vocab = VocabularyEntry(term="Hypotenuse", definition="The longest side of a right-angled triangle.")
    example = WorkedExample(
        problem="Calculate the area of a rectangle with length 4 and width 5.",
        solution="Area equals length times width. Multiply 4 by 5 to obtain 20.",
        answer="20 square units",
    )
    lesson = LessonPayload(
        title="Understanding Area and Perimeter in Geometry",
        caps_ref="4.M.2",
        grade=4,
        subject_code="MATH",
        language="en",
        learning_objectives=["Calculate rectangle area"],
        key_vocabulary=[vocab],
        body_markdown="# Geometry Lesson\n\nArea measures the total surface covered by a flat 2D shape or region. In this detailed lesson, we explore regular and irregular polygons.",
        worked_examples=[example],
    )
    assert lesson.grade == 4
    assert len(lesson.worked_examples) == 1


# ============================================================================
# ContentFactoryOrchestrator Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_factory_orchestrator():
    run_service = AsyncMock()
    orchestrator = ContentFactoryOrchestrator(run_service=run_service)
    session = AsyncMock()

    run_id = uuid.uuid4()
    scope_id = "scope_math_g4"

    mock_run = MagicMock(run_id=run_id)
    run_service.create_run.return_value = mock_run
    run_service.create_tasks_for_run.return_value = [MagicMock(), MagicMock()]

    # 1. create_dry_run_plan with generation_enabled = false
    with patch.dict("os.environ", {"CONTENT_FACTORY_GENERATION_ENABLED": "false"}):
        assert orchestrator.generation_enabled is False
        plan = await orchestrator.create_dry_run_plan(
            session,
            scope_id=scope_id,
            layers=[ContentLayer.DIAGNOSTIC_ITEMS],
            requested_by="admin",
        )
        assert isinstance(plan, OrchestratorPlan)
        assert plan.run_id == run_id
        assert plan.dry_run is True
        assert plan.generation_enabled is False
        assert plan.planned_states == PIPELINE_STATES
        assert plan.task_count == 2

    # 2. execute_noop
    run_service.get_run.return_value = mock_run
    run_service.get_run_tasks.return_value = [MagicMock()]
    noop_plan = await orchestrator.execute_noop(session, run_id)
    assert noop_plan.task_count == 1
    assert noop_plan.dry_run is True


# ============================================================================
# ContentFactoryService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_factory_service():
    service = ContentFactoryService()
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    art_id = uuid.uuid4()
    scope_id = "scope_math_g4"

    # 1. create_artifact with passing validation & sources
    valid_payload = {
        "scope_id": scope_id,
        "content_layer": "diagnostic_items",
        "artifact_type": "diagnostic_item",
        "caps_ref": "4.M.1",
        "artifact_json": {
            "question": "What is 1 + 1?",
            "answer_key": "2",
            "safety_status": "passed",
        },
        "sources": [
            {
                "source_document_id": "doc_1",
                "source_chunk_id": "chunk_1",
                "curriculum_mapping_id": "map_1",
                "source_hash": "shash_1",
                "source_title": "Textbook Chapter 1",
                "source_type": "pdf",
                "source_uri": "s3://eduboost-sources/doc1.pdf",
                "citation_text": "Page 5",
                "caps_ref": "4.M.1",
                "grade": 4,
                "subject_code": "MATH",
                "language": "en",
                "license_status": "open_license",
                "document_status": "approved",
                "source_quality_score": 0.95,
                "etl_version": "1.0",
                "document_version_id": "v1",
                "chunk_hash": "chash_1",
                "custom_metadata_key": "custom_val",
            }
        ],
    }


    created_art = await service.create_artifact(session, payload=valid_payload)
    assert isinstance(created_art, ContentGenerationArtifact)
    assert created_art.status == ContentArtifactStatus.PENDING_REVIEW
    session.add.assert_called()

    # 2. _get_artifact LookupError
    session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    with pytest.raises(LookupError, match="not found"):
        await service.get_artifact(session, art_id)

    # 3. validate_existing_artifact
    mock_source = ContentArtifactSource(
        source_document_id="doc_1",
        source_chunk_id="chunk_1",
        curriculum_mapping_id="map_1",
        source_hash="shash_1",
        source_quality_score=0.9,
        license_status="open_license",
        caps_ref="4.M.1",
        source_metadata={"document_status": "approved"},
    )
    created_art.sources = [mock_source]
    session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=created_art))
    val_report = await service.validate_existing_artifact(session, art_id)
    assert val_report.passed is True


    # 4. review_artifact - validation checks
    # Non-pending approval error
    created_art.status = ContentArtifactStatus.APPROVED
    with pytest.raises(ValueError, match="Only pending_review artifacts can be approved"):
        await service.review_artifact(
            session,
            artifact_id=art_id,
            reviewer_id="rev_1",
            review_action=ContentReviewAction.APPROVE,
        )

    # Missing sources approval error
    created_art.status = ContentArtifactStatus.PENDING_REVIEW
    created_art.sources = []
    with pytest.raises(ValueError, match="Cannot approve artifact without ETL source citations"):
        await service.review_artifact(
            session,
            artifact_id=art_id,
            reviewer_id="rev_1",
            review_action=ContentReviewAction.APPROVE,
        )

    # Clean reviews: Approve, Reject, Quarantine, Request Changes
    created_art.sources = [mock_source]
    review_app = await service.review_artifact(
        session,
        artifact_id=art_id,
        reviewer_id="rev_1",
        review_action=ContentReviewAction.APPROVE,
        quality_score=0.98,
    )
    assert created_art.status == ContentArtifactStatus.APPROVED
    assert review_app.quality_score == 0.98

    created_art.status = ContentArtifactStatus.PENDING_REVIEW
    await service.review_artifact(
        session,
        artifact_id=art_id,
        reviewer_id="rev_1",
        review_action=ContentReviewAction.REJECT,
        review_reason="inaccurate",
    )
    assert created_art.status == ContentArtifactStatus.REJECTED

    await service.review_artifact(
        session,
        artifact_id=art_id,
        reviewer_id="rev_1",
        review_action=ContentReviewAction.QUARANTINE,
    )
    assert created_art.status == ContentArtifactStatus.QUARANTINED

    await service.review_artifact(
        session,
        artifact_id=art_id,
        reviewer_id="rev_1",
        review_action=ContentReviewAction.REQUEST_CHANGES,
    )
    assert created_art.status == ContentArtifactStatus.VALIDATION_FAILED

    # 5. validate_artifact_sources & get_artifact_provenance & assert_artifact_has_approved_sources
    mock_source.source_metadata = {"document_status": "approved"}
    gate_res = await service.validate_artifact_sources(session, art_id)
    assert gate_res.passed is True


    prov_rep = await service.get_artifact_provenance(session, art_id)
    assert prov_rep.passed is True
    assert len(prov_rep.sources) == 1

    await service.assert_artifact_has_approved_sources(session, art_id)

    # Failing provenance raises ValueError
    service.validate_artifact_sources = AsyncMock(return_value=MagicMock(passed=False, errors=["unapproved"]))
    with pytest.raises(ValueError, match="Artifact provenance validation failed"):
        await service.assert_artifact_has_approved_sources(session, art_id)

    # 6. ETLProvenanceService and ContentValidationService edge cases
    etl = ETLProvenanceService()
    # Missing source_document_id and source_chunk_id, incompatible license, bad status, caps mismatch
    bad_source = {
        "license_status": "restricted",
        "document_status": "draft",
        "caps_ref": "4.M.99",
    }
    gate_fail = etl.validate_source_bundle(
        caps_ref="4.M.1",
        sources=[bad_source],
        min_sources=2,
        require_approved_documents=True,
    )
    assert gate_fail.passed is False
    assert any("source_document_id is required" in e for e in gate_fail.errors)
    assert any("source_chunk_id is required" in e for e in gate_fail.errors)
    assert any("incompatible license_status" in e for e in gate_fail.errors)
    assert any("document must be approved" in e for e in gate_fail.errors)
    assert any("does not match artifact caps_ref" in e for e in gate_fail.errors)
    assert any("requires at least 2 cited ETL source" in e for e in gate_fail.errors)

    # ContentValidationService edge cases
    cvs = ContentValidationService()
    res_empty = cvs.validate_artifact_payload(
        artifact_json={},
        caps_ref="4.M.1",
        sources=[],
        artifact_type="diagnostic_item",
    )
    assert res_empty["passed"] is False
    assert any("artifact_json must not be empty" in e for e in res_empty["errors"])
    assert any("artifacts require answer_key" in e for e in res_empty["errors"])

    res_bad_safety = cvs.validate_artifact_payload(
        artifact_json={"answer_key": "A", "safety_status": "quarantined_unsafe"},
        caps_ref="4.M.1",
        sources=[{
            "source_document_id": "d1",
            "source_chunk_id": "c1",
            "license_status": "open_license",
        }],
        artifact_type="diagnostic_item",
    )
    assert res_bad_safety["passed"] is False
    assert any("safety_status must be passed/safe/approved" in e for e in res_bad_safety["errors"])

    # 7. Helpers
    assert _enum_value(ContentArtifactStatus.APPROVED) == "approved"
    bundle_dict = _source_to_bundle_item(mock_source)
    assert bundle_dict["source_document_id"] == "doc_1"

