"""
Storage Layer
==============
Async SQLAlchemy 2.0 persistence for all three pipeline stages.

Tables:
  ingestion_raw         — RawContent records (staging)
  curriculum_content    — NormalisedContent records (working store)
  training_records      — TrainingRecord JSONL rows (export-ready)
  ingestion_jobs        — Job tracking
  curriculum_standards  — CurriculumStandard catalogue

Design decisions:
  • asyncpg for PostgreSQL, aiosqlite for dev/test
  • Upsert via ON CONFLICT DO UPDATE (idempotent re-runs)
  • Batch writes (configurable chunk size) to manage transaction size
  • JSONB columns for variable metadata without schema migration
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean, Column, DateTime, Float, Integer,
    String, Text, text,
)
from sqlalchemy.dialects.postgresql import JSONB, insert as pg_insert
from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession,
    async_sessionmaker, create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from scripts.ingestion.config import (
    CONTENT_TABLE, JOBS_TABLE, RAW_TABLE,
)
from scripts.ingestion.models import (
    IngestionJob, NormalisedContent, RawContent, TrainingRecord,
)

logger = logging.getLogger(__name__)

_DEFAULT_BATCH = 200


# ── ORM Models ────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


class RawContentRow(Base):
    __tablename__ = RAW_TABLE

    id                  = Column(String(36), primary_key=True)
    source_id           = Column(String(64), nullable=False, index=True)
    source_url          = Column(Text)
    source_internal_id  = Column(String(256))
    raw_text            = Column(Text, nullable=False)
    raw_html            = Column(Text)
    raw_json            = Column(JSONB)
    metadata_           = Column("metadata", JSONB, default=dict)
    scraped_at          = Column(DateTime, default=datetime.utcnow)
    license             = Column(String(128), default="unknown")
    language            = Column(String(8),  default="en")
    processed           = Column(Boolean,    default=False)


class NormalisedContentRow(Base):
    __tablename__ = CONTENT_TABLE

    id                      = Column(String(36), primary_key=True)
    source_id               = Column(String(64), nullable=False, index=True)
    source_url              = Column(Text)
    source_internal_id      = Column(String(256))
    subject                 = Column(String(64),  index=True)
    grade                   = Column(Integer,     index=True)
    topic                   = Column(String(256))
    subtopic                = Column(String(256))
    content_type            = Column(String(32))
    difficulty              = Column(String(32))
    title                   = Column(Text)
    body                    = Column(Text,  nullable=False)
    body_html               = Column(Text)
    answer                  = Column(Text)
    options                 = Column(JSONB)
    explanation             = Column(Text)
    caps_phase              = Column(String(32),  index=True)
    caps_subject            = Column(String(64))
    caps_topic_code         = Column(String(16))
    caps_learning_outcome   = Column(Text)
    caps_content_item_code  = Column(String(32))
    language                = Column(String(8),  default="en")
    jurisdiction            = Column(String(16), default="global")
    license                 = Column(String(128), default="unknown")
    ingested_at             = Column(DateTime, default=datetime.utcnow)
    confidence_score        = Column(Float,   default=1.0)
    extra                   = Column(JSONB)


class TrainingRecordRow(Base):
    __tablename__ = "training_records"

    id            = Column(String(36), primary_key=True)
    source_id     = Column(String(64), index=True)
    caps_code     = Column(String(32))
    grade         = Column(Integer,   index=True)
    subject       = Column(String(64))
    content_type  = Column(String(32))
    system        = Column(Text)
    user_msg      = Column("user",      Text, nullable=False)
    assistant     = Column(Text, nullable=False)
    difficulty    = Column(String(32))
    jurisdiction  = Column(String(16))
    language      = Column(String(8))
    license       = Column(String(128))
    tags          = Column(JSONB)


class IngestionJobRow(Base):
    __tablename__ = JOBS_TABLE

    id               = Column(String(36), primary_key=True)
    source_id        = Column(String(64), nullable=False)
    started_at       = Column(DateTime)
    completed_at     = Column(DateTime)
    status           = Column(String(16), default="pending", index=True)
    items_scraped    = Column(Integer, default=0)
    items_processed  = Column(Integer, default=0)
    items_failed     = Column(Integer, default=0)
    errors           = Column(JSONB, default=list)
    config           = Column(JSONB, default=dict)


# ── Engine / session factory ──────────────────────────────────────────────────

_engine:       AsyncEngine       | None = None
_session_factory: async_sessionmaker | None = None


async def init_db(database_url: str, echo: bool = False) -> None:
    """
    Initialise the async engine and create tables if they don't exist.

    Parameters
    ----------
    database_url : SQLAlchemy async DSN, e.g.
                   "postgresql+asyncpg://user:pass@localhost/eduboost"
                   "sqlite+aiosqlite:///./data/ingestion.db"  (dev/test)
    """
    global _engine, _session_factory
    _engine = create_async_engine(database_url, echo=echo, pool_pre_ping=True)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("[Storage] Database initialised: %s", database_url.split("@")[-1])


async def close_db() -> None:
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None


def get_session() -> AsyncSession:
    assert _session_factory, "Call init_db() first"
    return _session_factory()


# ── RawContent storage ────────────────────────────────────────────────────────

async def upsert_raw_batch(
    items: list[RawContent], batch_size: int = _DEFAULT_BATCH
) -> int:
    """Idempotent upsert of RawContent records. Returns count inserted/updated."""
    total = 0
    for chunk in _chunks(items, batch_size):
        rows = [_raw_to_row(r) for r in chunk]
        async with get_session() as sess:
            stmt = pg_insert(RawContentRow).values(rows)
            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={"processed": stmt.excluded.processed},
            )
            await sess.execute(stmt)
            await sess.commit()
        total += len(rows)
    return total


# ── NormalisedContent storage ─────────────────────────────────────────────────

async def upsert_content_batch(
    items: list[NormalisedContent], batch_size: int = _DEFAULT_BATCH
) -> int:
    total = 0
    for chunk in _chunks(items, batch_size):
        rows = [_norm_to_row(n) for n in chunk]
        async with get_session() as sess:
            stmt = pg_insert(NormalisedContentRow).values(rows)
            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "caps_topic_code":       stmt.excluded.caps_topic_code,
                    "caps_learning_outcome": stmt.excluded.caps_learning_outcome,
                    "confidence_score":      stmt.excluded.confidence_score,
                },
            )
            await sess.execute(stmt)
            await sess.commit()
        total += len(rows)
    return total


# ── TrainingRecord storage ────────────────────────────────────────────────────

async def upsert_training_batch(
    records: list[TrainingRecord], batch_size: int = _DEFAULT_BATCH
) -> int:
    total = 0
    for chunk in _chunks(records, batch_size):
        rows = [_training_to_row(t) for t in chunk]
        async with get_session() as sess:
            stmt = pg_insert(TrainingRecordRow).values(rows)
            stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
            await sess.execute(stmt)
            await sess.commit()
        total += len(rows)
    return total


# ── Job tracking ──────────────────────────────────────────────────────────────

async def upsert_job(job: IngestionJob) -> None:
    row = {
        "id":              job.id,
        "source_id":       job.source_id,
        "started_at":      job.started_at,
        "completed_at":    job.completed_at,
        "status":          job.status.value,
        "items_scraped":   job.items_scraped,
        "items_processed": job.items_processed,
        "items_failed":    job.items_failed,
        "errors":          job.errors,
        "config":          job.config,
    }
    async with get_session() as sess:
        stmt = pg_insert(IngestionJobRow).values([row])
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "status":          stmt.excluded.status,
                "completed_at":    stmt.excluded.completed_at,
                "items_scraped":   stmt.excluded.items_scraped,
                "items_processed": stmt.excluded.items_processed,
                "items_failed":    stmt.excluded.items_failed,
                "errors":          stmt.excluded.errors,
            },
        )
        await sess.execute(stmt)
        await sess.commit()


async def get_job(job_id: str) -> dict[str, Any] | None:
    async with get_session() as sess:
        result = await sess.execute(
            text(f"SELECT * FROM {JOBS_TABLE} WHERE id = :id"),
            {"id": job_id},
        )
        row = result.mappings().first()
        return dict(row) if row else None


# ── Query helpers ─────────────────────────────────────────────────────────────

async def count_content(
    subject: str | None = None,
    grade: int | None = None,
    caps_phase: str | None = None,
) -> int:
    """Count NormalisedContent rows matching optional filters."""
    where_parts = []
    params: dict[str, Any] = {}
    if subject:
        where_parts.append("subject = :subject")
        params["subject"] = subject
    if grade:
        where_parts.append("grade = :grade")
        params["grade"] = grade
    if caps_phase:
        where_parts.append("caps_phase = :caps_phase")
        params["caps_phase"] = caps_phase

    where = "WHERE " + " AND ".join(where_parts) if where_parts else ""
    sql   = text(f"SELECT COUNT(*) FROM {CONTENT_TABLE} {where}")
    async with get_session() as sess:
        result = await sess.execute(sql, params)
        return result.scalar() or 0


# ── Row serialisers ───────────────────────────────────────────────────────────

def _raw_to_row(r: RawContent) -> dict[str, Any]:
    return {
        "id":                 r.id,
        "source_id":          r.source_id,
        "source_url":         r.source_url,
        "source_internal_id": r.source_internal_id,
        "raw_text":           r.raw_text,
        "raw_html":           r.raw_html,
        "raw_json":           r.raw_json,
        "metadata_":          r.metadata,
        "scraped_at":         r.scraped_at,
        "license":            r.license,
        "language":           r.language,
        "processed":          r.processed,
    }


def _norm_to_row(n: NormalisedContent) -> dict[str, Any]:
    return {
        "id":                     n.id,
        "source_id":              n.source_id,
        "source_url":             n.source_url,
        "source_internal_id":     n.source_internal_id,
        "subject":                n.subject,
        "grade":                  n.grade,
        "topic":                  n.topic,
        "subtopic":               n.subtopic,
        "content_type":           n.content_type.value,
        "difficulty":             n.difficulty.value if n.difficulty else None,
        "title":                  n.title,
        "body":                   n.body,
        "body_html":              n.body_html,
        "answer":                 n.answer,
        "options":                n.options,
        "explanation":            n.explanation,
        "caps_phase":             n.caps_phase,
        "caps_subject":           n.caps_subject,
        "caps_topic_code":        n.caps_topic_code,
        "caps_learning_outcome":  n.caps_learning_outcome,
        "caps_content_item_code": n.caps_content_item_code,
        "language":               n.language,
        "jurisdiction":           n.jurisdiction,
        "license":                n.license,
        "ingested_at":            n.ingested_at,
        "confidence_score":       n.confidence_score,
        "extra":                  n.extra,
    }


def _training_to_row(t: TrainingRecord) -> dict[str, Any]:
    return {
        "id":           t.id,
        "source_id":    t.source_id,
        "caps_code":    t.caps_code,
        "grade":        t.grade,
        "subject":      t.subject,
        "content_type": t.content_type.value,
        "system":       t.system,
        "user_msg":     t.user,
        "assistant":    t.assistant,
        "difficulty":   t.difficulty.value if t.difficulty else None,
        "jurisdiction": t.jurisdiction,
        "language":     t.language,
        "license":      t.license,
        "tags":         t.tags,
    }


# ── Utilities ─────────────────────────────────────────────────────────────────

def _chunks(lst: list[Any], n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


class StorageLayer:
    """Simple wrapper providing the StorageLayer interface expected by the
    pipeline. Delegates to the module-level async helpers implemented above.
    """

    def __init__(self, db_url: str = "sqlite+aiosqlite:///ingestion_dev.db", batch_size: int = _DEFAULT_BATCH) -> None:
        self._db_url = db_url
        self._batch_size = batch_size

    async def init(self) -> None:
        await init_db(self._db_url)

    async def close(self) -> None:
        await close_db()

    async def save_raw_batch(self, items: list[RawContent]) -> int:
        return await upsert_raw_batch(items, batch_size=self._batch_size)

    async def save_normalised_batch(self, items: list[NormalisedContent]) -> int:
        return await upsert_content_batch(items, batch_size=self._batch_size)

    async def save_training_batch(self, items: list[TrainingRecord]) -> int:
        return await upsert_training_batch(items, batch_size=self._batch_size)
