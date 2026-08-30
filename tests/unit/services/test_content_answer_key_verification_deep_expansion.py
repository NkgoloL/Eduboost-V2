"""Comprehensive unit tests for ContentAnswerKeyVerificationService validation rules and result models."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock
import pytest

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
    async def test_unsupported_method_raises_value_error(self):
        mock_session = AsyncMock()
        service = ContentAnswerKeyVerificationService()

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

    @pytest.mark.asyncio
    async def test_empty_idempotency_key_raises_value_error(self):
        mock_session = AsyncMock()
        service = ContentAnswerKeyVerificationService()

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

    @pytest.mark.asyncio
    async def test_missing_verification_basis_raises_value_error(self):
        mock_session = AsyncMock()
        service = ContentAnswerKeyVerificationService()

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
                details={},  # missing verification_basis
            )
