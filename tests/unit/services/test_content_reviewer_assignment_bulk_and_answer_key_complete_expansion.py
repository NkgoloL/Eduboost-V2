"""Comprehensive unit tests covering content reviewer assignment, bulk review, and answer key verification."""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.models.content_factory import (
    ContentAnswerKeyVerification,
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentReviewAssignment,
)
from app.services.content_answer_key_verification import (
    AnswerKeyVerificationResult,
    ContentAnswerKeyVerificationService,
)
from app.services.content_bulk_review import (
    BulkReviewResult,
    ContentBulkReviewService,
    _value,
)
from app.services.content_reviewer_assignment import (
    ContentReviewerAssignmentService,
    ReviewerWorkload,
)


# ============================================================================
# ContentReviewerAssignmentService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_reviewer_assignment_service():
    service = ContentReviewerAssignmentService()
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    art_id = uuid.uuid4()
    reviewer_id = "reviewer_alice"
    actor_id = "admin_bob"

    # 1. assign_artifact - artifact not found
    session.get.return_value = None
    with pytest.raises(LookupError, match="not found"):
        await service.assign_artifact(session, art_id, reviewer_id, actor_id)

    # 2. assign_artifact - new assignment
    art = ContentGenerationArtifact(
        artifact_id=art_id,
        version_number=1,
    )
    session.get.return_value = art
    # _reviewer_assignment returns None
    session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

    assignment = await service.assign_artifact(
        session,
        art_id,
        reviewer_id,
        actor_id,
        priority="high",
        due_by=datetime.now(timezone.utc) + timedelta(days=2),
        competencies=["math"],
        idempotency_key="key_1",
    )
    assert isinstance(assignment, ContentReviewAssignment)
    assert assignment.assigned_to == reviewer_id
    assert assignment.status == "assigned"
    session.add.assert_called()

    # 3. assign_artifact - existing assignment open -> update fields
    existing_open = ContentReviewAssignment(
        artifact_id=art_id,
        artifact_version=1,
        assigned_to=reviewer_id,
        status="assigned",
        reviewer_competencies=[],
    )
    session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=existing_open))
    updated_assignment = await service.assign_artifact(
        session,
        art_id,
        reviewer_id,
        actor_id,
        priority="critical",
    )
    assert updated_assignment.priority == "critical"

    # 4. assign_artifact - existing assignment resolved -> error
    existing_resolved = ContentReviewAssignment(
        artifact_id=art_id,
        artifact_version=1,
        assigned_to=reviewer_id,
        status="approved",
    )
    session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=existing_resolved))
    with pytest.raises(ValueError, match="already completed or closed"):
        await service.assign_artifact(session, art_id, reviewer_id, actor_id)

    # 5. assign_batch
    service.assign_artifact = AsyncMock(return_value=assignment)
    batch_res = await service.assign_batch(session, [art_id], reviewer_id, actor_id)
    assert len(batch_res) == 1

    # 6. unassign_artifact - open assignment not found
    orig_open = service._open_assignment
    service._open_assignment = AsyncMock(return_value=None)
    with pytest.raises(LookupError, match="Open assignment .* not found"):
        await service.unassign_artifact(session, art_id, actor_id)

    # unassign_artifact - open assignment cancelled
    service._open_assignment = AsyncMock(return_value=existing_open)
    cancelled = await service.unassign_artifact(session, art_id, actor_id)
    assert cancelled.status == "cancelled"
    service._open_assignment = orig_open

    # 7. get_reviewer_workload
    now = datetime.now(timezone.utc)
    item_assigned = ContentReviewAssignment(
        status="assigned",
        due_by=now + timedelta(days=1),
        assigned_at=now,
        created_at=now,
    )
    item_overdue_dueby = ContentReviewAssignment(
        status="assigned",
        due_by=now - timedelta(days=1),
        assigned_at=now - timedelta(days=2),
        created_at=now - timedelta(days=2),
    )
    item_in_review_old = ContentReviewAssignment(
        status="in_review",
        due_by=None,
        assigned_at=now - timedelta(days=5),
        created_at=now - timedelta(days=5),  # older than 72h default cutoff
    )
    session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[
            item_assigned, item_overdue_dueby, item_in_review_old
        ])))
    )

    workload = await service.get_reviewer_workload(session, reviewer_id)
    assert isinstance(workload, ReviewerWorkload)
    assert workload.assigned == 2
    assert workload.in_review == 1
    assert workload.overdue == 2
    assert workload.total_open == 3

    # 8. list_assignments
    session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[item_assigned])))
    )
    listed = await service.list_assignments(session, reviewer_id=reviewer_id, status="assigned", limit=10)
    assert len(listed) == 1

    # 9. _open_assignment directly
    session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=item_assigned))
    open_found = await service._open_assignment(session, art_id, reviewer_id=reviewer_id)
    assert open_found is item_assigned
    open_any = await service._open_assignment(session, art_id, reviewer_id=None)
    assert open_any is item_assigned




# ============================================================================
# ContentBulkReviewService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_bulk_review_service():
    lifecycle_service = AsyncMock()
    assignment_service = AsyncMock()

    service = ContentBulkReviewService(
        lifecycle_service=lifecycle_service,
        assignment_service=assignment_service,
    )
    session = AsyncMock()

    art_id = uuid.uuid4()
    reviewer_id = "rev_1"

    # 1. bulk_approve is forbidden
    with pytest.raises(ValueError, match="Bulk approval is disabled"):
        await service.bulk_approve(session, [art_id], reviewer_id=reviewer_id, notes="notes")

    # 2. bulk_reject validation errors and success
    with pytest.raises(ValueError, match="requires a reason"):
        await service.bulk_reject(session, [art_id], reviewer_id=reviewer_id, reason="   ")

    with pytest.raises(ValueError, match="limited to"):
        await service.bulk_reject(session, [art_id] * 105, reviewer_id=reviewer_id, reason="too many")

    lifecycle_service.reject_artifact.return_value = MagicMock(artifact_id=art_id)
    rej_res = await service.bulk_reject(session, [art_id], reviewer_id=reviewer_id, reason="low quality")
    assert isinstance(rej_res, BulkReviewResult)
    assert rej_res.status == "rejected"
    assert rej_res.summary["rejected"] == 1

    # 3. bulk_quarantine validation errors and success
    with pytest.raises(ValueError, match="requires a reason"):
        await service.bulk_quarantine(session, [art_id], reviewer_id=reviewer_id, reason="")

    lifecycle_service.quarantine_artifact.return_value = MagicMock(artifact_id=art_id)
    quar_res = await service.bulk_quarantine(session, [art_id], reviewer_id=reviewer_id, reason="toxic content")
    assert isinstance(quar_res, BulkReviewResult)
    assert quar_res.status == "quarantined"
    assert quar_res.summary["quarantined"] == 1

    # 4. bulk_assign
    assignment_service.assign_batch.return_value = [MagicMock(artifact_id=art_id)]
    assign_res = await service.bulk_assign(session, [art_id], reviewer_id=reviewer_id, assigned_by="admin")
    assert isinstance(assign_res, BulkReviewResult)
    assert assign_res.status == "assigned"

    assert _value(MagicMock(value="val")) == "val"
    assert _value("val") == "val"


# ============================================================================
# ContentAnswerKeyVerificationService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_answer_key_verification_service():
    service = ContentAnswerKeyVerificationService()
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    art_id = uuid.uuid4()
    verif_id = uuid.uuid4()

    # 1. latest_for_artifact
    mock_verif = ContentAnswerKeyVerification(
        verification_id=verif_id,
        artifact_id=art_id,
        artifact_version=1,
        artifact_hash="hash1",
        method="deterministic_recompute",
        passed=True,
    )
    session.scalar.return_value = mock_verif
    art = ContentGenerationArtifact(
        artifact_id=art_id,
        version_number=1,
        artifact_hash="hash1",
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
        status=ContentArtifactStatus.APPROVED,
    )
    assert await service.latest_for_artifact(session, art) == mock_verif

    # 2. record input validation: unsupported method, empty idempotency key, passed without verification_basis
    with pytest.raises(ValueError, match="Unsupported answer-key verification method"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="invalid_method",
            passed=True,
            verifier_actor_id="actor1",
            idempotency_key="key1",
            details={},
        )

    with pytest.raises(ValueError, match="idempotency key is required"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="deterministic_recompute",
            passed=True,
            verifier_actor_id="actor1",
            idempotency_key="   ",
            details={"verification_basis": "recomputed"},
        )

    with pytest.raises(ValueError, match="verification_basis"):
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

    # 3. record idempotency replay (same artifact vs different artifact)
    existing_same = ContentAnswerKeyVerification(
        verification_id=verif_id,
        artifact_id=art_id,
        artifact_version=1,
        artifact_hash="hash1",
        method="deterministic_recompute",
        passed=True,
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
        details={"verification_basis": "ok"},
    )
    assert isinstance(replay_res, AnswerKeyVerificationResult)
    assert replay_res.idempotent_replay is True

    existing_diff = ContentAnswerKeyVerification(
        verification_id=verif_id,
        artifact_id=uuid.uuid4(),
    )
    session.scalar.return_value = existing_diff
    with pytest.raises(ValueError, match="already used for another artifact"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="deterministic_recompute",
            passed=True,
            verifier_actor_id="actor1",
            idempotency_key="key1",
            details={"verification_basis": "ok"},
        )

    # 4. record artifact checks: not found, version mismatch, hash mismatch, wrong layer
    session.scalar.side_effect = [None, None]  # idempotency check None, artifact query None
    with pytest.raises(LookupError, match="not found"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="deterministic_recompute",
            passed=True,
            verifier_actor_id="actor1",
            idempotency_key="key1",
            details={"verification_basis": "ok"},
        )

    # Version mismatch
    art_ver2 = ContentGenerationArtifact(
        artifact_id=art_id,
        version_number=2,
        artifact_hash="hash1",
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
    )
    session.scalar.side_effect = [None, art_ver2]
    with pytest.raises(ValueError, match="Artifact version changed"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="deterministic_recompute",
            passed=True,
            verifier_actor_id="actor1",
            idempotency_key="key1",
            details={"verification_basis": "ok"},
        )

    # Hash mismatch
    art_hash_diff = ContentGenerationArtifact(
        artifact_id=art_id,
        version_number=1,
        artifact_hash="hash_different",
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
    )
    session.scalar.side_effect = [None, art_hash_diff]
    with pytest.raises(ValueError, match="Artifact hash changed"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="deterministic_recompute",
            passed=True,
            verifier_actor_id="actor1",
            idempotency_key="key1",
            details={"verification_basis": "ok"},
        )

    # Non-diagnostic layer
    art_lesson = ContentGenerationArtifact(
        artifact_id=art_id,
        version_number=1,
        artifact_hash="hash1",
        content_layer="lessons",
        artifact_type="lesson",
    )
    session.scalar.side_effect = [None, art_lesson]
    with pytest.raises(ValueError, match="applies only to diagnostic items"):
        await service.record(
            session,
            artifact_id=art_id,
            expected_version=1,
            expected_artifact_hash="hash1",
            method="deterministic_recompute",
            passed=True,
            verifier_actor_id="actor1",
            idempotency_key="key1",
            details={"verification_basis": "ok"},
        )

    # 5. Clean successful record on approved artifact
    session.scalar.side_effect = [None, art]
    res_rec = await service.record(
        session,
        artifact_id=art_id,
        expected_version=1,
        expected_artifact_hash="hash1",
        method="deterministic_recompute",
        passed=True,
        verifier_actor_id="actor1",
        idempotency_key="key_clean",
        details={"verification_basis": "recomputed"},
    )
    assert res_rec.passed is True
    assert art.answer_key_verified is True
    assert art.publication_eligible is True
