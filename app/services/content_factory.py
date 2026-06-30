"""Content Factory services.

The service keeps generated artifacts separate from ETL source-document
governance while enforcing that every approvable artifact can cite approved
source material.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content_factory import (
    ContentArtifactReview,
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentReviewAction,
    ContentValidationReport,
)

APPROVED_SOURCE_STATUSES = {"approved", "indexed", "training_ready"}
ACCEPTABLE_LICENSE_STATUSES = {"government_open", "open_license", "public_domain", "cc_by", "cc_by_sa"}


@dataclass(frozen=True)
class SourceGateResult:
    passed: bool
    errors: list[str]
    source_snapshot_hash: str | None


@dataclass(frozen=True)
class ArtifactProvenanceReport:
    artifact_id: uuid.UUID
    passed: bool
    errors: list[str]
    source_snapshot_hash: str | None
    sources: list[dict[str, Any]]


def stable_json_hash(payload: Any) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


class ETLProvenanceService:
    """Validates source bundles exported from the ETL control plane."""

    def validate_source_bundle(
        self,
        *,
        caps_ref: str | None,
        sources: list[dict[str, Any]],
        min_sources: int = 1,
        require_approved_documents: bool = True,
        allow_synthetic_without_source: bool = False,
    ) -> SourceGateResult:
        if not sources:
            if allow_synthetic_without_source:
                return SourceGateResult(True, [], None)
            return SourceGateResult(False, ["At least one ETL source citation is required."], None)

        errors: list[str] = []
        cited_source_count = 0
        snapshot_inputs: list[dict[str, Any]] = []

        for index, source in enumerate(sources):
            label = f"sources[{index}]"
            document_id = source.get("source_document_id")
            chunk_id = source.get("source_chunk_id")
            if not document_id:
                errors.append(f"{label}.source_document_id is required.")
            if not chunk_id:
                errors.append(f"{label}.source_chunk_id is required.")

            status = str(source.get("document_status") or "").lower()
            if require_approved_documents and status not in APPROVED_SOURCE_STATUSES:
                errors.append(
                    f"{label} document must be approved, indexed, or training_ready; got {status or 'missing'}."
                )

            license_status = str(source.get("license_status") or "").lower()
            if license_status and license_status not in ACCEPTABLE_LICENSE_STATUSES:
                errors.append(f"{label} has incompatible license_status {license_status}.")

            mapping_caps_ref = source.get("caps_ref")
            if caps_ref and mapping_caps_ref and mapping_caps_ref != caps_ref:
                errors.append(f"{label}.caps_ref {mapping_caps_ref} does not match artifact caps_ref {caps_ref}.")

            quality = source.get("chunk_quality_score")
            if quality is not None and float(quality) < 0.5:
                errors.append(f"{label}.chunk_quality_score must be at least 0.5.")

            if document_id and chunk_id:
                cited_source_count += 1
                snapshot_inputs.append(
                    {
                        "source_document_id": document_id,
                        "source_chunk_id": chunk_id,
                        "curriculum_mapping_id": source.get("curriculum_mapping_id"),
                        "source_hash": source.get("source_hash"),
                    }
                )

        if cited_source_count < min_sources:
            errors.append(f"Artifact requires at least {min_sources} cited ETL source(s).")

        source_snapshot_hash = stable_json_hash(snapshot_inputs) if snapshot_inputs else None
        return SourceGateResult(not errors, errors, source_snapshot_hash)


class ContentValidationService:
    """Runs lightweight, deterministic gates before human review."""

    def __init__(self, provenance_service: ETLProvenanceService | None = None) -> None:
        self.provenance_service = provenance_service or ETLProvenanceService()

    def validate_artifact_payload(
        self,
        *,
        artifact_json: dict[str, Any],
        caps_ref: str | None,
        sources: list[dict[str, Any]],
        artifact_type: str,
        min_sources: int = 1,
    ) -> dict[str, Any]:
        errors: list[str] = []
        checks: dict[str, Any] = {}

        if not artifact_json:
            errors.append("artifact_json must not be empty.")
        checks["schema_present"] = bool(artifact_json)

        if artifact_type == "diagnostic_item" and not artifact_json.get("answer_key"):
            errors.append("diagnostic_item artifacts require answer_key.")
        checks["answer_key_verified"] = artifact_type != "diagnostic_item" or bool(artifact_json.get("answer_key"))

        gate = self.provenance_service.validate_source_bundle(
            caps_ref=caps_ref,
            sources=sources,
            min_sources=min_sources,
        )
        errors.extend(gate.errors)
        checks["source_traceability"] = gate.passed

        safety_status = str(artifact_json.get("safety_status") or "passed").lower()
        if safety_status not in {"passed", "safe", "approved"}:
            errors.append(f"safety_status must be passed/safe/approved; got {safety_status}.")
        checks["safety_status"] = safety_status

        return {
            "passed": not errors,
            "errors": errors,
            "checks": checks,
            "source_snapshot_hash": gate.source_snapshot_hash,
        }


class ContentFactoryService:
    def __init__(self, validation_service: ContentValidationService | None = None) -> None:
        self.validation_service = validation_service or ContentValidationService()

    async def create_artifact(
        self,
        session: AsyncSession,
        *,
        payload: dict[str, Any],
    ) -> ContentGenerationArtifact:
        sources = payload.pop("sources", [])
        validation = self.validation_service.validate_artifact_payload(
            artifact_json=payload["artifact_json"],
            caps_ref=payload.get("caps_ref"),
            sources=sources,
            artifact_type=payload["artifact_type"],
            min_sources=payload.pop("min_sources", 1),
        )
        artifact_hash = stable_json_hash(payload["artifact_json"])
        artifact = ContentGenerationArtifact(
            artifact_id=uuid.uuid4(),
            artifact_hash=artifact_hash,
            source_snapshot_hash=validation["source_snapshot_hash"],
            status=(
                ContentArtifactStatus.PENDING_REVIEW
                if validation["passed"]
                else ContentArtifactStatus.VALIDATION_FAILED
            ),
            **payload,
        )
        session.add(artifact)
        await session.flush()

        for source in sources:
            explicit_keys = {
                "source_document_id", "source_chunk_id", "source_title", "source_type", "source_uri",
                "citation_text", "caps_ref", "grade", "subject_code", "language", "license_status",
                "source_quality_score", "chunk_quality_score", "etl_version", "document_version_id",
                "chunk_hash", "curriculum_mapping_id", "source_hash", "source_role",
            }
            session.add(
                ContentArtifactSource(
                    artifact_id=artifact.artifact_id,
                    source_document_id=source["source_document_id"],
                    source_chunk_id=source.get("source_chunk_id"),
                    source_title=source.get("source_title"),
                    source_type=source.get("source_type"),
                    source_uri=source.get("source_uri"),
                    citation_text=source.get("citation_text"),
                    caps_ref=source.get("caps_ref"),
                    grade=source.get("grade"),
                    subject_code=source.get("subject_code"),
                    language=source.get("language"),
                    license_status=source.get("license_status"),
                    source_quality_score=source.get("source_quality_score") or source.get("chunk_quality_score"),
                    etl_version=source.get("etl_version"),
                    document_version_id=source.get("document_version_id"),
                    chunk_hash=source.get("chunk_hash"),
                    curriculum_mapping_id=source.get("curriculum_mapping_id"),
                    source_hash=source.get("source_hash"),
                    source_role=source.get("source_role") or "primary_context",
                    source_metadata={key: value for key, value in source.items() if key not in explicit_keys},
                )
            )

        session.add(
            ContentValidationReport(
                artifact_id=artifact.artifact_id,
                passed=validation["passed"],
                checks=validation["checks"],
                errors=validation["errors"],
            )
        )
        await session.flush()
        return artifact

    async def validate_existing_artifact(self, session: AsyncSession, artifact_id: uuid.UUID) -> ContentValidationReport:
        artifact = await self._get_artifact(session, artifact_id)
        sources = [
            {
                "source_document_id": source.source_document_id,
                "source_chunk_id": source.source_chunk_id,
                "curriculum_mapping_id": source.curriculum_mapping_id,
                "source_hash": source.source_hash,
                **(source.source_metadata or {}),
            }
            for source in artifact.sources
        ]
        validation = self.validation_service.validate_artifact_payload(
            artifact_json=artifact.artifact_json,
            caps_ref=artifact.caps_ref,
            sources=sources,
            artifact_type=_enum_value(artifact.artifact_type),
        )
        artifact.source_snapshot_hash = validation["source_snapshot_hash"]
        artifact.status = (
            ContentArtifactStatus.PENDING_REVIEW
            if validation["passed"]
            else ContentArtifactStatus.VALIDATION_FAILED
        )
        report = ContentValidationReport(
            artifact_id=artifact.artifact_id,
            passed=validation["passed"],
            checks=validation["checks"],
            errors=validation["errors"],
        )
        session.add(report)
        await session.flush()
        return report

    async def review_artifact(
        self,
        session: AsyncSession,
        *,
        artifact_id: uuid.UUID,
        reviewer_id: str | None,
        review_action: ContentReviewAction,
        review_reason: str | None = None,
        quality_score: float | None = None,
    ) -> ContentArtifactReview:
        artifact = await self._get_artifact(session, artifact_id)
        review_action = ContentReviewAction(review_action)
        if (
            review_action is ContentReviewAction.APPROVE
            and _enum_value(artifact.status) != ContentArtifactStatus.PENDING_REVIEW.value
        ):
            raise ValueError("Only pending_review artifacts can be approved.")
        if review_action is ContentReviewAction.APPROVE and not artifact.sources:
            raise ValueError("Cannot approve artifact without ETL source citations.")

        artifact.status = {
            ContentReviewAction.APPROVE: ContentArtifactStatus.APPROVED,
            ContentReviewAction.REJECT: ContentArtifactStatus.REJECTED,
            ContentReviewAction.QUARANTINE: ContentArtifactStatus.QUARANTINED,
            ContentReviewAction.REQUEST_CHANGES: ContentArtifactStatus.VALIDATION_FAILED,
        }[review_action]
        review = ContentArtifactReview(
            artifact_id=artifact.artifact_id,
            reviewer_id=reviewer_id,
            review_action=review_action,
            review_reason=review_reason,
            quality_score=quality_score,
        )
        session.add(review)
        await session.flush()
        return review

    async def validate_artifact_sources(self, session: AsyncSession, artifact_id: uuid.UUID) -> SourceGateResult:
        artifact = await self._get_artifact(session, artifact_id)
        sources = [_source_to_bundle_item(source) for source in artifact.sources]
        return self.validation_service.provenance_service.validate_source_bundle(
            caps_ref=artifact.caps_ref,
            sources=sources,
            min_sources=1,
            require_approved_documents=True,
        )

    async def get_artifact_provenance(self, session: AsyncSession, artifact_id: uuid.UUID) -> ArtifactProvenanceReport:
        artifact = await self._get_artifact(session, artifact_id)
        gate = await self.validate_artifact_sources(session, artifact_id)
        return ArtifactProvenanceReport(
            artifact_id=artifact.artifact_id,
            passed=gate.passed,
            errors=gate.errors,
            source_snapshot_hash=gate.source_snapshot_hash,
            sources=[_source_to_bundle_item(source) for source in artifact.sources],
        )

    async def assert_artifact_has_approved_sources(self, session: AsyncSession, artifact_id: uuid.UUID) -> None:
        gate = await self.validate_artifact_sources(session, artifact_id)
        if not gate.passed:
            raise ValueError("Artifact provenance validation failed: " + "; ".join(gate.errors))
    async def get_artifact(self, session: AsyncSession, artifact_id: uuid.UUID) -> ContentGenerationArtifact:
        return await self._get_artifact(session, artifact_id)

    async def _get_artifact(self, session: AsyncSession, artifact_id: uuid.UUID) -> ContentGenerationArtifact:
        result = await session.execute(
            select(ContentGenerationArtifact)
            .options(selectinload(ContentGenerationArtifact.sources))
            .where(ContentGenerationArtifact.artifact_id == artifact_id)
        )
        artifact = result.scalar_one_or_none()
        if artifact is None:
            raise LookupError(f"Artifact {artifact_id} not found.")
        return artifact


def _enum_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _source_to_bundle_item(source: ContentArtifactSource) -> dict[str, Any]:
    metadata = source.source_metadata or {}
    quality = source.source_quality_score
    return {
        "source_document_id": source.source_document_id,
        "source_chunk_id": source.source_chunk_id,
        "source_title": source.source_title,
        "source_type": source.source_type,
        "source_uri": source.source_uri,
        "citation_text": source.citation_text,
        "caps_ref": source.caps_ref or metadata.get("caps_ref"),
        "grade": source.grade,
        "subject_code": source.subject_code,
        "language": source.language,
        "license_status": source.license_status or metadata.get("license_status"),
        "source_quality_score": float(quality) if quality is not None else metadata.get("source_quality_score"),
        "chunk_quality_score": float(quality) if quality is not None else metadata.get("chunk_quality_score"),
        "etl_version": source.etl_version,
        "document_version_id": source.document_version_id,
        "chunk_hash": source.chunk_hash,
        "curriculum_mapping_id": source.curriculum_mapping_id,
        "source_hash": source.source_hash,
        "source_role": source.source_role,
        "document_status": metadata.get("document_status"),
        **metadata,
    }
