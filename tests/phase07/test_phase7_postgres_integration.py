from __future__ import annotations

import os
import uuid
from types import SimpleNamespace

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
)
from app.domain.content_coverage import ContentLayer
from app.models.curriculum_expansion import TrainingDatasetEntry, TrainingDatasetManifest
from app.services.curriculum_expansion import TrainingDatasetGovernanceService


DATABASE_URL = os.getenv("PHASE7_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="PHASE7_TEST_DATABASE_URL is required")


def _published_status():
    return getattr(ContentArtifactStatus, "PUBLISHED", ContentArtifactStatus.APPROVED)


@pytest.fixture
async def session():
    engine = create_async_engine(DATABASE_URL)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as db:
        yield db
        await db.rollback()
    await engine.dispose()


@pytest.mark.asyncio
async def test_phase7_schema_and_triggers_exist(session):
    tables = {
        row[0]
        for row in (
            await session.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema='public' AND (table_name LIKE '%training_dataset%' "
                    "OR table_name IN ('curriculum_coverage_snapshots','curriculum_expansion_runs'))"
                )
            )
        ).all()
    }
    assert "training_dataset_manifests" in tables
    assert "training_dataset_entries" in tables
    triggers = {
        row[0]
        for row in (
            await session.execute(
                text(
                    "SELECT tgname FROM pg_trigger "
                    "WHERE NOT tgisinternal AND tgname LIKE 'trg_phase7_%'"
                )
            )
        ).all()
    }
    assert "trg_phase7_dataset_entry_immutable" in triggers
    assert "trg_phase7_approved_manifest_immutable" in triggers


@pytest.mark.asyncio
async def test_manifest_selects_only_published_eligible_artifacts_and_is_immutable(session):
    eligible = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="grade4_mathematics_en",
        content_layer=ContentLayer.LESSONS,
        artifact_type=ContentArtifactType.LESSON,
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="M",
        language="en",
        status=_published_status(),
        artifact_json={"title": "Whole numbers", "summary": "CAPS aligned."},
        artifact_hash="a" * 64,
        source_snapshot_hash="s" * 64,
        quality_score=0.95,
        safety_status="approved",
        caps_alignment_score=0.95,
    )
    eligible.sources.append(
        ContentArtifactSource(
            source_document_id="caps-g4-maths",
            source_chunk_id="chunk-1",
            license_status="government_open",
            source_hash="h" * 64,
            source_role="primary_context",
            source_metadata={},
        )
    )
    excluded = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="grade4_mathematics_en",
        content_layer=ContentLayer.LESSONS,
        artifact_type=ContentArtifactType.LESSON,
        caps_ref="4.M.1.2",
        grade=4,
        subject_code="M",
        language="en",
        status=ContentArtifactStatus.GENERATED,
        artifact_json={"title": "Not reviewed"},
        artifact_hash="b" * 64,
        source_snapshot_hash="t" * 64,
        quality_score=0.99,
        safety_status="approved",
        caps_alignment_score=0.99,
    )
    excluded.sources.append(
        ContentArtifactSource(
            source_document_id="caps-g4-maths",
            source_chunk_id="chunk-2",
            license_status="government_open",
            source_hash="i" * 64,
            source_role="primary_context",
            source_metadata={},
        )
    )
    session.add_all([eligible, excluded])
    await session.flush()

    service = TrainingDatasetGovernanceService(session)
    manifest = await service.create_manifest(
        dataset_version=f"phase7-test-{uuid.uuid4().hex}",
        scope_ids=["grade4_mathematics_en"],
        languages=["en"],
        created_by="admin-test",
        require_published=True,
        min_quality_score=0.8,
        min_caps_alignment_score=0.8,
        policy_version="phase7-training-v1",
        rubric_version="phase3-review-v1",
    )
    assert manifest.artifact_count == 1
    await service.approve_manifest(manifest.manifest_id, "curriculum-lead", "approve")
    await session.commit()

    manifest_id = manifest.manifest_id
    entries = list(
        (
            await session.execute(
                text(
                    "SELECT artifact_id FROM training_dataset_entries "
                    "WHERE manifest_id=:manifest_id"
                ),
                {"manifest_id": manifest_id},
            )
        ).all()
    )
    assert entries == [(eligible.artifact_id,)]

    with pytest.raises(DBAPIError):
        await session.execute(
            text(
                "UPDATE training_dataset_entries SET language='af' "
                "WHERE manifest_id=:manifest_id"
            ),
            {"manifest_id": manifest_id},
        )
        await session.flush()
    await session.rollback()

    with pytest.raises(DBAPIError):
        await session.execute(
            text(
                "UPDATE training_dataset_manifests SET dataset_version=dataset_version || '-changed' "
                "WHERE manifest_id=:manifest_id"
            ),
            {"manifest_id": manifest_id},
        )
        await session.flush()
    await session.rollback()
