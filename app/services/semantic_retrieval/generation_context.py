"""Phase 1 source-context adapter backed by the Phase 2 retrieval corpus."""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.content_generation.prompt_payloads import SourceContextChunk
from app.services.content_generation.source_context import (
    ContentGenerationSourceContextService as LegacyContentGenerationSourceContextService,
)
from app.services.semantic_retrieval.embedding import build_embedding_provider
from app.services.semantic_retrieval.service import SemanticRetrievalService
from app.services.semantic_retrieval.types import RetrievalFilters


@dataclass(frozen=True)
class SemanticSourceContextResult:
    passed: bool
    errors: list[str]
    chunks: list[SourceContextChunk]


class SemanticContentGenerationSourceContextService(
    LegacyContentGenerationSourceContextService
):
    """Resolve source context exclusively from approved retrieval rows."""

    def __init__(
        self,
        min_quality_score: float = 0.5,
        retrieval_service: SemanticRetrievalService | None = None,
    ) -> None:
        self.min_quality_score = min_quality_score
        self._retrieval = retrieval_service or SemanticRetrievalService(
            embedding_provider=build_embedding_provider()
        )

    async def build_context(
        self,
        session: AsyncSession,
        *,
        scope_id: str,
        caps_ref: str,
        limit: int = 8,
        requested_chunk_ids: list[str] | None = None,
        query: str | None = None,
        grade: int | None = None,
        subject_code: str | None = None,
        language: str = "en",
        permission_scope: str = "public",
    ) -> SemanticSourceContextResult:
        filters = RetrievalFilters(
            scope_id=scope_id,
            caps_ref=caps_ref,
            grade=grade,
            subject_code=subject_code,
            language=language,
            permission_scope=permission_scope,
            min_quality_score=self.min_quality_score,
        )
        try:
            if requested_chunk_ids:
                hits = await self._retrieval.fetch_approved_chunks(
                    session,
                    chunk_ids=requested_chunk_ids,
                    filters=filters,
                )
            else:
                result = await self._retrieval.search(
                    session,
                    query=query or f"{caps_ref} {scope_id}",
                    filters=filters,
                    limit=limit,
                )
                hits = result.hits
        except (LookupError, ValueError) as exc:
            return SemanticSourceContextResult(passed=False, errors=[str(exc)], chunks=[])
        except Exception as exc:
            return SemanticSourceContextResult(
                passed=False,
                errors=[f"Semantic retrieval failed: {type(exc).__name__}"],
                chunks=[],
            )

        chunks = [
            SourceContextChunk(
                source_document_id=hit.document_id,
                source_chunk_id=hit.chunk_id,
                text=hit.content,
                source_title=hit.title,
                source_hash=hit.source_hash,
                curriculum_mapping_id=hit.curriculum_mapping_id,
                source_quality_score=hit.quality_score,
                license_status=hit.license_status,
                document_status=hit.document_status,
            )
            for hit in hits
        ]
        if not chunks:
            return SemanticSourceContextResult(
                passed=False,
                errors=["No approved semantic-retrieval source chunks are available."],
                chunks=[],
            )
        return SemanticSourceContextResult(passed=True, errors=[], chunks=chunks)
