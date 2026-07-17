"""Indexing and reindexing services for the approved retrieval corpus."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.retrieval import (
    COMPATIBLE_LICENSE_STATUSES,
    EMBEDDING_DIMENSIONS,
    SEARCHABLE_STATUSES,
    vector_literal,
)
from app.services.semantic_retrieval.embedding import EmbeddingProvider


@dataclass(frozen=True)
class SourceDocumentInput:
    document_id: str
    document_version_id: str
    title: str
    scope_id: str
    caps_ref: str | None
    grade: int | None
    subject_code: str | None
    language: str
    status: str
    permission_scope: str
    license_status: str
    quality_score: float | None
    source_uri: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class SourceChunkInput:
    chunk_id: str
    chunk_index: int
    content: str
    heading: str | None = None
    section_path: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    curriculum_mapping_id: str | None = None
    scope_id: str | None = None
    caps_ref: str | None = None
    grade: int | None = None
    subject_code: str | None = None
    language: str | None = None
    quality_score: float | None = None
    status: str | None = None
    permission_scope: str | None = None
    metadata: dict[str, Any] | None = None


class RetrievalIndexingService:
    def __init__(self, *, embedding_provider: EmbeddingProvider) -> None:
        if embedding_provider.dimensions != EMBEDDING_DIMENSIONS:
            raise ValueError("Embedding provider dimension does not match the Phase 2 schema.")
        self.embedding_provider = embedding_provider

    async def upsert_document(
        self,
        session: AsyncSession,
        *,
        document: SourceDocumentInput,
        chunks: list[SourceChunkInput],
    ) -> int:
        if not chunks:
            raise ValueError("A retrieval document must contain at least one chunk.")
        _validate_document(document)
        source_hash = _stable_hash(
            {
                "document_id": document.document_id,
                "document_version_id": document.document_version_id,
                "title": document.title,
                "scope_id": document.scope_id,
                "caps_ref": document.caps_ref,
                "chunks": [chunk.content for chunk in chunks],
            }
        )
        await session.execute(
            text(
                """
                INSERT INTO retrieval_source_documents (
                    document_id, document_version_id, title, scope_id, caps_ref,
                    grade, subject_code, language, status, permission_scope,
                    license_status, quality_score, source_hash, source_uri,
                    source_metadata, approved_at, updated_at
                ) VALUES (
                    :document_id, :document_version_id, :title, :scope_id, :caps_ref,
                    :grade, :subject_code, :language, :status, :permission_scope,
                    :license_status, :quality_score, :source_hash, :source_uri,
                    CAST(:source_metadata AS jsonb), :approved_at, now()
                )
                ON CONFLICT (document_id) DO UPDATE SET
                    document_version_id = EXCLUDED.document_version_id,
                    title = EXCLUDED.title,
                    scope_id = EXCLUDED.scope_id,
                    caps_ref = EXCLUDED.caps_ref,
                    grade = EXCLUDED.grade,
                    subject_code = EXCLUDED.subject_code,
                    language = EXCLUDED.language,
                    status = EXCLUDED.status,
                    permission_scope = EXCLUDED.permission_scope,
                    license_status = EXCLUDED.license_status,
                    quality_score = EXCLUDED.quality_score,
                    source_hash = EXCLUDED.source_hash,
                    source_uri = EXCLUDED.source_uri,
                    source_metadata = EXCLUDED.source_metadata,
                    approved_at = EXCLUDED.approved_at,
                    updated_at = now()
                """
            ),
            {
                **document.__dict__,
                "source_hash": source_hash,
                "source_metadata": json.dumps(document.metadata or {}, sort_keys=True),
                "approved_at": datetime.now(timezone.utc)
                if document.status in SEARCHABLE_STATUSES
                else None,
            },
        )

        document_searchable = (
            document.status in SEARCHABLE_STATUSES
            and document.license_status in COMPATIBLE_LICENSE_STATUSES
            and _metadata_allows_generated_artifact(document.metadata)
        )
        vectors: list[list[float] | None] = [None] * len(chunks)
        eligible_indexes = [
            index
            for index, chunk in enumerate(chunks)
            if document_searchable
            and (chunk.status or document.status) in SEARCHABLE_STATUSES
            and _metadata_allows_generated_artifact(chunk.metadata)
        ]
        if eligible_indexes:
            embedded = await self.embedding_provider.embed(
                [chunks[index].content for index in eligible_indexes]
            )
            for index, vector in zip(eligible_indexes, embedded, strict=True):
                vectors[index] = vector

        for chunk, vector in zip(chunks, vectors, strict=True):
            await self._upsert_chunk(
                session,
                document=document,
                document_source_hash=source_hash,
                chunk=chunk,
                vector=vector,
            )
        await self._delete_stale_chunks(
            session,
            document_id=document.document_id,
            current_chunk_ids=[chunk.chunk_id for chunk in chunks],
        )
        return len(chunks)

    async def reindex_document(self, session: AsyncSession, *, document_id: str) -> int:
        rows = (
            await session.execute(
                text(
                    """
                    SELECT c.chunk_id, c.content
                    FROM retrieval_source_chunks c
                    JOIN retrieval_source_documents d ON d.document_id = c.document_id
                    WHERE c.document_id = :document_id
                      AND c.status IN ('approved','indexed','training_ready')
                      AND d.status IN ('approved','indexed','training_ready')
                      AND (
                        NOT (
                          c.source_metadata ? 'artifact_status'
                          OR d.source_metadata ? 'artifact_status'
                          OR c.source_metadata ? 'artifact_id'
                          OR d.source_metadata ? 'artifact_id'
                          OR COALESCE(c.source_metadata->>'source_origin', '') IN ('generated','generated_artifact','content_factory')
                          OR COALESCE(d.source_metadata->>'source_origin', '') IN ('generated','generated_artifact','content_factory')
                        )
                        OR COALESCE(c.source_metadata->>'artifact_status', d.source_metadata->>'artifact_status')
                           IN ('published','promoted_production')
                      )
                    ORDER BY c.chunk_index
                    """
                ),
                {"document_id": document_id},
            )
        ).mappings().all()
        if not rows:
            return 0
        vectors = await self.embedding_provider.embed([str(row["content"]) for row in rows])
        for row, vector in zip(rows, vectors):
            await session.execute(
                text(
                    """
                    UPDATE retrieval_source_chunks
                    SET embedding = CAST(:embedding AS vector),
                        embedding_model = :model,
                        embedding_version = :version,
                        embedding_dim = :dimension,
                        indexed_at = now(),
                        updated_at = now()
                    WHERE chunk_id = :chunk_id
                    """
                ),
                {
                    "embedding": vector_literal(vector),
                    "model": self.embedding_provider.model,
                    "version": self.embedding_provider.version,
                    "dimension": EMBEDDING_DIMENSIONS,
                    "chunk_id": row["chunk_id"],
                },
            )
        return len(rows)


    async def _delete_stale_chunks(
        self,
        session: AsyncSession,
        *,
        document_id: str,
        current_chunk_ids: list[str],
    ) -> None:
        names = [f"current_chunk_{index}" for index in range(len(current_chunk_ids))]
        placeholders = ", ".join(f":{name}" for name in names)
        params: dict[str, Any] = {"document_id": document_id}
        params.update(dict(zip(names, current_chunk_ids)))
        await session.execute(
            text(
                f"""  # nosec B608
                DELETE FROM retrieval_source_chunks
                WHERE document_id = :document_id
                  AND chunk_id NOT IN ({placeholders})
                """
            ),
            params,
        )

    async def _upsert_chunk(
        self,
        session: AsyncSession,
        *,
        document: SourceDocumentInput,
        document_source_hash: str,
        chunk: SourceChunkInput,
        vector: list[float] | None,
    ) -> None:
        status = chunk.status or document.status
        permission_scope = chunk.permission_scope or document.permission_scope
        chunk_hash = _stable_hash(
            {
                "document_id": document.document_id,
                "document_version_id": document.document_version_id,
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
            }
        )
        params = {
            "chunk_id": chunk.chunk_id,
            "document_id": document.document_id,
            "document_version_id": document.document_version_id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "heading": chunk.heading,
            "section_path": chunk.section_path,
            "page_start": chunk.page_start,
            "page_end": chunk.page_end,
            "scope_id": chunk.scope_id or document.scope_id,
            "caps_ref": chunk.caps_ref or document.caps_ref,
            "grade": chunk.grade if chunk.grade is not None else document.grade,
            "subject_code": chunk.subject_code or document.subject_code,
            "language": chunk.language or document.language,
            "status": status,
            "permission_scope": permission_scope,
            "quality_score": chunk.quality_score
            if chunk.quality_score is not None
            else document.quality_score,
            "source_hash": document_source_hash,
            "chunk_hash": chunk_hash,
            "curriculum_mapping_id": chunk.curriculum_mapping_id,
            "source_metadata": json.dumps(chunk.metadata or {}, sort_keys=True),
            "embedding": vector_literal(vector) if vector is not None else None,
            "model": self.embedding_provider.model if vector is not None else None,
            "version": self.embedding_provider.version if vector is not None else None,
            "dimension": EMBEDDING_DIMENSIONS if vector is not None else None,
            "indexed_at": datetime.now(timezone.utc) if vector is not None else None,
        }
        embedding_sql = "CAST(:embedding AS vector)" if vector is not None else "NULL"
        await session.execute(
            text(
                f"""  # nosec B608
                INSERT INTO retrieval_source_chunks (
                    chunk_id, document_id, document_version_id, chunk_index,
                    content, heading, section_path, page_start, page_end,
                    scope_id, caps_ref, grade, subject_code, language, status,
                    permission_scope, quality_score, source_hash, chunk_hash,
                    curriculum_mapping_id, embedding_model, embedding_version,
                    embedding_dim, embedding, indexed_at, source_metadata, updated_at
                ) VALUES (
                    :chunk_id, :document_id, :document_version_id, :chunk_index,
                    :content, :heading, :section_path, :page_start, :page_end,
                    :scope_id, :caps_ref, :grade, :subject_code, :language, :status,
                    :permission_scope, :quality_score, :source_hash, :chunk_hash,
                    :curriculum_mapping_id, :model, :version, :dimension,
                    {embedding_sql},
                    :indexed_at,
                    CAST(:source_metadata AS jsonb), now()
                )
                ON CONFLICT (chunk_id) DO UPDATE SET
                    document_id = EXCLUDED.document_id,
                    document_version_id = EXCLUDED.document_version_id,
                    chunk_index = EXCLUDED.chunk_index,
                    content = EXCLUDED.content,
                    heading = EXCLUDED.heading,
                    section_path = EXCLUDED.section_path,
                    page_start = EXCLUDED.page_start,
                    page_end = EXCLUDED.page_end,
                    scope_id = EXCLUDED.scope_id,
                    caps_ref = EXCLUDED.caps_ref,
                    grade = EXCLUDED.grade,
                    subject_code = EXCLUDED.subject_code,
                    language = EXCLUDED.language,
                    status = EXCLUDED.status,
                    permission_scope = EXCLUDED.permission_scope,
                    quality_score = EXCLUDED.quality_score,
                    source_hash = EXCLUDED.source_hash,
                    chunk_hash = EXCLUDED.chunk_hash,
                    curriculum_mapping_id = EXCLUDED.curriculum_mapping_id,
                    embedding_model = EXCLUDED.embedding_model,
                    embedding_version = EXCLUDED.embedding_version,
                    embedding_dim = EXCLUDED.embedding_dim,
                    embedding = EXCLUDED.embedding,
                    indexed_at = EXCLUDED.indexed_at,
                    source_metadata = EXCLUDED.source_metadata,
                    updated_at = now()
                """
            ),
            params,
        )


def _stable_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_document(document: SourceDocumentInput) -> None:
    if not document.document_id or not document.document_version_id:
        raise ValueError("Document and version identifiers are required.")
    if not document.scope_id or not document.title:
        raise ValueError("Document scope and title are required.")
    if document.quality_score is not None and not 0 <= document.quality_score <= 1:
        raise ValueError("Document quality score must be between zero and one.")
    if document.status in SEARCHABLE_STATUSES and not document.license_status:
        raise ValueError("Searchable documents require an approved license status.")


def _metadata_allows_generated_artifact(metadata: dict[str, Any] | None) -> bool:
    """Fail closed when retrieval rows represent generated artifacts.

    Ordinary curriculum sources have no ``artifact_status`` metadata and remain
    eligible. Generated-artifact sources must be promoted or published.
    """
    values = metadata or {}
    status = str(values.get("artifact_status") or "").strip().lower()
    origin = str(values.get("source_origin") or "").strip().lower()
    generated = bool(
        status
        or values.get("artifact_id")
        or origin in {"generated", "generated_artifact", "content_factory"}
    )
    return not generated or status in {"published", "promoted_production"}
