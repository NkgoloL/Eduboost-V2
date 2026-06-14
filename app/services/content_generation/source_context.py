"""Build grounded source context for Content Factory generation tasks."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import ContentArtifactSource, ContentGenerationArtifact
from app.services.content_factory import ACCEPTABLE_LICENSE_STATUSES, APPROVED_SOURCE_STATUSES
from app.services.content_generation.prompt_payloads import SourceContextChunk


@dataclass(frozen=True)
class SourceContextResult:
    passed: bool
    errors: list[str]
    chunks: list[SourceContextChunk]


class ContentGenerationSourceContextService:
    def __init__(self, min_quality_score: float = 0.5) -> None:
        self.min_quality_score = min_quality_score

    async def build_context(
        self,
        session: AsyncSession,
        *,
        scope_id: str,
        caps_ref: str,
        limit: int = 8,
        requested_chunk_ids: list[str] | None = None,
    ) -> SourceContextResult:
        query = (
            select(ContentArtifactSource)
            .join(
                ContentGenerationArtifact,
                ContentGenerationArtifact.artifact_id == ContentArtifactSource.artifact_id,
            )
            .where(
                ContentGenerationArtifact.scope_id == scope_id,
                ContentArtifactSource.caps_ref == caps_ref,
            )
        )
        if requested_chunk_ids:
            query = query.where(ContentArtifactSource.source_chunk_id.in_(requested_chunk_ids))
        result = await session.execute(
            query.order_by(ContentArtifactSource.created_at.desc()).limit(limit)
        )
        rows = list(result.scalars().all())
        validated = self.validate_source_rows(rows, caps_ref=caps_ref)
        if requested_chunk_ids:
            found = {str(getattr(row, "source_chunk_id", "")) for row in rows}
            missing = sorted(set(requested_chunk_ids) - found)
            if missing:
                return SourceContextResult(
                    passed=False,
                    errors=[*validated.errors, f"Requested source chunks were not found: {missing}"],
                    chunks=validated.chunks,
                )
        return validated

    def validate_source_rows(self, sources: list[Any], *, caps_ref: str) -> SourceContextResult:
        errors: list[str] = []
        chunks: list[SourceContextChunk] = []
        for source in sources:
            metadata = getattr(source, "source_metadata", None) or {}
            document_status = str(metadata.get("document_status") or "approved").lower()
            license_status = str(getattr(source, "license_status", None) or metadata.get("license_status") or "").lower()
            quality = _quality(source, metadata)
            if document_status not in APPROVED_SOURCE_STATUSES:
                errors.append(f"source {getattr(source, 'source_document_id', 'unknown')} has status {document_status}.")
                continue
            if document_status in {"deprecated", "rejected", "archived"}:
                errors.append(f"source {getattr(source, 'source_document_id', 'unknown')} is not eligible for generation.")
                continue
            if license_status and license_status not in ACCEPTABLE_LICENSE_STATUSES:
                errors.append(f"source {getattr(source, 'source_document_id', 'unknown')} has incompatible license {license_status}.")
                continue
            if quality is not None and quality < self.min_quality_score:
                errors.append(f"source {getattr(source, 'source_document_id', 'unknown')} quality is below threshold.")
                continue
            if not getattr(source, "source_chunk_id", None):
                errors.append(f"source {getattr(source, 'source_document_id', 'unknown')} has no chunk id.")
                continue
            chunks.append(
                SourceContextChunk(
                    source_document_id=str(getattr(source, "source_document_id")),
                    source_chunk_id=str(getattr(source, "source_chunk_id")),
                    text=str(metadata.get("chunk_text") or getattr(source, "citation_text", None) or getattr(source, "source_title", None) or caps_ref),
                    source_title=getattr(source, "source_title", None),
                    source_hash=getattr(source, "source_hash", None),
                    curriculum_mapping_id=getattr(source, "curriculum_mapping_id", None),
                    source_quality_score=quality,
                    license_status=license_status or None,
                    document_status=document_status,
                )
            )
        if not chunks:
            errors.append("No approved/indexed/training_ready ETL source chunks are available.")
        return SourceContextResult(passed=not errors and bool(chunks), errors=errors, chunks=chunks)


def source_rows_for_chunks(chunks: list[SourceContextChunk], *, caps_ref: str, grade: int, subject_code: str, language: str) -> list[dict[str, Any]]:
    return [
        {
            "source_document_id": chunk.source_document_id,
            "source_chunk_id": chunk.source_chunk_id,
            "source_title": chunk.source_title,
            "citation_text": chunk.text,
            "caps_ref": caps_ref,
            "grade": grade,
            "subject_code": subject_code,
            "language": language,
            "license_status": chunk.license_status,
            "source_quality_score": chunk.source_quality_score,
            "source_hash": chunk.source_hash or f"source:{uuid.uuid5(uuid.NAMESPACE_URL, chunk.source_document_id + ':' + chunk.source_chunk_id)}",
            "curriculum_mapping_id": chunk.curriculum_mapping_id,
            "document_status": chunk.document_status,
            "chunk_quality_score": chunk.source_quality_score,
        }
        for chunk in chunks
    ]


def _quality(source: Any, metadata: dict[str, Any]) -> float | None:
    value = getattr(source, "source_quality_score", None)
    if value is None:
        value = metadata.get("source_quality_score") or metadata.get("chunk_quality_score")
    return float(value) if value is not None else None
