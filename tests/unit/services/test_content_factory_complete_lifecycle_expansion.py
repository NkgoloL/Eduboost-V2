import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.content_factory import (
    ContentArtifactReview,
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentReviewAction,
    ContentValidationReport,
)
from app.services.content_factory import (
    ContentValidationService,
    ContentFactoryService,
    _source_to_bundle_item,
    _enum_value,
)


def test_content_validation_service_all_branches():
    service = ContentValidationService()

    # 1. Empty artifact_json
    res_empty = service.validate_artifact_payload(
        artifact_json={},
        caps_ref="4.M.1",
        sources=[],
        artifact_type="lesson",
    )
    assert res_empty["passed"] is False
    assert "artifact_json must not be empty." in res_empty["errors"]

    # 2. Diagnostic item without answer_key
    res_diag_nokey = service.validate_artifact_payload(
        artifact_json={"question": "What is 2+2?"},
        caps_ref="4.M.1",
        sources=[],
        artifact_type="diagnostic_item",
    )
    assert res_diag_nokey["passed"] is False
    assert "diagnostic_item artifacts require answer_key." in res_diag_nokey["errors"]

    # 3. Invalid safety_status
    res_unsafe = service.validate_artifact_payload(
        artifact_json={"answer_key": "4", "safety_status": "flagged"},
        caps_ref="4.M.1",
        sources=[],
        artifact_type="diagnostic_item",
    )
    assert res_unsafe["passed"] is False
    assert any("safety_status must be passed/safe/approved" in e for e in res_unsafe["errors"])


@pytest.mark.asyncio
async def test_content_factory_service_create_and_validate():
    factory = ContentFactoryService()
    session = AsyncMock()

    payload = {
        "artifact_type": "diagnostic_item",
        "scope_id": "scope-1",
        "caps_ref": "4.M.1",
        "grade": 4,
        "subject_code": "MATHS",
        "language": "en",
        "content_layer": "diagnostic_items",
        "artifact_json": {
            "question": "What is 10/2?",
            "answer_key": "5",
            "safety_status": "passed",
        },
        "sources": [
            {
                "source_document_id": "doc-10",
                "source_chunk_id": "chunk-20",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.85,
                "caps_ref": "4.M.1",
                "extra_metadata_field": "test_meta",
            }
        ],
    }

    # create_artifact
    artifact = await factory.create_artifact(session, payload=dict(payload))
    assert artifact.status == ContentArtifactStatus.PENDING_REVIEW
    assert artifact.source_snapshot_hash is not None
    session.add.assert_called()

    # validate_existing_artifact
    real_source = ContentArtifactSource(
        source_id=uuid.uuid4(),
        artifact_id=artifact.artifact_id,
        source_document_id="doc-10",
        source_chunk_id="chunk-20",
        curriculum_mapping_id="map-1",
        source_hash="sha-1",
        source_metadata={"document_status": "approved", "license_status": "government_open", "caps_ref": "4.M.1"},
        source_quality_score=0.9,
    )
    artifact.sources = [real_source]

    # Mock _get_artifact
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = artifact
    session.execute = AsyncMock(return_value=mock_result)

    report = await factory.validate_existing_artifact(session, artifact.artifact_id)
    assert report.passed is True
    assert artifact.status == ContentArtifactStatus.PENDING_REVIEW


@pytest.mark.asyncio
async def test_content_factory_service_reviews_and_gates():
    factory = ContentFactoryService()
    session = AsyncMock()

    artifact_id = uuid.uuid4()
    real_source = ContentArtifactSource(
        source_id=uuid.uuid4(),
        artifact_id=artifact_id,
        source_document_id="doc-1",
        source_chunk_id="chunk-1",
        source_title="Title",
        source_type="text",
        source_uri="s3://uri",
        citation_text="Citation",
        caps_ref="4.M.1",
        grade=4,
        subject_code="MATHS",
        language="en",
        license_status="government_open",
        source_quality_score=0.9,
        etl_version="1.0",
        document_version_id="ver-1",
        chunk_hash="chash-1",
        curriculum_mapping_id="map-1",
        source_hash="shash-1",
        source_role="primary_context",
        source_metadata={"document_status": "approved"},
    )

    art = ContentGenerationArtifact(
        artifact_id=artifact_id,
        artifact_hash="hash-1",
        artifact_type="lesson",
        scope_id="scope-1",
        caps_ref="4.M.1",
        grade=4,
        subject_code="MATHS",
        language="en",
        content_layer="lessons",
        status=ContentArtifactStatus.PENDING_REVIEW,
        artifact_json={"title": "Lesson 1"},
    )
    art.sources = [real_source]


    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = art
    session.execute = AsyncMock(return_value=mock_result)

    # 1. get_artifact found vs not found
    got = await factory.get_artifact(session, artifact_id)
    assert got.artifact_id == artifact_id

    mock_result_none = MagicMock()
    mock_result_none.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=mock_result_none)
    with pytest.raises(LookupError, match="not found"):
        await factory.get_artifact(session, uuid.uuid4())

    # Reset artifact
    session.execute = AsyncMock(return_value=mock_result)

    # 2. review_artifact APPROVE
    rev_app = await factory.review_artifact(
        session,
        artifact_id=artifact_id,
        reviewer_id="reviewer-1",
        review_action=ContentReviewAction.APPROVE,
        review_reason="Looks good",
        quality_score=0.95,
    )
    assert art.status == ContentArtifactStatus.APPROVED
    assert rev_app.review_action == ContentReviewAction.APPROVE

    # Cannot approve when status is already APPROVED
    with pytest.raises(ValueError, match="Only pending_review artifacts can be approved"):
        await factory.review_artifact(
            session,
            artifact_id=artifact_id,
            reviewer_id="reviewer-1",
            review_action=ContentReviewAction.APPROVE,
        )

    # Cannot approve when sources are empty
    art.status = ContentArtifactStatus.PENDING_REVIEW
    art.sources = []
    with pytest.raises(ValueError, match="Cannot approve artifact without ETL source citations"):
        await factory.review_artifact(
            session,
            artifact_id=artifact_id,
            reviewer_id="reviewer-1",
            review_action=ContentReviewAction.APPROVE,
        )

    # Restore sources
    art.sources = [real_source]


    # review_artifact REJECT
    await factory.review_artifact(
        session,
        artifact_id=artifact_id,
        reviewer_id="reviewer-1",
        review_action=ContentReviewAction.REJECT,
    )
    assert art.status == ContentArtifactStatus.REJECTED

    # review_artifact QUARANTINE
    await factory.review_artifact(
        session,
        artifact_id=artifact_id,
        reviewer_id="reviewer-1",
        review_action=ContentReviewAction.QUARANTINE,
    )
    assert art.status == ContentArtifactStatus.QUARANTINED

    # review_artifact REQUEST_CHANGES
    await factory.review_artifact(
        session,
        artifact_id=artifact_id,
        reviewer_id="reviewer-1",
        review_action=ContentReviewAction.REQUEST_CHANGES,
    )
    assert art.status == ContentArtifactStatus.VALIDATION_FAILED

    # 3. validate_artifact_sources & get_artifact_provenance & assert_artifact_has_approved_sources
    gate = await factory.validate_artifact_sources(session, artifact_id)
    assert gate.passed is True

    provenance = await factory.get_artifact_provenance(session, artifact_id)
    assert provenance.passed is True
    assert len(provenance.sources) == 1

    await factory.assert_artifact_has_approved_sources(session, artifact_id)

    # assert failure when sources invalid
    art.caps_ref = "MISMATCHED_REF"
    with pytest.raises(ValueError, match="Artifact provenance validation failed"):
        await factory.assert_artifact_has_approved_sources(session, artifact_id)


def test_source_to_bundle_item_and_enum_value():
    assert _enum_value("already_str") == "already_str"
    assert _enum_value(ContentArtifactStatus.APPROVED) == "approved"

    mock_src = MagicMock(
        spec=ContentArtifactSource,
        source_document_id="doc-x",
        source_chunk_id="chk-x",
        source_title="Title X",
        source_type="doc",
        source_uri=None,
        citation_text="Sample citation",
        caps_ref=None,
        grade=4,
        subject_code="MATHS",
        language="en",
        license_status=None,
        source_quality_score=None,
        etl_version="2.0",
        document_version_id="dv-1",
        chunk_hash="ch-1",
        curriculum_mapping_id="cm-1",
        source_hash="sh-1",
        source_role="secondary",
        source_metadata={"caps_ref": "4.M.1", "license_status": "government_open", "chunk_quality_score": 0.8},
    )
    bundle_item = _source_to_bundle_item(mock_src)
    assert bundle_item["source_document_id"] == "doc-x"
    assert bundle_item["caps_ref"] == "4.M.1"
    assert bundle_item["license_status"] == "government_open"
    assert bundle_item["chunk_quality_score"] == 0.8
