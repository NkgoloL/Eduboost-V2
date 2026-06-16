"""Independent answer-key verification boundary for governed diagnostic content."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import (
    ContentAnswerKeyVerification,
    ContentArtifactStatus,
    ContentGenerationArtifact,
)

_ALLOWED_METHODS = {
    "deterministic_recompute",
    "independent_model",
    "educator_recalculation",
}


@dataclass(frozen=True)
class AnswerKeyVerificationResult:
    verification_id: uuid.UUID
    artifact_id: uuid.UUID
    artifact_version: int
    artifact_hash: str
    method: str
    passed: bool
    idempotent_replay: bool = False


class ContentAnswerKeyVerificationService:
    """Records append-only evidence and updates the current artifact gate."""

    async def latest_for_artifact(
        self,
        session: AsyncSession,
        artifact: ContentGenerationArtifact,
    ) -> ContentAnswerKeyVerification | None:
        return await session.scalar(
            select(ContentAnswerKeyVerification)
            .where(
                ContentAnswerKeyVerification.artifact_id == artifact.artifact_id,
                ContentAnswerKeyVerification.artifact_version == artifact.version_number,
                ContentAnswerKeyVerification.artifact_hash == artifact.artifact_hash,
            )
            .order_by(
                ContentAnswerKeyVerification.created_at.desc(),
                ContentAnswerKeyVerification.verification_id.desc(),
            )
            .limit(1)
        )

    async def record(
        self,
        session: AsyncSession,
        *,
        artifact_id: uuid.UUID,
        expected_version: int,
        expected_artifact_hash: str,
        method: str,
        passed: bool,
        verifier_actor_id: str,
        idempotency_key: str,
        details: dict[str, Any],
        verifier_provider: str | None = None,
        verifier_model: str | None = None,
    ) -> AnswerKeyVerificationResult:
        method = method.strip().lower()
        if method not in _ALLOWED_METHODS:
            raise ValueError(f"Unsupported answer-key verification method: {method}")
        if not idempotency_key.strip():
            raise ValueError("An idempotency key is required.")
        if passed and not details.get("verification_basis"):
            raise ValueError("Passing verification requires details.verification_basis.")

        existing = await session.scalar(
            select(ContentAnswerKeyVerification).where(
                ContentAnswerKeyVerification.verifier_actor_id == verifier_actor_id,
                ContentAnswerKeyVerification.idempotency_key == idempotency_key,
            )
        )
        if existing is not None:
            if existing.artifact_id != artifact_id:
                raise ValueError("Idempotency key was already used for another artifact.")
            return AnswerKeyVerificationResult(
                verification_id=existing.verification_id,
                artifact_id=existing.artifact_id,
                artifact_version=existing.artifact_version,
                artifact_hash=existing.artifact_hash,
                method=existing.method,
                passed=existing.passed,
                idempotent_replay=True,
            )

        artifact = await session.scalar(
            select(ContentGenerationArtifact)
            .where(ContentGenerationArtifact.artifact_id == artifact_id)
            .with_for_update()
        )
        if artifact is None:
            raise LookupError(f"Artifact {artifact_id} not found.")
        if int(artifact.version_number or 1) != int(expected_version):
            raise ValueError("Artifact version changed before answer-key verification.")
        if artifact.artifact_hash != expected_artifact_hash:
            raise ValueError("Artifact hash changed before answer-key verification.")
        layer = str(getattr(artifact.content_layer, "value", artifact.content_layer))
        artifact_type = str(getattr(artifact.artifact_type, "value", artifact.artifact_type))
        if layer != "diagnostic_items" and artifact_type != "diagnostic_item":
            raise ValueError("Answer-key verification applies only to diagnostic items.")

        verification = ContentAnswerKeyVerification(
            artifact_id=artifact.artifact_id,
            artifact_version=int(artifact.version_number or 1),
            artifact_hash=artifact.artifact_hash,
            method=method,
            passed=bool(passed),
            verifier_actor_id=verifier_actor_id,
            verifier_provider=verifier_provider,
            verifier_model=verifier_model,
            details=details,
            idempotency_key=idempotency_key,
        )
        session.add(verification)
        artifact.answer_key_verified = bool(passed)
        if str(getattr(artifact.status, "value", artifact.status)) in {
            ContentArtifactStatus.APPROVED.value,
            ContentArtifactStatus.PROMOTED_PRODUCTION.value,
        }:
            artifact.publication_eligible = bool(passed)
        await session.flush()
        return AnswerKeyVerificationResult(
            verification_id=verification.verification_id,
            artifact_id=artifact.artifact_id,
            artifact_version=int(artifact.version_number or 1),
            artifact_hash=artifact.artifact_hash,
            method=method,
            passed=bool(passed),
        )
