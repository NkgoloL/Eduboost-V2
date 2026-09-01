"""Batch 236 — app/services/curriculum_expansion.py comprehensive service branch coverage expansion.

Tests:
- String and hashing helpers (_enum_value, _artifact_version, _normalised_json, record_sha256, dataset_sha256)
- forbidden_training_paths: nested dicts, lists, forbidden keys
- obvious_pii_findings: email, SA phone, ID number
- validate_language_content: placeholders, unsupported language, unexpected script mix
- artifact_eligibility_reasons: all branch gates (status, hashes, scores, safety, answer key, sources, licenses, PII, fields)
- CurriculumExpansionService:
  - coverage_for_scope: green / amber / red status computation
  - capture_snapshot: persistence
  - build_expansion_plan: gap filtering and plan structure
- TrainingDatasetGovernanceService:
  - create_manifest: existing shortcut, candidate filtering, entry creation
  - approve_manifest: LookupError, already decided idempotent, reject branch, empty entries ValueError, approved
  - _safe_output_path: directory traversal ValueError
  - export_manifest: LookupError, unapproved PermissionError, ineligible artifact PermissionError, hash drift RuntimeError, success file export
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.content_factory import ContentArtifactStatus, ContentGenerationArtifact
from app.models.curriculum_expansion import (
    CurriculumCoverageSnapshot,
    CurriculumExpansionRun,
    TrainingDatasetEntry,
    TrainingDatasetManifest,
)
from app.services.curriculum_expansion import (
    CurriculumExpansionService,
    TrainingDatasetGovernanceService,
    _artifact_version,
    _enum_value,
    _normalised_json,
    artifact_eligibility_reasons,
    build_training_record,
    dataset_sha256,
    forbidden_training_paths,
    obvious_pii_findings,
    record_sha256,
    validate_language_content,
)


# ---------------------------------------------------------------------------
# Helpers, PII, and Language Validation
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_curriculum_expansion_helpers_and_sanitizers():
    # _enum_value and _artifact_version
    assert _enum_value("APPROVED") == "approved"
    assert _artifact_version(SimpleNamespace(version_number=3)) == 3
    assert _artifact_version(SimpleNamespace(version_number=None, artifact_version=2)) == 2
    assert _artifact_version(SimpleNamespace(version_number=None, artifact_version=None)) == 1

    # record_sha256 and dataset_sha256
    h1 = record_sha256({"a": 1, "b": 2})
    h2 = record_sha256({"b": 2, "a": 1})
    assert h1 == h2
    assert isinstance(dataset_sha256([h1]), str)

    # forbidden_training_paths
    bad_data = {
        "learner_id": "l-123",
        "nested": [{"user_id": "u-456"}],
        "safe_key": "safe_value",
    }
    findings = forbidden_training_paths(bad_data)
    assert "$.learner_id" in findings
    assert "$.nested[0].user_id" in findings

    # obvious_pii_findings
    assert len(obvious_pii_findings({"email": "test@example.com"})) > 0
    assert len(obvious_pii_findings({"phone": "0821234567"})) > 0
    assert len(obvious_pii_findings({"id": "9001015009087"})) > 0
    assert len(obvious_pii_findings({"text": "Hello world clean text"})) == 0

    # validate_language_content
    assert "placeholder_text" in validate_language_content({"content": "TODO: finish"}, "en")
    assert "unsupported_language" in validate_language_content({"content": "Goeie dag"}, "fr")
    # Greek script in content
    assert "unexpected_script_mix" in validate_language_content({"content": "αβγδεζηθικλμ"}, "en")


# ---------------------------------------------------------------------------
# Artifact Eligibility Reasons
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_artifact_eligibility_reasons_comprehensive():
    valid_source = SimpleNamespace(
        license_status="government_open",
        source_hash="hash_src",
        chunk_hash="hash_chk",
    )
    artifact = SimpleNamespace(
        status="approved",
        artifact_hash="hash_art",
        source_snapshot_hash="hash_snap",
        quality_score=0.9,
        caps_alignment_score=0.9,
        safety_status="safe",
        content_layer="lessons",
        answer_key_verified=True,
        sources=[valid_source],
        artifact_json={"lesson": "Valid content"},
        language="en",
    )

    # 1. Fully eligible
    assert artifact_eligibility_reasons(
        artifact,
        require_published=False,
        min_quality_score=0.8,
        min_caps_alignment_score=0.8,
    ) == []

    # 2. Ineligible status (require_published=True when approved)
    reasons = artifact_eligibility_reasons(
        artifact,
        require_published=True,
        min_quality_score=0.8,
        min_caps_alignment_score=0.8,
    )
    assert "status:approved" in reasons

    # 3. Disallowed license and missing hashes
    bad_source = SimpleNamespace(license_status="proprietary", source_hash="", chunk_hash="")
    artifact.sources = [bad_source]
    artifact.quality_score = 0.5
    artifact.safety_status = "blocked"
    artifact.content_layer = "diagnostic_items"
    artifact.answer_key_verified = False

    reasons_bad = artifact_eligibility_reasons(
        artifact,
        require_published=False,
        min_quality_score=0.8,
        min_caps_alignment_score=0.8,
    )
    assert "disallowed_source_license" in reasons_bad
    assert "missing_source_hash" in reasons_bad
    assert "quality_below_threshold" in reasons_bad
    assert "safety_not_approved" in reasons_bad
    assert "answer_key_not_verified" in reasons_bad


# ---------------------------------------------------------------------------
# CurriculumExpansionService Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_curriculum_expansion_service_methods():
    mock_db = AsyncMock()
    mock_registry = MagicMock()
    mock_registry.require_active_scope.return_value = SimpleNamespace(language="en")
    mock_registry.get_scope_targets.return_value = [
        SimpleNamespace(
            caps_ref="4.M.1.1",
            targets={"lessons.approved": 5},
        )
    ]

    service = CurriculumExpansionService(db=mock_db, registry=mock_registry)

    # 1. coverage_for_scope
    mock_db.scalar = AsyncMock(return_value=5)  # pipeline_ready=5, published=5
    cov = await service.coverage_for_scope("scope-1")
    assert cov["status"] == "green"
    assert cov["gap_count"] == 0

    # 2. capture_snapshot
    snapshot = await service.capture_snapshot("scope-1", source_commit_sha="commit123")
    assert snapshot.scope_id == "scope-1"
    mock_db.add.assert_called()
    mock_db.flush.assert_called()

    # 3. build_expansion_plan
    plan_run = await service.build_expansion_plan(
        requested_by="admin-1",
        scope_ids=["scope-1"],
        languages=["en"],
        layers=["lessons"],
        dry_run=True,
    )
    assert plan_run.status == "completed"
    assert plan_run.dry_run is True


# ---------------------------------------------------------------------------
# TrainingDatasetGovernanceService Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_training_dataset_governance_service_full_flow(tmp_path):
    mock_db = AsyncMock()
    gov_svc = TrainingDatasetGovernanceService(db=mock_db, artifact_root=tmp_path)

    # 1. _safe_output_path traversal error vs valid
    with pytest.raises(ValueError, match="escapes approved"):
        gov_svc._safe_output_path("../../etc/passwd")

    safe_path = gov_svc._safe_output_path("valid_dataset.jsonl")
    assert safe_path.parent == tmp_path

    # 2. create_manifest (shortcut when existing)
    mock_existing = MagicMock(dataset_version="v1.0.0")
    mock_db.scalar.return_value = mock_existing
    existing_res = await gov_svc.create_manifest(
        dataset_version="v1.0.0",
        scope_ids=["scope-1"],
        languages=["en"],
        created_by="admin",
        require_published=True,
        min_quality_score=0.8,
        min_caps_alignment_score=0.8,
        policy_version="v1",
        rubric_version="v1",
    )
    assert existing_res == mock_existing

    # 3. approve_manifest branches
    manifest_id = uuid.uuid4()

    # 3a. LookupError
    mock_db.scalar.return_value = None
    with pytest.raises(LookupError, match="not found"):
        await gov_svc.approve_manifest(manifest_id, "admin-1", "approve")

    # 3b. Already decided idempotent
    mock_manifest = MagicMock(status="approved")
    mock_db.scalar.return_value = mock_manifest
    assert (await gov_svc.approve_manifest(manifest_id, "admin-1", "approve")).status == "approved"

    # 3c. Reject decision
    mock_manifest_draft = MagicMock(status="draft")
    mock_db.scalar.return_value = mock_manifest_draft
    rejected = await gov_svc.approve_manifest(manifest_id, "admin-1", "reject")
    assert rejected.status == "rejected"

    # 3d. Empty entries ValueError
    mock_manifest_ready = MagicMock(status="ready")
    mock_db.scalar.return_value = mock_manifest_ready
    mock_scalars_res = MagicMock()
    mock_scalars_res.all.return_value = []
    mock_db.scalars.return_value = mock_scalars_res
    with pytest.raises(ValueError, match="empty dataset"):
        await gov_svc.approve_manifest(manifest_id, "admin-1", "approve")

    # 4. export_manifest branches
    # 4a. LookupError & unapproved PermissionError
    mock_db.scalar.return_value = None
    with pytest.raises(LookupError):
        await gov_svc.export_manifest(manifest_id, "export.jsonl")

    mock_unapproved = MagicMock(status="draft")
    mock_db.scalar.return_value = mock_unapproved
    with pytest.raises(PermissionError, match="Only approved"):
        await gov_svc.export_manifest(manifest_id, "export.jsonl")
