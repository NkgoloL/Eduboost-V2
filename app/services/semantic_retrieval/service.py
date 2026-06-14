"""Semantic retrieval orchestration with tightly governed fallback."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.semantic_retrieval.embedding import EmbeddingProvider, EmbeddingProviderError
from app.services.semantic_retrieval.repository import SemanticRetrievalRepository
from app.services.semantic_retrieval.types import RetrievalFilters, RetrievalHit, RetrievalResult

log = structlog.get_logger(__name__)


@dataclass(frozen=True)
class FallbackPolicy:
    on_embedding_error: bool = True
    on_vector_error: bool = True
    on_no_vector_hits: bool = True


class SemanticRetrievalService:
    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        repository: SemanticRetrievalRepository | None = None,
        fallback_policy: FallbackPolicy | None = None,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.repository = repository or SemanticRetrievalRepository()
        self.fallback_policy = fallback_policy or FallbackPolicy()

    async def search(
        self,
        session: AsyncSession,
        *,
        query: str,
        filters: RetrievalFilters,
        limit: int = 8,
    ) -> RetrievalResult:
        normalized_query = " ".join(query.split())
        if not normalized_query:
            raise ValueError("Retrieval query must not be empty.")
        if not 1 <= limit <= 20:
            raise ValueError("Retrieval limit must be between 1 and 20.")

        started = time.perf_counter()
        fingerprint = hashlib.sha256(normalized_query.casefold().encode("utf-8")).hexdigest()[:16]
        fallback_reason: str | None = None
        hits: list[RetrievalHit] = []

        try:
            query_vector = await self.embedding_provider.embed_query(normalized_query)
        except EmbeddingProviderError as exc:
            if not self.fallback_policy.on_embedding_error:
                raise
            fallback_reason = f"embedding_unavailable:{type(exc).__name__}"
        else:
            try:
                hits = await self.repository.semantic_search(
                    session,
                    query_vector=query_vector,
                    filters=filters,
                    limit=limit,
                )
            except Exception as exc:
                if not self.fallback_policy.on_vector_error:
                    raise
                fallback_reason = f"vector_query_failed:{type(exc).__name__}"
            if hits:
                elapsed = (time.perf_counter() - started) * 1000
                self._log_result(fingerprint, "semantic", len(hits), elapsed, None, filters)
                return RetrievalResult(
                    query_fingerprint=fingerprint,
                    mode="semantic",
                    hits=hits,
                    fallback_reason=None,
                    embedding_model=self.embedding_provider.model,
                    embedding_version=self.embedding_provider.version,
                    elapsed_ms=elapsed,
                )
            if fallback_reason is None:
                if not self.fallback_policy.on_no_vector_hits:
                    elapsed = (time.perf_counter() - started) * 1000
                    return RetrievalResult(
                        query_fingerprint=fingerprint,
                        mode="semantic",
                        hits=[],
                        fallback_reason=None,
                        embedding_model=self.embedding_provider.model,
                        embedding_version=self.embedding_provider.version,
                        elapsed_ms=elapsed,
                    )
                fallback_reason = "no_vector_hits"

        hits = await self.repository.full_text_search(
            session,
            query=normalized_query,
            filters=filters,
            limit=limit,
        )
        elapsed = (time.perf_counter() - started) * 1000
        self._log_result(fingerprint, "full_text", len(hits), elapsed, fallback_reason, filters)
        return RetrievalResult(
            query_fingerprint=fingerprint,
            mode="full_text",
            hits=hits,
            fallback_reason=fallback_reason,
            embedding_model=self.embedding_provider.model,
            embedding_version=self.embedding_provider.version,
            elapsed_ms=elapsed,
        )

    async def fetch_approved_chunks(
        self,
        session: AsyncSession,
        *,
        chunk_ids: list[str],
        filters: RetrievalFilters,
    ) -> list[RetrievalHit]:
        unique_ids = list(dict.fromkeys(chunk_ids))
        hits = await self.repository.fetch_approved_chunks(
            session,
            chunk_ids=unique_ids,
            filters=filters,
        )
        found = {hit.chunk_id for hit in hits}
        missing = [chunk_id for chunk_id in unique_ids if chunk_id not in found]
        if missing:
            raise LookupError(
                "Requested chunks are missing or fail approval/scope/permission filters: "
                + ", ".join(missing)
            )
        return hits

    @staticmethod
    def _log_result(
        fingerprint: str,
        mode: str,
        count: int,
        elapsed_ms: float,
        fallback_reason: str | None,
        filters: RetrievalFilters,
    ) -> None:
        log.info(
            "semantic_retrieval_completed",
            query_fingerprint=fingerprint,
            mode=mode,
            hit_count=count,
            elapsed_ms=round(elapsed_ms, 3),
            fallback_reason=fallback_reason,
            scope_id=filters.scope_id,
            caps_ref=filters.caps_ref,
            grade=filters.grade,
            subject_code=filters.subject_code,
            language=filters.language,
        )
