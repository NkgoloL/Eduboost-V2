import uuid
from pathlib import Path
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.content_factory import (
    ContentGenerationArtifact,
    ContentArtifactStatus,
    ContentLayer,
    ContentArtifactType,
    ContentArtifactSource,
)
from app.models.curriculum_expansion import (
    TrainingDatasetManifest,
    TrainingDatasetEntry,
)

from app.services.curriculum_expansion import (
    TrainingDatasetGovernanceService,
    artifact_eligibility_reasons,
    build_training_record,
    record_sha256,
    dataset_sha256,
)


@pytest.mark.asyncio
async def test_artifact_eligibility_reasons_all_branches():
    # 1. Ineligible status & missing hashes
    art_ineligible = MagicMock(
        spec=ContentGenerationArtifact,
        status="quarantined",
        artifact_hash=None,
        source_snapshot_hash=None,
        quality_score=0.9,
        caps_alignment_score=0.3,
        safety_status="failed",
        content_layer="diagnostic_items",
        answer_key_verified=False,
        sources=[],
        artifact_json={"learner_id": "lrn-123", "placeholder": "TODO"},
        language="en",
    )
    reasons = artifact_eligibility_reasons(
        art_ineligible,
        require_published=False,
        min_quality_score=0.8,
        min_caps_alignment_score=0.7,
    )
    assert "ineligible_lifecycle_state" in reasons
    assert "missing_artifact_hash" in reasons
    assert "missing_source_snapshot_hash" in reasons
    assert "caps_alignment_below_threshold" in reasons
    assert "missing_sources" in reasons
    assert "forbidden_operational_fields" in reasons
    assert "language_validation_failed" in reasons

    # 2. PII findings and language failure
    art_pii = MagicMock(
        spec=ContentGenerationArtifact,
        status="approved",
        artifact_hash="hash1",
        source_snapshot_hash="snap1",
        quality_score=0.9,
        caps_alignment_score=0.9,
        safety_status="passed",
        content_layer="lessons",
        answer_key_verified=True,
        sources=[MagicMock(license_status="open_license", source_hash="sh1", chunk_hash="ch1")],
        artifact_json={"email_str": "student@school.za"},
        language="en",
    )
    reasons_pii = artifact_eligibility_reasons(
        art_pii,
        require_published=False,
        min_quality_score=0.8,
        min_caps_alignment_score=0.8,
    )
    assert "obvious_pii" in reasons_pii

    # 3. Disallowed license
    art_bad_lic = MagicMock(
        spec=ContentGenerationArtifact,
        status="approved",
        artifact_hash="hash1",
        source_snapshot_hash="snap1",
        quality_score=0.9,
        caps_alignment_score=0.9,
        safety_status="passed",
        content_layer="lessons",
        answer_key_verified=True,
        sources=[MagicMock(license_status="proprietary_copyright", source_hash="sh1", chunk_hash="ch1")],
        artifact_json={"text": "Clean content"},
        language="en",
    )
    reasons_lic = artifact_eligibility_reasons(
        art_bad_lic,
        require_published=False,
        min_quality_score=0.8,
        min_caps_alignment_score=0.8,
    )
    assert "disallowed_source_license" in reasons_lic


@pytest.mark.asyncio
async def test_training_dataset_governance_service_full_lifecycle(tmp_path):
    db = AsyncMock()
    service = TrainingDatasetGovernanceService(db=db, artifact_root=tmp_path)

    # 1. _safe_output_path escape detection
    with pytest.raises(ValueError, match="Output path escapes"):
        service._safe_output_path("../../escaped.jsonl")

    valid_path = service._safe_output_path("dataset_v1.jsonl")
    assert valid_path.parent == tmp_path

    # 2. create_manifest when existing returns early
    existing_manifest = MagicMock(spec=TrainingDatasetManifest, dataset_version="v1.0")
    db.scalar.return_value = existing_manifest
    res_existing = await service.create_manifest(
        dataset_version="v1.0",
        scope_ids=["scope_1"],
        languages=["en"],
        created_by="admin_1",
        require_published=False,
        min_quality_score=0.8,
        min_caps_alignment_score=0.8,
        policy_version="1.0",
        rubric_version="1.0",
    )
    assert res_existing == existing_manifest

    # 3. create_manifest fresh with candidates
    db.scalar.return_value = None

    art1 = MagicMock(
        spec=ContentGenerationArtifact,
        artifact_id=uuid.uuid4(),
        artifact_hash="hash-123",
        artifact_version=1,
        version_number=1,
        grade=4,
        subject_code="MATHEMATICS",
        scope_id="scope_1",

        caps_ref="4.M.1",
        language="en",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
        artifact_type=ContentArtifactType.DIAGNOSTIC_ITEM,
        status="approved",
        quality_score=0.95,
        caps_alignment_score=0.90,
        source_snapshot_hash="snap-hash-1",
        safety_status="passed",
        answer_key_verified=True,
        artifact_json={"question": "What is 2+2?", "answer": "4"},
        sources=[
            MagicMock(
                license_status="government_open",
                source_hash="sh-1",
                chunk_hash="ch-1",
                source_document_id="doc-1",
                source_chunk_id="chunk-1",
                source_title="Maths Book",
                source_uri="s3://book.pdf",
                source_role="primary_context",
            )
        ],

    )

    service._candidates = AsyncMock(return_value=[art1])

    manifest = await service.create_manifest(
        dataset_version="v2.0",
        scope_ids=["scope_1"],
        languages=["en"],
        created_by="admin_1",
        require_published=False,
        min_quality_score=0.8,
        min_caps_alignment_score=0.8,
        policy_version="1.0",
        rubric_version="1.0",
    )
    assert manifest.dataset_version == "v2.0"
    assert manifest.artifact_count == 1
    assert manifest.status == "ready"


    # 4. approve_manifest: not found -> LookupError
    manifest_id = uuid.uuid4()
    db.scalar.return_value = None
    with pytest.raises(LookupError, match="not found"):
        await service.approve_manifest(manifest_id, actor_id="admin_1", decision="approve")

    # approve_manifest: already approved/rejected returns early
    manifest.status = "approved"
    db.scalar.return_value = manifest
    assert (await service.approve_manifest(manifest_id, "admin_1", "approve")) == manifest

    # approve_manifest: decision == reject
    manifest.status = "ready"
    rej_manifest = await service.approve_manifest(manifest_id, "admin_1", decision="reject")
    assert rej_manifest.status == "rejected"

    # approve_manifest: empty entries -> ValueError
    manifest.status = "ready"
    mock_empty_scalars = MagicMock()
    mock_empty_scalars.all.return_value = []
    db.scalars.return_value = mock_empty_scalars
    with pytest.raises(ValueError, match="Cannot approve an empty dataset manifest"):
        await service.approve_manifest(manifest_id, "admin_1", decision="approve")

    # approve_manifest: valid approval
    entry1 = MagicMock(
        spec=TrainingDatasetEntry,
        record_sha256="record_hash_123",
        manifest_id=manifest_id,
        artifact_id=art1.artifact_id,
    )
    mock_entries_scalars = MagicMock()
    mock_entries_scalars.all.return_value = [entry1]
    db.scalars.return_value = mock_entries_scalars

    approved_manifest = await service.approve_manifest(manifest_id, "admin_1", decision="approve")
    assert approved_manifest.status == "approved"
    assert approved_manifest.dataset_sha256 is not None

    # 5. export_manifest: not found -> LookupError
    db.scalar.return_value = None
    with pytest.raises(LookupError, match="not found"):
        await service.export_manifest(manifest_id, "dataset.jsonl")

    # export_manifest: status != approved -> PermissionError
    manifest.status = "draft"
    db.scalar.return_value = manifest
    with pytest.raises(PermissionError, match="Only approved training dataset"):
        await service.export_manifest(manifest_id, "dataset.jsonl")

    # export_manifest: success path
    manifest.status = "approved"
    db.scalar.return_value = manifest

    rec = build_training_record(art1)
    rec_digest = record_sha256(rec)
    entry1.record_sha256 = rec_digest
    manifest.dataset_sha256 = dataset_sha256([rec_digest])

    mock_execute_res = MagicMock()
    mock_execute_res.all.return_value = [(entry1, art1)]
    db.execute.return_value = mock_execute_res

    exported_manifest, out_path = await service.export_manifest(manifest_id, "export.jsonl")
    assert exported_manifest == manifest
    assert out_path.exists()
    assert len(out_path.read_text(encoding="utf-8").strip()) > 0
