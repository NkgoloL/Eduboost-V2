"""Phase 2 semantic retrieval public API."""
from app.services.semantic_retrieval.embedding import (
    AzureOpenAIEmbeddingProvider,
    DeterministicEmbeddingProvider,
    EmbeddingProviderError,
    build_embedding_provider,
)
from app.services.semantic_retrieval.indexing import (
    RetrievalIndexingService,
    SourceChunkInput,
    SourceDocumentInput,
)
from app.services.semantic_retrieval.repository import SemanticRetrievalRepository
from app.services.semantic_retrieval.service import FallbackPolicy, SemanticRetrievalService
from app.services.semantic_retrieval.types import RetrievalFilters, RetrievalHit, RetrievalResult

__all__ = [
    "AzureOpenAIEmbeddingProvider",
    "DeterministicEmbeddingProvider",
    "EmbeddingProviderError",
    "FallbackPolicy",
    "RetrievalFilters",
    "RetrievalHit",
    "RetrievalIndexingService",
    "RetrievalResult",
    "SemanticRetrievalRepository",
    "SemanticRetrievalService",
    "SourceChunkInput",
    "SourceDocumentInput",
    "build_embedding_provider",
]
