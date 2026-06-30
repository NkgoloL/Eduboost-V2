"""Generate assessment blueprints for Content Factory."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import ContentGenerationArtifact, ContentArtifactStatus


@dataclass(frozen=True)
class BlueprintGenerationResult:
    """Result of blueprint generation."""
    artifact_id: uuid.UUID
    status: str
    errors: list[str] = None


class BlueprintGenerator:
    """Generate assessment blueprints."""

    async def generate(
        self,
        session: AsyncSession,
        *,
        scope_id: str,
        caps_ref: str,
        grade: int | None = None,
        subject_code: str | None = None,
        language: str = "en",
        provider: str = "deterministic",
    ) -> BlueprintGenerationResult:
        """Generate an assessment blueprint.

        Args:
            session: Database session
            scope_id: Content scope ID
            caps_ref: CAPS reference
            grade: Grade level
            subject_code: Subject code
            language: Language code
            provider: Generation provider

        Returns:
            BlueprintGenerationResult with artifact ID and status
        """
        artifact_id = uuid.uuid4()

        if provider == "deterministic":
            payload = self._generate_deterministic_blueprint(
                scope_id=scope_id,
                caps_ref=caps_ref,
                grade=grade,
                subject_code=subject_code,
                language=language,
            )
        else:
            # LLM provider would call the actual LLM
            payload = self._generate_deterministic_blueprint(
                scope_id=scope_id,
                caps_ref=caps_ref,
                grade=grade,
                subject_code=subject_code,
                language=language,
            )

        # Validate the blueprint
        validation_errors = self._validate_blueprint(payload, scope_id, caps_ref)

        if validation_errors:
            status = ContentArtifactStatus.VALIDATION_FAILED.value
        else:
            status = ContentArtifactStatus.PENDING_REVIEW.value

        artifact = ContentGenerationArtifact(
            artifact_id=artifact_id,
            scope_id=scope_id,
            content_layer="assessment_blueprints",
            artifact_type="assessment_blueprint",
            caps_ref=caps_ref,
            grade=grade,
            subject_code=subject_code,
            language=language,
            status=status,
            artifact_json=payload,
            artifact_hash=self._compute_hash(payload),
            schema_version="1.0",
        )

        session.add(artifact)
        await session.flush()

        return BlueprintGenerationResult(
            artifact_id=artifact_id,
            status=status,
            errors=validation_errors,
        )

    def _generate_deterministic_blueprint(
        self,
        *,
        scope_id: str,
        caps_ref: str,
        grade: int | None = None,
        subject_code: str | None = None,
        language: str = "en",
    ) -> dict[str, Any]:
        """Generate a deterministic blueprint for testing."""
        return {
            "scope_id": scope_id,
            "caps_ref": caps_ref,
            "grade": grade,
            "subject_code": subject_code,
            "language": language,
            "title": f"Assessment Blueprint for {caps_ref}",
            "assessment_type": "summative",
            "question_mix": {"multiple_choice": 10, "short_answer": 5},
            "cognitive_level_distribution": {"recall": 3, "application": 7, "analysis": 5},
            "linked_diagnostic_item_ids": [],
            "rubric": {"criteria": ["accuracy", "completeness"]},
            "answer_key_policy": "provided",
            "source_chunk_ids": [],
        }

    def _validate_blueprint(self, payload: dict[str, Any], scope_id: str, caps_ref: str) -> list[str]:
        """Validate a blueprint payload."""
        errors = []

        if not payload.get("caps_ref"):
            errors.append("Missing caps_ref")
        if payload.get("caps_ref") != caps_ref:
            errors.append(f"caps_ref mismatch: expected {caps_ref}, got {payload.get('caps_ref')}")

        if not payload.get("assessment_type"):
            errors.append("Missing assessment_type")

        if not payload.get("question_mix"):
            errors.append("Missing question_mix")

        return errors

    def _compute_hash(self, payload: dict[str, Any]) -> str:
        """Compute a hash for the payload."""
        import hashlib
        import json
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()[:64]
