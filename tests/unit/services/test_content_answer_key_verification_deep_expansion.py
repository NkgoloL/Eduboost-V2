"""Comprehensive unit tests for ContentAnswerKeyVerificationService validation rules, replay, and record flows."""
from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.models.content_factory import (
    ContentAnswerKeyVerification,
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentLayer,
)
from app.services.content_answer_key_verification import (
    _ALLOWED_METHODS,
    AnswerKeyVerificationResult,
    ContentAnswerKeyVerificationService,
)


class TestAnswerKeyVerificationModels:
    def test_allowed_methods_set(self):
        assert "deterministic_recompute" in _ALLOWED_METHODS
        assert "independent_model" in _ALLOWED_METHODS
        assert "educator_recalculation" in _ALLOWED_METHODS

    def test_verification_result_dataclass(self):
        vid = uuid.uuid4()
        aid = uuid.uuid4()
        res = AnswerKeyVerificationResult(
            verification_id=vid,
            artifact_id=aid,
            artifact_version=1,
            artifact_hash="hash-123",
            method="deterministic_recompute",
            passed=True,
            idempotent_replay=False,
        )
        assert res.verification_id == vid
        assert res.artifact_id == aid
        assert res.passed is True
        assert res.method == "deterministic_recompute"


class TestContentAnswerKeyVerificationServiceValidation:
    @pytest.mark.asyncio
    async def test_unsupported_method_and_empty_idempotency_key(self):
        mock_session = AsyncMock()
        service = ContentAnswerKeyVerificationService()

        # 1. Unsupported method
        with pytest.raises(ValueError, match="Unsupported answer-key verification method"):
            await service.record(
                session=mock_session,
                artifact_id=uuid.uuid4(),
                expected_version=1,
                expected_artifact_hash="hash-123",
                method="unsupported_method",
                passed=True,
                verifier_actor_id="actor-1",
                idempotency_key="key-12345",
                details={"verification_basis": "verified"},
            )

        # 2. Empty idempotency key
        with pytest.raises(ValueError, match="idempotency key is required"):
            await service.record(
                session=mock_session,
                artifact_id=uuid.uuid4(),
                expected_version=1,
                expected_artifact_hash="hash-123",
                method="deterministic_recompute",
                passed=True,
                verifier_actor_id="actor-1",
                idempotency_key="   ",
                details={"verification_basis": "verified"},
            )

        # 3. Missing verification basis
        with pytest.raises(ValueError, match="Passing verification requires details.verification_basis"):
            await service.record(
                session=mock_session,
                artifact_id=uuid.uuid4(),
                expected_version=1,
                expected_artifact_hash="hash-123",
                method="deterministic_recompute",
                passed=True,
                verifier_actor_id="actor-1",
                idempotency_key="key-12345",
                details={},
            )

    @pytest.mark.asyncio
    async def test_idempotency_and_artifact_validation_branches(self):
        service = ContentAnswerKeyVerificationService()
        session = AsyncMock()
        aid = uuid.uuid4()
        other_aid = uuid.uuid4()

        # 1. Idempotency key reused for different artifact -> ValueError
        existing_other = SimpleNamespace(
            artifact_id=other_aid,
            verification_id=uuid.uuid4(),
            artifact_version=1,
            artifact_hash="hash-123",
            method="deterministic_recompute",
            passed=True,
        )
        session.scalar.side_effect = [existing_other]

        with pytest.raises(ValueError, match="already used for another artifact"):
            await service.record(
                session=session,
                artifact_id=aid,
                expected_version=1,
                expected_artifact_hash="hash-123",
                method="deterministic_recompute",
                passed=True,
                verifier_actor_id="actor-1",
                idempotency_key="key-1",
                details={"verification_basis": "verified"},
            )

        # 2. Idempotent replay for same artifact
        existing_same = SimpleNamespace(
            artifact_id=aid,
            verification_id=uuid.uuid4(),
            artifact_version=1,
            artifact_hash="hash-123",
            method="deterministic_recompute",
            passed=True,
        )
        session.scalar.side_effect = [existing_same]

        replay = await service.record(
            session=session,
            artifact_id=aid,
            expected_version=1,
            expected_artifact_hash="hash-123",
            method="deterministic_recompute",
            passed=True,
            verifier_actor_id="actor-1",
            idempotency_key="key-1",
            details={"verification_basis": "verified"},
        )
        assert replay.idempotent_replay is True
        assert replay.artifact_id == aid

        # 3. Artifact not found -> LookupError
        session.scalar.side_effect = [None, None]  # existing=None, artifact=None
        with pytest.raises(LookupError, match="not found"):
            await service.record(
                session=session,
                artifact_id=aid,
                expected_version=1,
                expected_artifact_hash="hash-123",
                method="deterministic_recompute",
                passed=True,
                verifier_actor_id="actor-1",
                idempotency_key="key-new",
                details={"verification_basis": "verified"},
            )

        # 4. Version mismatch
        mock_art_v2 = SimpleNamespace(
            artifact_id=aid,
            version_number=2,
            artifact_hash="hash-123",
            content_layer="diagnostic_items",
            artifact_type="diagnostic_item",
        )
        session.scalar.side_effect = [None, mock_art_v2]
        with pytest.raises(ValueError, match="version changed"):
            await service.record(
                session=session,
                artifact_id=aid,
                expected_version=1,
                expected_artifact_hash="hash-123",
                method="deterministic_recompute",
                passed=True,
                verifier_actor_id="actor-1",
                idempotency_key="key-new",
                details={"verification_basis": "verified"},
            )

        # 5. Hash mismatch
        mock_art_wrong_hash = SimpleNamespace(
            artifact_id=aid,
            version_number=1,
            artifact_hash="hash-different",
            content_layer="diagnostic_items",
            artifact_type="diagnostic_item",
        )
        session.scalar.side_effect = [None, mock_art_wrong_hash]
        with pytest.raises(ValueError, match="hash changed"):
            await service.record(
                session=session,
                artifact_id=aid,
                expected_version=1,
                expected_artifact_hash="hash-123",
                method="deterministic_recompute",
                passed=True,
                verifier_actor_id="actor-1",
                idempotency_key="key-new",
                details={"verification_basis": "verified"},
            )

        # 6. Non-diagnostic layer
        mock_art_lesson = SimpleNamespace(
            artifact_id=aid,
            version_number=1,
            artifact_hash="hash-123",
            content_layer="lessons",
            artifact_type="lesson",
        )
        session.scalar.side_effect = [None, mock_art_lesson]
        with pytest.raises(ValueError, match="only to diagnostic items"):
            await service.record(
                session=session,
                artifact_id=aid,
                expected_version=1,
                expected_artifact_hash="hash-123",
                method="deterministic_recompute",
                passed=True,
                verifier_actor_id="actor-1",
                idempotency_key="key-new",
                details={"verification_basis": "verified"},
            )

        # 7. Clean successful record
        mock_art_good = SimpleNamespace(
            artifact_id=aid,
            version_number=1,
            artifact_hash="hash-123",
            content_layer="diagnostic_items",
            artifact_type="diagnostic_item",
            status=ContentArtifactStatus.APPROVED,
            answer_key_verified=False,
            publication_eligible=False,
        )
        session.scalar.side_effect = [None, mock_art_good]
        res = await service.record(
            session=session,
            artifact_id=aid,
            expected_version=1,
            expected_artifact_hash="hash-123",
            method="deterministic_recompute",
            passed=True,
            verifier_actor_id="actor-1",
            idempotency_key="key-clean",
            details={"verification_basis": "deterministic formula"},
        )
        assert res.passed is True
        assert mock_art_good.answer_key_verified is True
        assert mock_art_good.publication_eligible is True
        session.add.assert_called()
        session.flush.assert_called()

    @pytest.mark.asyncio
    async def test_latest_for_artifact(self):
        service = ContentAnswerKeyVerificationService()
        session = AsyncMock()
        mock_verification = SimpleNamespace(verification_id=uuid.uuid4())
        session.scalar.return_value = mock_verification

        artifact = SimpleNamespace(
            artifact_id=uuid.uuid4(),
            version_number=1,
            artifact_hash="hash-123",
        )
        latest = await service.latest_for_artifact(session, artifact)
        assert latest == mock_verification
