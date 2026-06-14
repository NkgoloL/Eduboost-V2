"""Phase 2 semantic retrieval corpus and pgvector indexes.

Revision ID: 20260614_1200_p2_retrieval
Revises: 20260614_0900_p1_validation
Create Date: 2026-06-14 12:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import UserDefinedType

revision = "20260614_1200_p2_retrieval"
down_revision = "20260614_0900_p1_validation"
branch_labels = None
depends_on = None


class Vector1536(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **_: object) -> str:
        return "vector(1536)"


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "retrieval_source_documents",
        sa.Column("document_id", sa.String(length=120), primary_key=True),
        sa.Column("document_version_id", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=True),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.Column("subject_code", sa.String(length=20), nullable=True),
        sa.Column("language", sa.String(length=8), nullable=False, server_default="en"),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("permission_scope", sa.String(length=80), nullable=False, server_default="public"),
        sa.Column("license_status", sa.String(length=80), nullable=False),
        sa.Column("quality_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("source_hash", sa.String(length=120), nullable=False),
        sa.Column("source_uri", sa.String(length=500), nullable=True),
        sa.Column("source_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("grade IS NULL OR (grade >= 0 AND grade <= 12)", name="ck_retrieval_documents_grade"),
        sa.CheckConstraint(
            "quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1)",
            name="ck_retrieval_documents_quality",
        ),
    )
    op.create_index("ix_retrieval_source_documents_scope_id", "retrieval_source_documents", ["scope_id"])
    op.create_index("ix_retrieval_source_documents_caps_ref", "retrieval_source_documents", ["caps_ref"])
    op.create_index("ix_retrieval_source_documents_status", "retrieval_source_documents", ["status"])
    op.create_index(
        "ix_retrieval_documents_filter",
        "retrieval_source_documents",
        ["scope_id", "caps_ref", "grade", "subject_code", "language", "status"],
    )

    op.create_table(
        "retrieval_source_chunks",
        sa.Column("chunk_id", sa.String(length=120), primary_key=True),
        sa.Column(
            "document_id",
            sa.String(length=120),
            sa.ForeignKey("retrieval_source_documents.document_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("document_version_id", sa.String(length=120), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("heading", sa.String(length=300), nullable=True),
        sa.Column("section_path", sa.String(length=500), nullable=True),
        sa.Column("page_start", sa.Integer(), nullable=True),
        sa.Column("page_end", sa.Integer(), nullable=True),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=True),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.Column("subject_code", sa.String(length=20), nullable=True),
        sa.Column("language", sa.String(length=8), nullable=False, server_default="en"),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("permission_scope", sa.String(length=80), nullable=False, server_default="public"),
        sa.Column("quality_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("source_hash", sa.String(length=120), nullable=False),
        sa.Column("chunk_hash", sa.String(length=120), nullable=False),
        sa.Column("curriculum_mapping_id", sa.String(length=120), nullable=True),
        sa.Column("embedding_model", sa.String(length=120), nullable=True),
        sa.Column("embedding_version", sa.String(length=80), nullable=True),
        sa.Column("embedding_dim", sa.Integer(), nullable=True),
        sa.Column("embedding", Vector1536(), nullable=True),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("chunk_index >= 0", name="ck_retrieval_chunks_index"),
        sa.CheckConstraint("grade IS NULL OR (grade >= 0 AND grade <= 12)", name="ck_retrieval_chunks_grade"),
        sa.CheckConstraint(
            "quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1)",
            name="ck_retrieval_chunks_quality",
        ),
        sa.CheckConstraint("embedding IS NULL OR embedding_dim = 1536", name="ck_retrieval_chunks_embedding_dim"),
    )
    op.create_index("ix_retrieval_source_chunks_status", "retrieval_source_chunks", ["status"])
    op.create_index(
        "ux_retrieval_chunks_document_index",
        "retrieval_source_chunks",
        ["document_id", "chunk_index"],
        unique=True,
    )
    op.create_index(
        "ix_retrieval_chunks_filter",
        "retrieval_source_chunks",
        ["scope_id", "caps_ref", "grade", "subject_code", "language", "status"],
    )
    op.create_index(
        "ix_retrieval_chunks_document_version",
        "retrieval_source_chunks",
        ["document_id", "document_version_id"],
    )
    op.execute(
        """
        CREATE INDEX ix_retrieval_chunks_embedding_hnsw
        ON retrieval_source_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        WHERE embedding IS NOT NULL
        """
    )
    op.execute(
        """
        CREATE INDEX ix_retrieval_chunks_fulltext_gin
        ON retrieval_source_chunks
        USING gin (to_tsvector('simple', COALESCE(heading, '') || ' ' || content))
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_retrieval_chunks_fulltext_gin")
    op.execute("DROP INDEX IF EXISTS ix_retrieval_chunks_embedding_hnsw")
    op.drop_table("retrieval_source_chunks")
    op.drop_table("retrieval_source_documents")
    # Keep the vector extension: other current/future schemas may use it.
