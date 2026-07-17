"""PostgreSQL repository for approval-preserving vector and full-text search."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.retrieval import EMBEDDING_DIMENSIONS, vector_literal
from app.services.semantic_retrieval.types import RetrievalFilters, RetrievalHit

_SEARCHABLE_STATUS_SQL = "('approved','indexed','training_ready')"

_COMMON_SELECT = """
    c.chunk_id,
    c.document_id,
    c.document_version_id,
    d.title,
    c.content,
    c.heading,
    c.section_path,
    c.page_start,
    c.page_end,
    c.scope_id,
    c.caps_ref,
    c.grade,
    c.subject_code,
    c.language,
    c.permission_scope,
    d.status AS document_status,
    c.status AS chunk_status,
    d.license_status,
    COALESCE(c.quality_score, d.quality_score) AS quality_score,
    c.source_hash,
    c.chunk_hash,
    c.curriculum_mapping_id,
    c.embedding_model,
    c.embedding_version,
    c.source_metadata
"""

_FILTER_SQL = f"""
    c.status IN {_SEARCHABLE_STATUS_SQL}
    AND d.status IN {_SEARCHABLE_STATUS_SQL}
    AND d.license_status IN ('government_open','open_license','public_domain','cc_by','cc_by_sa')
    AND c.scope_id = :scope_id
    AND (CAST(:caps_ref AS text) IS NULL OR c.caps_ref = CAST(:caps_ref AS text))
    AND (CAST(:grade AS integer) IS NULL OR c.grade = CAST(:grade AS integer))
    AND (CAST(:subject_code AS text) IS NULL OR c.subject_code = CAST(:subject_code AS text))
    AND (CAST(:language AS text) IS NULL OR c.language = CAST(:language AS text))
    AND (c.permission_scope = 'public' OR c.permission_scope = :permission_scope)
    AND (d.permission_scope = 'public' OR d.permission_scope = :permission_scope)
    AND COALESCE(c.quality_score, d.quality_score, 0) >= :min_quality_score
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
"""


class SemanticRetrievalRepository:
    async def semantic_search(
        self,
        session: AsyncSession,
        *,
        query_vector: list[float],
        filters: RetrievalFilters,
        limit: int,
    ) -> list[RetrievalHit]:
        params = _filter_params(filters)
        params.update(
            {
                "query_vector": vector_literal(query_vector),
                "embedding_dim": EMBEDDING_DIMENSIONS,
                "limit": limit,
            }
        )
        sql = text(
            f"""  # nosec B608
            SELECT {_COMMON_SELECT},
                   GREATEST(0.0, LEAST(1.0,
                       1.0 - (c.embedding <=> CAST(:query_vector AS vector))
                   )) AS score
            FROM retrieval_source_chunks c
            JOIN retrieval_source_documents d ON d.document_id = c.document_id
            WHERE {_FILTER_SQL}
              AND c.embedding IS NOT NULL
              AND c.embedding_dim = :embedding_dim
              AND (CAST(:embedding_model AS text) IS NULL OR c.embedding_model = CAST(:embedding_model AS text))
              AND (CAST(:embedding_version AS text) IS NULL OR c.embedding_version = CAST(:embedding_version AS text))
              AND (1.0 - (c.embedding <=> CAST(:query_vector AS vector))) >= :min_semantic_score
            ORDER BY c.embedding <=> CAST(:query_vector AS vector), c.chunk_id
            LIMIT :limit
            """
        )
        result = await session.execute(sql, params)
        return [_row_to_hit(dict(row), "semantic") for row in result.mappings().all()]

    async def full_text_search(
        self,
        session: AsyncSession,
        *,
        query: str,
        filters: RetrievalFilters,
        limit: int,
    ) -> list[RetrievalHit]:
        params = _filter_params(filters)
        params.update({"query": query, "limit": limit})
        document = "to_tsvector('simple', COALESCE(c.heading, '') || ' ' || c.content)"
        tsquery = "websearch_to_tsquery('simple', :query)"
        sql = text(
            f"""  # nosec B608
            SELECT {_COMMON_SELECT},
                   ts_rank_cd({document}, {tsquery}, 32) AS score
            FROM retrieval_source_chunks c
            JOIN retrieval_source_documents d ON d.document_id = c.document_id
            WHERE {_FILTER_SQL}
              AND {document} @@ {tsquery}
            ORDER BY score DESC, c.chunk_id
            LIMIT :limit
            """
        )
        result = await session.execute(sql, params)
        return [_row_to_hit(dict(row), "full_text") for row in result.mappings().all()]

    async def fetch_approved_chunks(
        self,
        session: AsyncSession,
        *,
        chunk_ids: Sequence[str],
        filters: RetrievalFilters,
    ) -> list[RetrievalHit]:
        if not chunk_ids:
            return []
        names = [f"chunk_id_{index}" for index in range(len(chunk_ids))]
        placeholders = ", ".join(f":{name}" for name in names)
        params = _filter_params(filters)
        params.update(dict(zip(names, chunk_ids)))
        sql = text(
            f"""  # nosec B608
            SELECT {_COMMON_SELECT}, 1.0 AS score
            FROM retrieval_source_chunks c
            JOIN retrieval_source_documents d ON d.document_id = c.document_id
            WHERE {_FILTER_SQL}
              AND c.chunk_id IN ({placeholders})
            ORDER BY c.chunk_index, c.chunk_id
            """
        )
        result = await session.execute(sql, params)
        return [_row_to_hit(dict(row), "semantic") for row in result.mappings().all()]

    async def explain_semantic_search(
        self,
        session: AsyncSession,
        *,
        query_vector: list[float],
        filters: RetrievalFilters,
        limit: int = 8,
    ) -> list[str]:
        params = _filter_params(filters)
        params.update(
            {
                "query_vector": vector_literal(query_vector),
                "embedding_dim": EMBEDDING_DIMENSIONS,
                "limit": limit,
            }
        )
        sql = text(
            f"""  # nosec B608
            EXPLAIN (FORMAT TEXT)
            SELECT c.chunk_id
            FROM retrieval_source_chunks c
            JOIN retrieval_source_documents d ON d.document_id = c.document_id
            WHERE {_FILTER_SQL}
              AND c.embedding IS NOT NULL
              AND c.embedding_dim = :embedding_dim
              AND (CAST(:embedding_model AS text) IS NULL OR c.embedding_model = CAST(:embedding_model AS text))
              AND (CAST(:embedding_version AS text) IS NULL OR c.embedding_version = CAST(:embedding_version AS text))
            ORDER BY c.embedding <=> CAST(:query_vector AS vector)
            LIMIT :limit
            """
        )
        result = await session.execute(sql, params)
        return [str(row[0]) for row in result.all()]


    async def explain_hnsw_probe(
        self,
        session: AsyncSession,
        *,
        query_vector: list[float],
        limit: int = 8,
    ) -> list[str]:
        result = await session.execute(
            text(
                """
                EXPLAIN (FORMAT TEXT)
                SELECT chunk_id
                FROM retrieval_source_chunks
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:query_vector AS vector)
                LIMIT :limit
                """
            ),
            {"query_vector": vector_literal(query_vector), "limit": limit},
        )
        return [str(row[0]) for row in result.all()]


def _filter_params(filters: RetrievalFilters) -> dict[str, Any]:
    return {
        "scope_id": filters.scope_id,
        "caps_ref": filters.caps_ref,
        "grade": filters.grade,
        "subject_code": filters.subject_code,
        "language": filters.language,
        "permission_scope": filters.permission_scope,
        "min_quality_score": filters.min_quality_score,
        "min_semantic_score": filters.min_semantic_score,
        "embedding_model": filters.embedding_model,
        "embedding_version": filters.embedding_version,
    }


def _row_to_hit(row: dict[str, Any], mode: str) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=str(row["chunk_id"]),
        document_id=str(row["document_id"]),
        document_version_id=str(row["document_version_id"]),
        title=str(row["title"]),
        content=str(row["content"]),
        heading=row.get("heading"),
        section_path=row.get("section_path"),
        page_start=row.get("page_start"),
        page_end=row.get("page_end"),
        scope_id=str(row["scope_id"]),
        caps_ref=row.get("caps_ref"),
        grade=row.get("grade"),
        subject_code=row.get("subject_code"),
        language=str(row["language"]),
        permission_scope=str(row["permission_scope"]),
        document_status=str(row["document_status"]),
        chunk_status=str(row["chunk_status"]),
        license_status=str(row["license_status"]),
        quality_score=float(row["quality_score"]) if row.get("quality_score") is not None else None,
        source_hash=str(row["source_hash"]),
        chunk_hash=str(row["chunk_hash"]),
        curriculum_mapping_id=row.get("curriculum_mapping_id"),
        score=float(row.get("score") or 0.0),
        retrieval_mode=mode,  # type: ignore[arg-type]
        embedding_model=row.get("embedding_model"),
        embedding_version=row.get("embedding_version"),
        metadata=dict(row.get("source_metadata") or {}),
    )
