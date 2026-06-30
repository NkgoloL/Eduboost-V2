"""Gate 2R.5 retrieval projection facade."""
from __future__ import annotations

from app.services.curriculum.corpus import (
    ActiveCorpusBinding,
    ActiveCorpusRetriever,
    CorpusRetrievalRecord,
    RetrievalHit,
    RetrievalProjection,
    RetrievalProjectionBuilder,
    RetrievalQuery,
    RetrievalResult,
)

__all__ = [
    "ActiveCorpusBinding",
    "ActiveCorpusRetriever",
    "CorpusRetrievalRecord",
    "RetrievalHit",
    "RetrievalProjection",
    "RetrievalProjectionBuilder",
    "RetrievalQuery",
    "RetrievalResult",
]
