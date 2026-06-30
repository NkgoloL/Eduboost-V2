from __future__ import annotations

import asyncio
import os
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentLayer,
    ContentReviewAction,
    ContentReviewDecision,
)
from app.services.content_artifact_lifecycle import ContentArtifactLifecycleService
from app.services.content_review_governance import (
    ContentReviewGovernanceService,
    ReviewConflictError,
    ReviewGovernancePolicy,
)
from app.services.semantic_retrieval.embedding import DeterministicEmbeddingProvider
from app.services.semantic_retrieval.indexing import (
    RetrievalIndexingService,
    SourceChunkInput,
    SourceDocumentInput,
)
from app.services.semantic_retrieval.service import SemanticRetrievalService
from app.services.semantic_retrieval.types import RetrievalFilters

DATABASE_URL = os.getenv("PHASE3_TEST_DATABASE_URL", "")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="PHASE3_TEST_DATABASE_URL must point to a disposable pgvector PostgreSQL database.",
)

PASSING_RUBRIC = {
    "caps_alignment": True,
    "factual_accuracy": True,
    "answer_key_correctness": True,
    "grade_suitability": True,
    "language_quality": True,
    "cultural_appropriateness": True,
    "bias_and_safety": True,
    "accessibility_and_clarity": True,
    "source_grounding": True,
    "personal_information": True,
}


@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await session.execute(
            text(
                """
                TRUNCATE content_state_transition_events,
                         content_review_decisions,
                         content_review_assignments,
                         content_artifact_reviews,
                         content_validation_reports,
                         content_artifact_sources,
                         content_generation_artifacts,
                         content_generation_tasks,
                         content_generation_runs,
                         retrieval_source_chunks,
                         retrieval_source_documents
                CASCADE
                """
            )
        )
        await session.commit()
    yield factory
    await engine.dispose()


async def seed_artifact(factory, *, creator: str = "creator", language: str = "en") -> uuid.UUID:
    artifact_id = uuid.uuid4()
    async with factory() as session:
        artifact = ContentGenerationArtifact(
            artifact_id=artifact_id,
            scope_id="g4-math",
            content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
            artifact_type=ContentArtifactType.DIAGNOSTIC_ITEM,
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="MATH",
            language=language,
            status=ContentArtifactStatus.PENDING_REVIEW,
            artifact_json={
                "question_text": "What is the value of 5 in 5 432?",
                "options": ["5", "50", "500", "5 000"],
                "answer_key": {"correct_answer": "5 000"},
                "explanation": "The digit is in the thousands place.",
                "safety_status": "passed",
            },
            artifact_hash=f"sha256:{artifact_id.hex}",
            source_snapshot_hash="sha256:source",
            created_by_actor_id=creator,
            review_policy_version="phase3-v1",
            rubric_version="1.0",
            publication_eligible=False,
        )
        session.add(artifact)
        session.add(
            ContentArtifactSource(
                artifact_id=artifact_id,
                source_document_id="caps-grade4-math",
                source_chunk_id="whole-numbers",
                caps_ref="4.M.1.1",
                grade=4,
                subject_code="MATH",
                language=language,
                license_status="government_open",
                source_quality_score=0.95,
                document_version_id="2026.1",
                chunk_hash="sha256:chunk",
                curriculum_mapping_id="map-whole",
                source_hash="sha256:source",
                source_metadata={
                    "document_status": "approved",
                    "license_status": "government_open",
                    "caps_ref": "4.M.1.1",
                },
            )
        )
        await session.commit()
    return artifact_id


async def assign(factory, artifact_id: uuid.UUID, reviewers: list[str]) -> None:
    service = ContentReviewGovernanceService(policy=ReviewGovernancePolicy())
    competencies = {reviewers[0]: ["subject", "caps"]}
    for reviewer in reviewers[1:]:
        competencies[reviewer] = ["general"]
    async with factory() as session:
        await service.assign_reviewers(
            session,
            artifact_id=artifact_id,
            reviewer_ids=reviewers,
            assigned_by="curriculum-lead",
            reviewer_competencies=competencies,
        )
        await session.commit()


async def approve(factory, artifact_id: uuid.UUID, reviewer: str, key: str):
    service = ContentReviewGovernanceService(policy=ReviewGovernancePolicy())
    async with factory() as session:
        result = await service.submit_decision(
            session,
            artifact_id=artifact_id,
            reviewer_id=reviewer,
            action=ContentReviewAction.APPROVE,
            rubric_results=PASSING_RUBRIC,
            idempotency_key=key,
            expected_version=1,
        )
        await session.commit()
        return result


@pytest.mark.asyncio
async def test_three_distinct_approvals_reach_quorum(session_factory) -> None:
    artifact_id = await seed_artifact(session_factory)
    await assign(session_factory, artifact_id, ["r1", "r2", "r3"])
    one = await approve(session_factory, artifact_id, "r1", "decision-r1")
    two = await approve(session_factory, artifact_id, "r2", "decision-r2")
    three = await approve(session_factory, artifact_id, "r3", "decision-r3")
    assert one.current_status == "pending_review"
    assert two.current_status == "pending_review"
    assert three.current_status == "approved"
    assert three.approval_count == 3
    async with session_factory() as session:
        artifact = await session.get(ContentGenerationArtifact, artifact_id)
        assert artifact is not None
        assert artifact.status == ContentArtifactStatus.APPROVED
        assert artifact.publication_eligible is True
        assert artifact.answer_key_verified is True


@pytest.mark.asyncio
async def test_creator_self_review_and_duplicate_decision_are_blocked(session_factory) -> None:
    artifact_id = await seed_artifact(session_factory, creator="creator")
    await assign(session_factory, artifact_id, ["r1", "r2", "r3"])
    service = ContentReviewGovernanceService(policy=ReviewGovernancePolicy())
    async with session_factory() as session:
        with pytest.raises(PermissionError, match="creators"):
            await service.submit_decision(
                session,
                artifact_id=artifact_id,
                reviewer_id="creator",
                action=ContentReviewAction.APPROVE,
                rubric_results=PASSING_RUBRIC,
                idempotency_key="creator-decision",
                expected_version=1,
            )
    first = await approve(session_factory, artifact_id, "r1", "same-key-r1")
    async with session_factory() as session:
        replay = await service.submit_decision(
            session,
            artifact_id=artifact_id,
            reviewer_id="r1",
            action=ContentReviewAction.APPROVE,
            rubric_results=PASSING_RUBRIC,
            idempotency_key="same-key-r1",
            expected_version=1,
        )
        assert replay.decision_id == first.decision_id
        assert replay.idempotent_replay is True
        with pytest.raises(ReviewConflictError, match="already submitted"):
            await service.submit_decision(
                session,
                artifact_id=artifact_id,
                reviewer_id="r1",
                action=ContentReviewAction.APPROVE,
                rubric_results=PASSING_RUBRIC,
                idempotency_key="different-key-r1",
                expected_version=1,
            )


@pytest.mark.asyncio
async def test_concurrent_final_approvals_do_not_overcount(session_factory) -> None:
    artifact_id = await seed_artifact(session_factory)
    reviewers = ["r1", "r2", "r3", "r4"]
    await assign(session_factory, artifact_id, reviewers)
    await approve(session_factory, artifact_id, "r1", "concurrent-r1")
    await approve(session_factory, artifact_id, "r2", "concurrent-r2")

    results = await asyncio.gather(
        approve(session_factory, artifact_id, "r3", "concurrent-r3"),
        approve(session_factory, artifact_id, "r4", "concurrent-r4"),
        return_exceptions=True,
    )
    assert sum(not isinstance(item, Exception) for item in results) == 1
    assert any(isinstance(item, ReviewConflictError) for item in results)
    async with session_factory() as session:
        artifact = await session.get(ContentGenerationArtifact, artifact_id)
        assert artifact is not None
        assert artifact.approval_count == 3
        assert artifact.status == ContentArtifactStatus.APPROVED
        decisions = list(
            (
                await session.scalars(
                    select(ContentReviewDecision).where(
                        ContentReviewDecision.artifact_id == artifact_id
                    )
                )
            ).all()
        )
        assert len(decisions) == 3


@pytest.mark.asyncio
async def test_rejection_quarantine_and_revision_are_fail_closed(session_factory) -> None:
    artifact_id = await seed_artifact(session_factory)
    await assign(session_factory, artifact_id, ["r1", "r2", "r3"])
    service = ContentReviewGovernanceService(policy=ReviewGovernancePolicy())
    async with session_factory() as session:
        result = await service.submit_decision(
            session,
            artifact_id=artifact_id,
            reviewer_id="r1",
            action=ContentReviewAction.REQUEST_CHANGES,
            rubric_results={},
            idempotency_key="request-changes-r1",
            expected_version=1,
            reason_code="factual_correction",
            comments="Correct the place-value explanation.",
        )
        await session.commit()
        assert result.current_status == "revision_required"
    async with session_factory() as session:
        revision = await service.create_revision(
            session,
            artifact_id=artifact_id,
            actor_id="editor",
            artifact_json={
                "question_text": "What is the value of 6 in 6 432?",
                "options": ["6", "60", "600", "6 000"],
                "answer_key": {"correct_answer": "6 000"},
                "explanation": "The digit is in the thousands place.",
                "safety_status": "passed",
            },
            reason="Apply reviewer correction.",
            expected_version=1,
        )
        await session.commit()
        assert revision.version_number == 2
        original = await session.get(ContentGenerationArtifact, artifact_id)
        assert original is not None
        assert original.status == ContentArtifactStatus.SUPERSEDED
        revised = await session.get(ContentGenerationArtifact, revision.new_artifact_id)
        assert revised is not None
        assert revised.approval_count == 0
        assert revised.publication_eligible is False


@pytest.mark.asyncio
async def test_append_only_audit_triggers_reject_mutation(session_factory) -> None:
    artifact_id = await seed_artifact(session_factory)
    await assign(session_factory, artifact_id, ["r1", "r2", "r3"])
    result = await approve(session_factory, artifact_id, "r1", "append-only-r1")
    async with session_factory() as session:
        with pytest.raises(Exception, match="append-only"):
            await session.execute(
                text(
                    "UPDATE content_review_decisions SET comments='tampered' WHERE decision_id=:id"
                ),
                {"id": result.decision_id},
            )
            await session.commit()
        await session.rollback()


@pytest.mark.asyncio
async def test_publication_requires_promotion_and_quorum(session_factory) -> None:
    artifact_id = await seed_artifact(session_factory)
    await assign(session_factory, artifact_id, ["r1", "r2", "r3"])
    await approve(session_factory, artifact_id, "r1", "publish-r1")
    await approve(session_factory, artifact_id, "r2", "publish-r2")
    await approve(session_factory, artifact_id, "r3", "publish-r3")
    lifecycle = ContentArtifactLifecycleService()
    governance = ContentReviewGovernanceService(policy=ReviewGovernancePolicy())
    async with session_factory() as session:
        await lifecycle.mark_seeded_staging(session, artifact_id, "release-manager")
        await lifecycle.mark_promoted_production(session, artifact_id, "release-manager")
        artifact = await governance.publish_artifact(
            session,
            artifact_id=artifact_id,
            actor_id="curriculum-lead",
            expected_version=1,
            reason="Release-approved educator content.",
        )
        await session.commit()
        assert artifact.status == ContentArtifactStatus.PUBLISHED
        assert artifact.published_at is not None


@pytest.mark.asyncio
async def test_phase2_retrieval_excludes_unpublished_generated_artifacts(session_factory) -> None:
    provider = DeterministicEmbeddingProvider()
    indexing = RetrievalIndexingService(embedding_provider=provider)
    async with session_factory() as session:
        await indexing.upsert_document(
            session,
            document=SourceDocumentInput(
                document_id="generated-pending",
                document_version_id="v1",
                title="Generated pending artifact",
                scope_id="g4-math",
                caps_ref="4.M.1.1",
                grade=4,
                subject_code="MATH",
                language="en",
                status="approved",
                permission_scope="public",
                license_status="government_open",
                quality_score=1.0,
                metadata={"artifact_status": "pending_review"},
            ),
            chunks=[
                SourceChunkInput(
                    chunk_id="pending-generated-chunk",
                    chunk_index=0,
                    content="whole numbers place value unpublished artifact",
                    metadata={"artifact_status": "pending_review"},
                )
            ],
        )
        await indexing.upsert_document(
            session,
            document=SourceDocumentInput(
                document_id="generated-published",
                document_version_id="v1",
                title="Generated published artifact",
                scope_id="g4-math",
                caps_ref="4.M.1.1",
                grade=4,
                subject_code="MATH",
                language="en",
                status="approved",
                permission_scope="public",
                license_status="government_open",
                quality_score=1.0,
                metadata={"artifact_status": "published"},
            ),
            chunks=[
                SourceChunkInput(
                    chunk_id="published-generated-chunk",
                    chunk_index=0,
                    content="whole numbers place value published artifact",
                    metadata={"artifact_status": "published"},
                )
            ],
        )
        await session.commit()
        result = await SemanticRetrievalService(embedding_provider=provider).search(
            session,
            query="whole numbers place value",
            filters=RetrievalFilters(scope_id="g4-math", caps_ref="4.M.1.1"),
            limit=10,
        )
        ids = {hit.chunk_id for hit in result.hits}
        assert "published-generated-chunk" in ids
        assert "pending-generated-chunk" not in ids


@pytest.mark.asyncio
async def test_phase3_schema_and_append_only_objects_exist(session_factory) -> None:
    async with session_factory() as session:
        head = await session.scalar(text("SELECT version_num FROM alembic_version"))
        assert head is not None  # head moves forward as phases are added
        tables = {
            row[0]
            for row in (
                await session.execute(
                    text(
                        "SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename LIKE 'content_%'"
                    )
                )
            ).all()
        }
        assert "content_review_decisions" in tables
        assert "content_state_transition_events" in tables
