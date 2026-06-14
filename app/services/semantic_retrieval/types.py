"""Typed contracts for Phase 2 semantic retrieval."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RetrievalFilters(BaseModel):
    """Mandatory server-side retrieval filters.

    Search never accepts an arbitrary status list: the repository always restricts
    results to approved/indexed/training-ready rows. Optional fields only narrow
    that already-safe corpus.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    scope_id: str = Field(min_length=1, max_length=80)
    caps_ref: str | None = Field(default=None, max_length=80)
    grade: int | None = Field(default=None, ge=0, le=12)
    subject_code: str | None = Field(default=None, max_length=20)
    language: str | None = Field(default="en", min_length=2, max_length=8)
    permission_scope: str = Field(default="public", min_length=1, max_length=80)
    min_quality_score: float = Field(default=0.5, ge=0, le=1)
    min_semantic_score: float = Field(default=0.15, ge=-1, le=1)
    embedding_model: str | None = Field(default=None, max_length=120)
    embedding_version: str | None = Field(default=None, max_length=80)

    @field_validator("scope_id", "caps_ref", "subject_code", "language", "permission_scope", mode="before")
    @classmethod
    def strip_strings(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


@dataclass(frozen=True)
class RetrievalHit:
    chunk_id: str
    document_id: str
    document_version_id: str
    title: str
    content: str
    heading: str | None
    section_path: str | None
    page_start: int | None
    page_end: int | None
    scope_id: str
    caps_ref: str | None
    grade: int | None
    subject_code: str | None
    language: str
    permission_scope: str
    document_status: str
    chunk_status: str
    license_status: str
    quality_score: float | None
    source_hash: str
    chunk_hash: str
    curriculum_mapping_id: str | None
    score: float
    retrieval_mode: Literal["semantic", "full_text"]
    embedding_model: str | None = None
    embedding_version: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def provenance(self) -> dict[str, Any]:
        return {
            "source_document_id": self.document_id,
            "source_chunk_id": self.chunk_id,
            "source_title": self.title,
            "citation_text": self.content,
            "caps_ref": self.caps_ref,
            "grade": self.grade,
            "subject_code": self.subject_code,
            "language": self.language,
            "license_status": self.license_status,
            "source_quality_score": self.quality_score,
            "source_hash": self.source_hash,
            "chunk_hash": self.chunk_hash,
            "document_version_id": self.document_version_id,
            "curriculum_mapping_id": self.curriculum_mapping_id,
            "document_status": self.document_status,
            "chunk_status": self.chunk_status,
            "retrieval_mode": self.retrieval_mode,
            "retrieval_score": self.score,
            "embedding_model": self.embedding_model,
            "embedding_version": self.embedding_version,
        }


@dataclass(frozen=True)
class RetrievalResult:
    query_fingerprint: str
    mode: Literal["semantic", "full_text"]
    hits: list[RetrievalHit]
    fallback_reason: str | None
    embedding_model: str | None
    embedding_version: str | None
    elapsed_ms: float


class EvaluationCase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    query: str
    expected_chunk_ids: frozenset[str]
    filters: RetrievalFilters
    k: int = Field(default=5, ge=1, le=20)


@dataclass(frozen=True)
class EvaluationMetrics:
    case_count: int
    recall_at_k: float
    mean_reciprocal_rank: float
    precision_at_k: float
    unsafe_hit_count: int
    passed: bool
    thresholds: dict[str, float]
    case_results: list[dict[str, Any]]
