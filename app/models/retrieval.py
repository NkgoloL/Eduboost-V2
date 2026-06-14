"""Canonical PostgreSQL source corpus for semantic retrieval.

The retrieval corpus is independent from generated artifacts. Source documents and
chunks are approved before they become searchable, and every hit carries immutable
version/hash metadata that can be propagated into generated-artifact provenance.
"""
from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import UserDefinedType

from app.core.database import Base

EMBEDDING_DIMENSIONS = 1536
SEARCHABLE_STATUSES = frozenset({"approved", "indexed", "training_ready"})
COMPATIBLE_LICENSE_STATUSES = frozenset(
    {"government_open", "open_license", "public_domain", "cc_by", "cc_by_sa"}
)


class Vector1536(UserDefinedType):
    """Minimal PostgreSQL pgvector type without a runtime pgvector-python dependency.

    Repository queries bind vectors as text and explicitly cast them to ``vector``.
    The ORM type exists for schema metadata and model inspection; application code
    intentionally does not select the raw embedding value.
    """

    cache_ok = True

    def get_col_spec(self, **_: Any) -> str:
        return f"vector({EMBEDDING_DIMENSIONS})"


def vector_literal(values: list[float] | tuple[float, ...]) -> str:
    """Return a validated pgvector input literal."""
    if len(values) != EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Embedding must contain {EMBEDDING_DIMENSIONS} values; received {len(values)}."
        )
    numbers: list[str] = []
    for value in values:
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("Embedding values must be finite numbers.")
        numbers.append(format(number, ".9g"))
    return "[" + ",".join(numbers) + "]"


class RetrievalSourceDocument(Base):
    __tablename__ = "retrieval_source_documents"

    document_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    document_version_id: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    caps_ref: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subject_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False, server_default="en")
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    permission_scope: Mapped[str] = mapped_column(String(80), nullable=False, server_default="public")
    license_status: Mapped[str] = mapped_column(String(80), nullable=False)
    quality_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    source_hash: Mapped[str] = mapped_column(String(120), nullable=False)
    source_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    chunks: Mapped[list["RetrievalSourceChunk"]] = relationship(
        "RetrievalSourceChunk", back_populates="document", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("grade IS NULL OR (grade >= 0 AND grade <= 12)", name="ck_retrieval_documents_grade"),
        CheckConstraint(
            "quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1)",
            name="ck_retrieval_documents_quality",
        ),
        Index(
            "ix_retrieval_documents_filter",
            "scope_id",
            "caps_ref",
            "grade",
            "subject_code",
            "language",
            "status",
        ),
    )


class RetrievalSourceChunk(Base):
    __tablename__ = "retrieval_source_chunks"

    chunk_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("retrieval_source_documents.document_id", ondelete="CASCADE"), nullable=False
    )
    document_version_id: Mapped[str] = mapped_column(String(120), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    heading: Mapped[str | None] = mapped_column(String(300), nullable=True)
    section_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False)
    caps_ref: Mapped[str | None] = mapped_column(String(80), nullable=True)
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subject_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False, server_default="en")
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    permission_scope: Mapped[str] = mapped_column(String(80), nullable=False, server_default="public")
    quality_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    source_hash: Mapped[str] = mapped_column(String(120), nullable=False)
    chunk_hash: Mapped[str] = mapped_column(String(120), nullable=False)
    curriculum_mapping_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    embedding_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    embedding_dim: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedding: Mapped[Any | None] = mapped_column(Vector1536(), nullable=True)
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    document: Mapped[RetrievalSourceDocument] = relationship(
        "RetrievalSourceDocument", back_populates="chunks"
    )

    __table_args__ = (
        CheckConstraint("chunk_index >= 0", name="ck_retrieval_chunks_index"),
        CheckConstraint("grade IS NULL OR (grade >= 0 AND grade <= 12)", name="ck_retrieval_chunks_grade"),
        CheckConstraint(
            "quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1)",
            name="ck_retrieval_chunks_quality",
        ),
        CheckConstraint(
            f"embedding IS NULL OR embedding_dim = {EMBEDDING_DIMENSIONS}",
            name="ck_retrieval_chunks_embedding_dim",
        ),
        Index("ux_retrieval_chunks_document_index", "document_id", "chunk_index", unique=True),
        Index(
            "ix_retrieval_chunks_filter",
            "scope_id",
            "caps_ref",
            "grade",
            "subject_code",
            "language",
            "status",
        ),
        Index("ix_retrieval_chunks_document_version", "document_id", "document_version_id"),
    )
