"""Generate study-plan templates for Content Factory."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import ContentGenerationArtifact, ContentArtifactStatus


@dataclass(frozen=True)
class StudyPlanTemplateGenerationResult:
    """Result of study-plan template generation."""
    artifact_id: uuid.UUID
    status: str
    errors: list[str] = None


class StudyPlanTemplateGenerator:
    """Generate study-plan templates."""

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
    ) -> StudyPlanTemplateGenerationResult:
        """Generate a study-plan template.

        Args:
            session: Database session
            scope_id: Content scope ID
            caps_ref: CAPS reference
            grade: Grade level
            subject_code: Subject code
            language: Language code
            provider: Generation provider

        Returns:
            StudyPlanTemplateGenerationResult with artifact ID and status
        """
        artifact_id = uuid.uuid4()

        if provider == "deterministic":
            payload = self._generate_deterministic_template(
                scope_id=scope_id,
                caps_ref=caps_ref,
                grade=grade,
                subject_code=subject_code,
                language=language,
            )
        else:
            # LLM provider would call the actual LLM
            payload = self._generate_deterministic_template(
                scope_id=scope_id,
                caps_ref=caps_ref,
                grade=grade,
                subject_code=subject_code,
                language=language,
            )

        # Validate the template
        validation_errors = self._validate_template(payload, scope_id, caps_ref)

        if validation_errors:
            status = ContentArtifactStatus.VALIDATION_FAILED.value
        else:
            status = ContentArtifactStatus.PENDING_REVIEW.value

        artifact = ContentGenerationArtifact(
            artifact_id=artifact_id,
            scope_id=scope_id,
            content_layer="study_plan_templates",
            artifact_type="study_plan_template",
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

        return StudyPlanTemplateGenerationResult(
            artifact_id=artifact_id,
            status=status,
            errors=validation_errors,
        )

    def _generate_deterministic_template(
        self,
        *,
        scope_id: str,
        caps_ref: str,
        grade: int | None = None,
        subject_code: str | None = None,
        language: str = "en",
    ) -> dict[str, Any]:
        """Generate a deterministic template for testing."""
        return {
            "scope_id": scope_id,
            "caps_ref": caps_ref,
            "grade": grade,
            "subject_code": subject_code,
            "language": language,
            "title": f"Study Plan Template for {caps_ref}",
            "diagnostic_trigger_conditions": {"score_below": 60},
            "recommended_lesson_ids": [],
            "practice_item_ids": [],
            "remediation_steps": ["review_concepts", "practice_exercises"],
            "extension_steps": ["advanced_problems", "real_world_applications"],
            "estimated_minutes": 45,
            "source_chunk_ids": [],
        }

    def _validate_template(self, payload: dict[str, Any], scope_id: str, caps_ref: str) -> list[str]:
        """Validate a template payload."""
        errors = []

        if not payload.get("caps_ref"):
            errors.append("Missing caps_ref")
        if payload.get("caps_ref") != caps_ref:
            errors.append(f"caps_ref mismatch: expected {caps_ref}, got {payload.get('caps_ref')}")

        if not payload.get("diagnostic_trigger_conditions"):
            errors.append("Missing diagnostic_trigger_conditions")

        if not payload.get("estimated_minutes"):
            errors.append("Missing estimated_minutes")

        return errors

    def _compute_hash(self, payload: dict[str, Any]) -> str:
        """Compute a hash for the payload."""
        import hashlib
        import json
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()[:64]
