"""
etl_pipeline_v2.py — Eduboost ETL: Phases 8–12 Extensions
==========================================================
Extends etl_pipeline.py (Phases 0–7) with:

  Phase 8  — Canonical Content Store (versioning, document API, soft-delete)
  Phase 9  — Search & Vector Indexing (FTS5 full-text, embedding interface,
              hybrid search, citation support)
  Phase 10 — Training Dataset Builder (QA generation, summaries, JSONL/CSV/
              Parquet export, dataset versioning, contamination checks)
  Phase 12 — Monitoring, Observability & Feedback Loop (metrics collection,
              stale-content detection, feedback ingestion, health reports,
              alerting hooks)

Usage
-----
    from etl_pipeline import EduboostETL
    from etl_pipeline_v2 import EduboostETLv2

    etl = EduboostETLv2(db_url="sqlite:///eduboost_etl.db", storage_root="./data")
    etl.init_db()          # creates v1 + v2 tables
    etl.init_fts()         # creates FTS5 virtual tables (SQLite only)

    # Phase 9: full-text search
    hits = etl.search_fulltext("fractions grade 4", grade=4, limit=10)

    # Phase 10: generate training examples
    dataset = etl.generate_training_dataset(document_ids=["doc-abc"])
    etl.export_dataset(dataset.dataset_id, format="jsonl", out_path="./exports")

    # Phase 12: health report
    report = etl.get_monitoring_report()
    etl.submit_feedback(document_id="doc-abc", feedback_type="incorrect_answer",
                        user_id="learner_42", details="The answer on page 3 is wrong.")
"""

from __future__ import annotations

import csv
import json
import re
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# ── Base pipeline import ──────────────────────────────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent))
from app.services.etl.etl_pipeline import (
    EduboostETL, DocumentChunk,
    ProcessingStatus, _now, _uid,
)

# ── Optional heavy deps ───────────────────────────────────────────────────
try:
    import numpy as np          # for cosine similarity
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import pyarrow as pa        # for Parquet export
    import pyarrow.parquet as pq
    HAS_PARQUET = True
except ImportError:
    HAS_PARQUET = False


# ===========================================================================
# PHASE 8 — CANONICAL CONTENT STORE: extra schemas & dataclasses
# ===========================================================================

SCHEMA_V2_SQL = """
-- Phase 8: document versioning
CREATE TABLE IF NOT EXISTS document_versions (
    version_id       TEXT PRIMARY KEY,
    document_id      TEXT NOT NULL,
    version_number   TEXT NOT NULL,           -- semver: "1.0", "1.1", "2.0"
    change_summary   TEXT DEFAULT '',
    created_by       TEXT DEFAULT 'system',
    created_at       TEXT NOT NULL,
    snapshot_path    TEXT,                    -- path to frozen normalized JSON
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

-- Phase 8: curriculum mappings (learning objective ↔ chunk)
CREATE TABLE IF NOT EXISTS curriculum_mappings (
    mapping_id       TEXT PRIMARY KEY,
    document_id      TEXT NOT NULL,
    chunk_id         TEXT,
    curriculum       TEXT NOT NULL DEFAULT 'CAPS',
    grade            INTEGER,
    subject          TEXT,
    topic_code       TEXT,                    -- e.g. "CAPS-G4-MATH-FRACTIONS"
    learning_outcome TEXT,
    created_at       TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(document_id),
    FOREIGN KEY (chunk_id)    REFERENCES document_chunks(chunk_id)
);

-- Phase 9: embedding records
CREATE TABLE IF NOT EXISTS chunk_embeddings (
    embedding_id     TEXT PRIMARY KEY,
    chunk_id         TEXT NOT NULL UNIQUE,
    document_id      TEXT NOT NULL,
    model_name       TEXT NOT NULL DEFAULT 'stub-v0',
    embedding_dim    INTEGER NOT NULL DEFAULT 0,
    embedding_blob   BLOB,                    -- raw float32 bytes (numpy.tobytes)
    indexed_at       TEXT NOT NULL,
    FOREIGN KEY (chunk_id)    REFERENCES document_chunks(chunk_id),
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

CREATE INDEX IF NOT EXISTS idx_embeddings_doc ON chunk_embeddings(document_id);

-- Phase 9: FTS5 full-text search  (created separately via init_fts())
-- CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(...)

-- Phase 10: training datasets
CREATE TABLE IF NOT EXISTS training_datasets (
    dataset_id       TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    description      TEXT DEFAULT '',
    dataset_type     TEXT NOT NULL,           -- retrieval_corpus / qa_pairs / summaries / ...
    version          TEXT NOT NULL DEFAULT '1.0',
    split            TEXT NOT NULL DEFAULT 'train',  -- train / validation / test
    document_ids     TEXT NOT NULL DEFAULT '[]',     -- JSON array
    example_count    INTEGER DEFAULT 0,
    is_synthetic     INTEGER DEFAULT 0,
    created_by       TEXT DEFAULT 'system',
    created_at       TEXT NOT NULL,
    exported_at      TEXT,
    export_path      TEXT
);

-- Phase 10: individual training examples
CREATE TABLE IF NOT EXISTS training_examples (
    example_id       TEXT PRIMARY KEY,
    dataset_id       TEXT NOT NULL,
    document_id      TEXT NOT NULL,
    chunk_id         TEXT,
    example_type     TEXT NOT NULL,           -- qa / summary / concept / rubric / ...
    input_text       TEXT NOT NULL,
    output_text      TEXT NOT NULL,
    source_page      INTEGER,
    curriculum_code  TEXT,
    grade            INTEGER,
    subject          TEXT,
    is_synthetic     INTEGER DEFAULT 0,
    human_reviewed   INTEGER DEFAULT 0,
    quality_score    REAL DEFAULT 0.0,
    created_at       TEXT NOT NULL,
    FOREIGN KEY (dataset_id)  REFERENCES training_datasets(dataset_id),
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

CREATE INDEX IF NOT EXISTS idx_examples_dataset  ON training_examples(dataset_id);
CREATE INDEX IF NOT EXISTS idx_examples_document ON training_examples(document_id);

-- Phase 12: pipeline metrics (time-series counters)
CREATE TABLE IF NOT EXISTS pipeline_metrics (
    metric_id        TEXT PRIMARY KEY,
    metric_name      TEXT NOT NULL,           -- ingestion_count / extraction_failures / ...
    metric_value     REAL NOT NULL,
    tags             TEXT DEFAULT '{}',       -- JSON {stage, subject, grade, ...}
    recorded_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_metrics_name ON pipeline_metrics(metric_name, recorded_at);

-- Phase 12: user feedback
CREATE TABLE IF NOT EXISTS user_feedback (
    feedback_id      TEXT PRIMARY KEY,
    document_id      TEXT,
    chunk_id         TEXT,
    user_id          TEXT NOT NULL,
    feedback_type    TEXT NOT NULL,           -- incorrect_answer / missing_document / ...
    details          TEXT DEFAULT '',
    resolved         INTEGER DEFAULT 0,
    resolved_at      TEXT,
    resolved_by      TEXT,
    review_task_id   TEXT,
    created_at       TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_doc  ON user_feedback(document_id);
CREATE INDEX IF NOT EXISTS idx_feedback_type ON user_feedback(feedback_type);
"""


@dataclass
class DocumentVersion:
    version_id:     str
    document_id:    str
    version_number: str
    change_summary: str
    created_by:     str
    created_at:     str
    snapshot_path:  Optional[str] = None


@dataclass
class TrainingDataset:
    dataset_id:    str
    name:          str
    description:   str
    dataset_type:  str   # retrieval_corpus | qa_pairs | summaries | concepts | ...
    version:       str
    split:         str   # train | validation | test
    document_ids:  list[str]
    example_count: int = 0
    is_synthetic:  bool = False
    created_by:    str = "system"
    created_at:    str = ""
    exported_at:   Optional[str] = None
    export_path:   Optional[str] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = _now()


@dataclass
class TrainingExample:
    example_id:      str
    dataset_id:      str
    document_id:     str
    chunk_id:        Optional[str]
    example_type:    str   # qa | summary | concept | rubric
    input_text:      str
    output_text:     str
    source_page:     Optional[int] = None
    curriculum_code: Optional[str] = None
    grade:           Optional[int] = None
    subject:         Optional[str] = None
    is_synthetic:    bool = False
    human_reviewed:  bool = False
    quality_score:   float = 0.0
    created_at:      str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = _now()


@dataclass
class FeedbackRecord:
    feedback_id:    str
    document_id:    Optional[str]
    chunk_id:       Optional[str]
    user_id:        str
    feedback_type:  str   # incorrect_answer | missing_document | outdated_document | bad_citation | wrong_grade_subject
    details:        str
    resolved:       bool = False
    resolved_at:    Optional[str] = None
    resolved_by:    Optional[str] = None
    review_task_id: Optional[str] = None
    created_at:     str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = _now()


@dataclass
class MonitoringReport:
    generated_at:       str
    total_documents:    int
    ingestion_rate_7d:  int           # docs ingested last 7 days
    approval_rate:      float         # approved / (approved + rejected) last 30 days
    avg_quality_score:  float
    stale_documents:    list[dict]    # docs not updated > 90 days still in early status
    failed_jobs_24h:    int
    pending_reviews:    int
    extraction_failure_rate: float
    feedback_summary:   dict          # {type: count}
    alerts:             list[str]     # human-readable issues


# ===========================================================================
# EXTENDED PIPELINE  (Phases 8–12)
# ===========================================================================

class EduboostETLv2(EduboostETL):
    """Drop-in extension of EduboostETL with Phases 8–12."""

    # ── Initialisation ─────────────────────────────────────────────────────

    def init_db(self):
        """Create v1 tables, then v2 tables."""
        super().init_db()
        db = self._db()
        # Execute each statement separately to avoid issues with compound SQL
        statements = [s.strip() for s in SCHEMA_V2_SQL.split(";") if s.strip()]
        for stmt in statements:
            try:
                db.execute(stmt)
            except sqlite3.OperationalError as e:
                if "already exists" not in str(e).lower():
                    raise
        db.commit()

    def init_fts(self):
        """Create FTS5 virtual table for full-text search (SQLite ≥ 3.9)."""
        db = self._db()
        try:
            db.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
                USING fts5(
                    chunk_id UNINDEXED,
                    document_id UNINDEXED,
                    heading,
                    content,
                    section_path,
                    tokenize='porter unicode61'
                )
            """)
            db.commit()
            self._populate_fts()
        except sqlite3.OperationalError as e:
            # FTS5 may not be compiled in — log and skip
            print(f"[WARN] FTS5 not available: {e}. Full-text search will fall back to LIKE.")

    def _populate_fts(self):
        """Sync all chunks into the FTS table."""
        db = self._db()
        try:
            db.execute("DELETE FROM chunks_fts")
            db.execute("""
                INSERT INTO chunks_fts (chunk_id, document_id, heading, content, section_path)
                SELECT chunk_id, document_id, heading, content, section_path
                FROM document_chunks
            """)
            db.commit()
        except sqlite3.OperationalError:
            pass  # FTS not available


    # =========================================================================
    # PHASE 8 — CANONICAL CONTENT STORE
    # =========================================================================

    def create_version(self, document_id: str, change_summary: str = "",
                       created_by: str = "system") -> DocumentVersion:
        """Snapshot the current normalized output as a new version."""
        self._load_document(document_id)
        # Bump version
        existing = self._list_versions(document_id)
        if existing:
            parts = existing[-1].version_number.split(".")
            minor = int(parts[1]) + 1 if len(parts) > 1 else 0
            version_number = f"{parts[0]}.{minor}"
        else:
            version_number = "1.0"

        # Snapshot normalized JSON
        src = self.storage_root / "normalized" / document_id / "normalized.json"
        snap_dir = self.storage_root / "versions" / document_id / version_number
        snap_dir.mkdir(parents=True, exist_ok=True)
        snap_path = snap_dir / "normalized.json"
        if src.exists():
            import shutil
            shutil.copy2(src, snap_path)

        v = DocumentVersion(
            version_id=_uid(), document_id=document_id,
            version_number=version_number, change_summary=change_summary,
            created_by=created_by, created_at=_now(),
            snapshot_path=str(snap_path) if snap_path.exists() else None,
        )
        db = self._db()
        db.execute(
            "INSERT INTO document_versions VALUES (?,?,?,?,?,?,?)",
            (v.version_id, v.document_id, v.version_number, v.change_summary,
             v.created_by, v.created_at, v.snapshot_path)
        )
        db.commit()
        return v

    def _list_versions(self, document_id: str) -> list[DocumentVersion]:
        rows = self._db().execute(
            "SELECT * FROM document_versions WHERE document_id=? ORDER BY created_at",
            (document_id,)
        ).fetchall()
        return [DocumentVersion(**dict(r)) for r in rows]

    def list_versions(self, document_id: str) -> list[dict]:
        return [asdict(v) for v in self._list_versions(document_id)]

    def get_document_chunks(self, document_id: str,
                            chunk_type: Optional[str] = None) -> list[dict]:
        """Return all chunks for a document, optionally filtered by type."""
        chunks = self._load_chunks(document_id)
        if chunk_type:
            chunks = [c for c in chunks if c.chunk_type == chunk_type]
        return [asdict(c) for c in chunks]

    def add_curriculum_mapping(self, document_id: str, chunk_id: Optional[str],
                                grade: int, subject: str, topic_code: str,
                                learning_outcome: str,
                                curriculum: str = "CAPS") -> str:
        """Link a chunk to a curriculum learning objective."""
        mapping_id = _uid()
        self._db().execute(
            "INSERT INTO curriculum_mappings VALUES (?,?,?,?,?,?,?,?,?)",
            (mapping_id, document_id, chunk_id, curriculum, grade,
             subject, topic_code, learning_outcome, _now())
        )
        self._db().commit()
        return mapping_id

    def update_document_metadata(self, document_id: str, updates: dict,
                                  updated_by: str = "system") -> dict:
        """
        Partial metadata update. Allowed fields: title, description, subject,
        grade, language, publisher, author, publication_year, curriculum,
        province, license_status, reviewer_notes.
        Creates a new version snapshot automatically.
        """
        allowed = {
            "title", "description", "subject", "grade", "language",
            "publisher", "author", "publication_year", "curriculum",
            "province", "license_status", "reviewer_notes", "phase",
        }
        filtered = {k: v for k, v in updates.items() if k in allowed}
        if not filtered:
            return {"updated": 0, "skipped": list(updates.keys())}

        clauses = ", ".join(f"{k}=?" for k in filtered)
        values = list(filtered.values()) + [_now(), document_id]
        self._db().execute(
            f"UPDATE documents SET {clauses}, updated_at=? WHERE document_id=?",
            values
        )
        self._db().commit()
        # Auto-snapshot on metadata correction
        self.create_version(document_id, change_summary=f"Metadata update by {updated_by}",
                            created_by=updated_by)
        return {"updated": len(filtered), "fields": list(filtered.keys())}

    def deprecate_document(self, document_id: str, reason: str = "") -> dict:
        """Soft-delete: move to 'archived' status."""
        self._db().execute(
            "UPDATE documents SET processing_status=?, updated_at=?, rejected_reason=? "
            "WHERE document_id=?",
            (ProcessingStatus.archived, _now(), reason or "Deprecated", document_id)
        )
        self._db().commit()
        return {"document_id": document_id, "status": "archived"}


    # =========================================================================
    # PHASE 9 — SEARCH & VECTOR INDEXING
    # =========================================================================

    def index_chunk_for_search(self, chunk: DocumentChunk):
        """Insert or update one chunk in the FTS index."""
        try:
            db = self._db()
            db.execute("DELETE FROM chunks_fts WHERE chunk_id=?", (chunk.chunk_id,))
            db.execute(
                "INSERT INTO chunks_fts (chunk_id, document_id, heading, content, section_path) "
                "VALUES (?,?,?,?,?)",
                (chunk.chunk_id, chunk.document_id, chunk.heading,
                 chunk.content, chunk.section_path)
            )
            db.commit()
        except sqlite3.OperationalError:
            pass  # FTS not available

    def search_fulltext(self, query: str, grade: Optional[int] = None,
                        subject: Optional[str] = None,
                        document_type: Optional[str] = None,
                        limit: int = 20) -> list[dict]:
        """
        Full-text search across chunks using FTS5 (falls back to LIKE).
        Returns hits with citation support: document_id, page_start, section_path.
        """
        db = self._db()
        try:
            # Try FTS5 path
            base_sql = """
                SELECT cf.chunk_id, cf.document_id, cf.heading, cf.content,
                       cf.section_path, dc.page_start, dc.page_end,
                       dc.curriculum_code, dc.chunk_type, dc.token_count,
                       d.title, d.grade, d.subject, d.document_type,
                       d.language, d.quality_score
                FROM chunks_fts cf
                JOIN document_chunks dc ON cf.chunk_id = dc.chunk_id
                JOIN documents d ON cf.document_id = d.document_id
                WHERE chunks_fts MATCH ?
                  AND d.processing_status IN ('approved','indexed','training_ready')
            """
            params: list = [query]
            if grade:
                base_sql += " AND d.grade = ?"
                params.append(grade)
            if subject:
                base_sql += " AND d.subject = ?"
                params.append(subject)
            if document_type:
                base_sql += " AND d.document_type = ?"
                params.append(document_type)
            base_sql += f" ORDER BY rank LIMIT {limit}"
            rows = db.execute(base_sql, params).fetchall()
        except sqlite3.OperationalError:
            # FTS5 not available — LIKE fallback
            like_q = f"%{query}%"
            base_sql = """
                SELECT dc.chunk_id, dc.document_id, dc.heading, dc.content,
                       dc.section_path, dc.page_start, dc.page_end,
                       dc.curriculum_code, dc.chunk_type, dc.token_count,
                       d.title, d.grade, d.subject, d.document_type,
                       d.language, d.quality_score
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.document_id
                WHERE (dc.content LIKE ? OR dc.heading LIKE ?)
                  AND d.processing_status IN ('approved','indexed','training_ready')
            """
            params = [like_q, like_q]
            if grade:
                base_sql += " AND d.grade = ?"
                params.append(grade)
            if subject:
                base_sql += " AND d.subject = ?"
                params.append(subject)
            if document_type:
                base_sql += " AND d.document_type = ?"
                params.append(document_type)
            base_sql += f" LIMIT {limit}"
            rows = db.execute(base_sql, params).fetchall()

        results = []
        for r in rows:
            row = dict(r)
            # Citation object for AI consumers
            row["citation"] = {
                "document_id":   row["document_id"],
                "title":         row["title"],
                "section_path":  row.get("section_path", ""),
                "page_start":    row.get("page_start"),
                "page_end":      row.get("page_end"),
                "curriculum_code": row.get("curriculum_code"),
            }
            results.append(row)
        return results

    def store_embedding(self, chunk_id: str, document_id: str,
                        embedding: list[float], model_name: str = "stub-v0") -> str:
        """
        Persist a vector embedding for a chunk.
        In production replace with pgvector INSERT or Qdrant upsert.
        """
        emb_id = _uid()
        blob = None
        if HAS_NUMPY:
            blob = bytes(bytearray(
                int(b) for b in (
                    b''.join(
                        x.to_bytes(4, 'little') if isinstance(x, int)
                        else bytes([int(x * 127 + 128)]) * 4
                        for x in embedding[:1]  # stub: store first element only
                    )
                )
            ))
            # Use numpy for proper serialisation
            arr = np.array(embedding, dtype=np.float32)
            blob = arr.tobytes()

        db = self._db()
        db.execute(
            "INSERT OR REPLACE INTO chunk_embeddings "
            "(embedding_id, chunk_id, document_id, model_name, embedding_dim, "
            "embedding_blob, indexed_at) VALUES (?,?,?,?,?,?,?)",
            (emb_id, chunk_id, document_id, model_name,
             len(embedding), blob, _now())
        )
        db.commit()
        return emb_id

    def semantic_search_stub(self, query_embedding: list[float],
                             grade: Optional[int] = None,
                             subject: Optional[str] = None,
                             limit: int = 10) -> list[dict]:
        """
        Cosine-similarity search using stored embeddings (numpy path).
        For production: replace this body with a pgvector or Qdrant call.
        """
        if not HAS_NUMPY:
            return [{"warning": "numpy not installed — install numpy for semantic search"}]

        db = self._db()
        rows = db.execute(
            """SELECT ce.chunk_id, ce.document_id, ce.embedding_blob, ce.embedding_dim,
                      dc.heading, dc.content, dc.section_path, dc.page_start,
                      d.title, d.grade, d.subject, d.document_type
               FROM chunk_embeddings ce
               JOIN document_chunks dc ON ce.chunk_id = dc.chunk_id
               JOIN documents d ON ce.document_id = d.document_id
               WHERE d.processing_status IN ('approved','indexed','training_ready')
                 AND ce.embedding_blob IS NOT NULL
            """ + (f" AND d.grade={grade}" if grade else "")
              + (f" AND d.subject='{subject}'" if subject else "")
        ).fetchall()

        if not rows:
            return []

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec) + 1e-10

        scored = []
        for r in rows:
            blob = r["embedding_blob"]
            dim  = r["embedding_dim"]
            if not blob or dim == 0:
                continue
            try:
                c_vec = np.frombuffer(blob, dtype=np.float32)
                if len(c_vec) != len(q_vec):
                    continue
                score = float(np.dot(q_vec, c_vec) / (q_norm * (np.linalg.norm(c_vec) + 1e-10)))
                scored.append({"score": score, **dict(r)})
            except Exception:
                continue

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    def hybrid_search(self, query: str,
                      query_embedding: Optional[list[float]] = None,
                      grade: Optional[int] = None,
                      subject: Optional[str] = None,
                      document_type: Optional[str] = None,
                      keyword_weight: float = 0.5,
                      semantic_weight: float = 0.5,
                      limit: int = 20) -> list[dict]:
        """
        Reciprocal-rank fusion of keyword + semantic results.
        Falls back to keyword-only when no embedding is supplied.
        """
        kw_results = self.search_fulltext(query, grade=grade, subject=subject,
                                          document_type=document_type, limit=limit * 2)
        if not kw_results or not query_embedding:
            return kw_results[:limit]

        sem_results = self.semantic_search_stub(query_embedding, grade=grade,
                                                subject=subject, limit=limit * 2)

        # Reciprocal Rank Fusion
        RRF_K = 60
        scores: dict[str, float] = {}
        for rank, hit in enumerate(kw_results):
            cid = hit["chunk_id"]
            scores[cid] = scores.get(cid, 0) + keyword_weight / (RRF_K + rank + 1)
        for rank, hit in enumerate(sem_results):
            cid = hit.get("chunk_id", "")
            scores[cid] = scores.get(cid, 0) + semantic_weight / (RRF_K + rank + 1)

        # Merge metadata
        chunk_meta = {h["chunk_id"]: h for h in kw_results}
        chunk_meta.update({h.get("chunk_id", ""): h for h in sem_results})

        fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [{"rrf_score": sc, **chunk_meta[cid]}
                for cid, sc in fused[:limit] if cid in chunk_meta]

    def mark_indexed(self, document_id: str) -> str:
        """After embedding all chunks, promote document to 'indexed'."""
        self._db().execute(
            "UPDATE documents SET processing_status=?, updated_at=? WHERE document_id=?",
            (ProcessingStatus.indexed, _now(), document_id)
        )
        self._db().commit()
        return ProcessingStatus.indexed


    # =========================================================================
    # PHASE 10 — TRAINING DATASET BUILDER
    # =========================================================================

    def generate_training_dataset(
        self,
        document_ids: Optional[list[str]] = None,
        example_type: str = "qa",          # qa | summary | concept | rubric
        dataset_name: Optional[str] = None,
        split: str = "train",
        is_synthetic: bool = True,
        created_by: str = "system",
    ) -> TrainingDataset:
        """
        Auto-generate training examples from approved/indexed chunks.

        example_type:
            qa       — question + answer pairs (one per chunk)
            summary  — chunk → brief summary
            concept  — extract key concepts + definitions
            rubric   — assessment marking guidance from memoranda

        Returns a TrainingDataset with all examples stored in the DB.
        """
        # Resolve document list
        if document_ids:
            clause = "d.document_id IN (%s)" % ",".join("?" * len(document_ids))
            params: list = list(document_ids)
        else:
            clause = "d.processing_status IN ('approved','indexed','training_ready')"
            params = []

        rows = self._db().execute(
            f"""SELECT dc.*, d.grade, d.subject, d.document_type, d.title
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.document_id
                WHERE {clause}
                ORDER BY dc.document_id, dc.chunk_index""",
            params
        ).fetchall()

        ds_id = _uid()
        ds_name = dataset_name or f"{example_type.upper()} dataset — {_now()[:10]}"
        examples: list[TrainingExample] = []

        for row in rows:
            chunk = dict(row)
            ex = self._generate_example(chunk, ds_id, example_type, is_synthetic)
            if ex:
                examples.append(ex)

        # Save dataset record
        doc_ids_json = json.dumps(list({e.document_id for e in examples}))
        dataset = TrainingDataset(
            dataset_id=ds_id, name=ds_name, description="",
            dataset_type=example_type, version="1.0", split=split,
            document_ids=json.loads(doc_ids_json),
            example_count=len(examples), is_synthetic=is_synthetic,
            created_by=created_by,
        )
        db = self._db()
        db.execute(
            "INSERT INTO training_datasets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (dataset.dataset_id, dataset.name, dataset.description,
             dataset.dataset_type, dataset.version, dataset.split,
             doc_ids_json, dataset.example_count, int(dataset.is_synthetic),
             dataset.created_by, dataset.created_at, None, None)
        )

        for ex in examples:
            db.execute(
                "INSERT INTO training_examples VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (ex.example_id, ex.dataset_id, ex.document_id, ex.chunk_id,
                 ex.example_type, ex.input_text, ex.output_text, ex.source_page,
                 ex.curriculum_code, ex.grade, ex.subject,
                 int(ex.is_synthetic), int(ex.human_reviewed),
                 ex.quality_score, ex.created_at)
            )
        db.commit()
        return dataset

    def _generate_example(self, chunk: dict, dataset_id: str,
                           example_type: str,
                           is_synthetic: bool) -> Optional[TrainingExample]:
        """Template-based example generation (replace with LLM call in prod)."""
        content = (chunk.get("content") or "").strip()
        heading = (chunk.get("heading") or "").strip()
        if len(content) < 50:
            return None

        if example_type == "qa":
            # Simple heuristic: turn heading into a question
            if heading:
                q = f"What does the section '{heading}' explain?"
            else:
                q = "What is the main idea of this passage?"
            a = content[:500].strip()
            input_text, output_text = q, a

        elif example_type == "summary":
            input_text  = f"Summarise the following educational content:\n\n{content[:800]}"
            # Stub: first 2 sentences as summary
            sentences = re.split(r'(?<=[.!?])\s+', content)
            output_text = " ".join(sentences[:2]).strip() or content[:200]

        elif example_type == "concept":
            input_text  = f"List the key concepts and definitions from:\n\n{content[:800]}"
            # Extract bolded terms or capitalised phrases as stub
            terms = re.findall(r'\*\*(.+?)\*\*|__(.+?)__|([A-Z][a-z]+ [A-Z][a-z]+)', content)
            flat  = [next(t for t in term if t) for term in terms[:5]]
            output_text = "; ".join(flat) if flat else content[:150]

        elif example_type == "rubric":
            input_text  = f"Generate a marking rubric for:\n\n{content[:600]}"
            output_text = (
                "Criterion 1 — Accuracy (4 marks): ...\n"
                "Criterion 2 — Completeness (3 marks): ...\n"
                "Criterion 3 — Presentation (3 marks): ...\n"
                "[Replace with actual rubric derived from memorandum content]"
            )
        else:
            return None

        return TrainingExample(
            example_id=_uid(), dataset_id=dataset_id,
            document_id=chunk["document_id"],
            chunk_id=chunk.get("chunk_id"),
            example_type=example_type,
            input_text=input_text, output_text=output_text,
            source_page=chunk.get("page_start"),
            curriculum_code=chunk.get("curriculum_code"),
            grade=chunk.get("grade"), subject=chunk.get("subject"),
            is_synthetic=is_synthetic,
            quality_score=min(1.0, len(content) / 1000),  # rough proxy
        )

    def list_training_datasets(self) -> list[dict]:
        rows = self._db().execute(
            "SELECT * FROM training_datasets ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_training_examples(self, dataset_id: str,
                               limit: int = 100, offset: int = 0) -> list[dict]:
        rows = self._db().execute(
            "SELECT * FROM training_examples WHERE dataset_id=? "
            "ORDER BY created_at LIMIT ? OFFSET ?",
            (dataset_id, limit, offset)
        ).fetchall()
        return [dict(r) for r in rows]

    def contamination_check(self, dataset_id: str,
                             test_dataset_id: str) -> dict:
        """Detect exact-match overlap between train and test splits."""
        def _hashes(ds_id: str) -> set[str]:
            rows = self._db().execute(
                "SELECT input_text FROM training_examples WHERE dataset_id=?", (ds_id,)
            ).fetchall()
            return {hashlib.md5(r["input_text"].encode()).hexdigest() for r in rows}

        import hashlib
        h1 = _hashes(dataset_id)
        h2 = _hashes(test_dataset_id)
        overlap = h1 & h2
        return {
            "dataset_a_count":  len(h1),
            "dataset_b_count":  len(h2),
            "overlap_count":    len(overlap),
            "contamination_pct": round(len(overlap) / max(len(h1), 1) * 100, 2),
            "is_contaminated":  len(overlap) > 0,
        }

    def export_dataset(self, dataset_id: str, fmt: str = "jsonl",
                       out_dir: str = "./exports") -> str:
        """
        Export training examples to file.
        fmt: 'jsonl' | 'csv' | 'parquet'
        Returns the output file path.
        """
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        examples = self.get_training_examples(dataset_id, limit=100_000)
        if not examples:
            return ""

        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        base = Path(out_dir) / f"dataset_{dataset_id[:8]}_{ts}"

        if fmt == "jsonl":
            path = str(base) + ".jsonl"
            with open(path, "w") as f:
                for ex in examples:
                    f.write(json.dumps({
                        "id":       ex["example_id"],
                        "type":     ex["example_type"],
                        "input":    ex["input_text"],
                        "output":   ex["output_text"],
                        "grade":    ex.get("grade"),
                        "subject":  ex.get("subject"),
                        "doc_id":   ex["document_id"],
                        "synthetic": bool(ex.get("is_synthetic", 0)),
                    }) + "\n")

        elif fmt == "csv":
            path = str(base) + ".csv"
            fieldnames = ["example_id","example_type","input_text","output_text",
                          "grade","subject","document_id","is_synthetic",
                          "human_reviewed","quality_score","created_at"]
            with open(path, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                w.writeheader()
                w.writerows(examples)

        elif fmt == "parquet":
            if not HAS_PARQUET:
                raise RuntimeError("pyarrow is required for Parquet export: pip install pyarrow")
            path = str(base) + ".parquet"
            table = pa.Table.from_pylist(examples)
            pq.write_table(table, path)

        else:
            raise ValueError(f"Unsupported format: {fmt}. Use jsonl, csv, or parquet.")

        # Record export
        self._db().execute(
            "UPDATE training_datasets SET exported_at=?, export_path=? WHERE dataset_id=?",
            (_now(), path, dataset_id)
        )
        self._db().commit()
        return path

    def mark_training_ready(self, document_id: str) -> str:
        """Promote an approved+indexed document to training_ready."""
        self._db().execute(
            "UPDATE documents SET processing_status=?, training_readiness=1, "
            "updated_at=? WHERE document_id=?",
            (ProcessingStatus.training_ready, _now(), document_id)
        )
        self._db().commit()
        return ProcessingStatus.training_ready


    # =========================================================================
    # PHASE 12 — MONITORING, OBSERVABILITY & FEEDBACK LOOP
    # =========================================================================

    def record_metric(self, name: str, value: float, tags: Optional[dict] = None):
        """Append one time-series metric point."""
        self._db().execute(
            "INSERT INTO pipeline_metrics VALUES (?,?,?,?,?)",
            (_uid(), name, value, json.dumps(tags or {}), _now())
        )
        self._db().commit()

    def submit_feedback(
        self,
        user_id: str,
        feedback_type: str,
        details: str = "",
        document_id: Optional[str] = None,
        chunk_id: Optional[str] = None,
    ) -> FeedbackRecord:
        """
        Ingest user feedback and optionally create a review task.
        feedback_type: incorrect_answer | missing_document | outdated_document |
                       bad_citation | wrong_grade_subject
        """
        fb = FeedbackRecord(
            feedback_id=_uid(), document_id=document_id, chunk_id=chunk_id,
            user_id=user_id, feedback_type=feedback_type, details=details,
        )
        db = self._db()
        db.execute(
            "INSERT INTO user_feedback VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (fb.feedback_id, fb.document_id, fb.chunk_id, fb.user_id,
             fb.feedback_type, fb.details, int(fb.resolved), fb.resolved_at,
             fb.resolved_by, fb.review_task_id, fb.created_at)
        )

        # Auto-create review task for actionable feedback types
        if document_id and feedback_type in ("incorrect_answer", "outdated_document",
                                              "bad_citation", "wrong_grade_subject"):
            task_id = _uid()
            db.execute(
                "INSERT INTO review_tasks VALUES (?,?,?,?,?,?,?)",
                (task_id, document_id,
                 f"User feedback: {feedback_type} — {details[:120]}",
                 _now(), None, None, None)
            )
            db.execute(
                "UPDATE user_feedback SET review_task_id=? WHERE feedback_id=?",
                (task_id, fb.feedback_id)
            )
            fb.review_task_id = task_id

        db.commit()
        return fb

    def get_stale_documents(self, days_threshold: int = 90) -> list[dict]:
        """
        Documents stuck in early processing stages for > N days.
        These indicate pipeline failures that need investigation.
        """
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days_threshold)).isoformat()
        early_statuses = ("acquired", "extracted", "normalized", "metadata_enriched", "chunked")
        placeholders = ",".join("?" * len(early_statuses))
        rows = self._db().execute(
            f"""SELECT document_id, title, processing_status, grade, subject,
                       document_type, updated_at, created_at,
                       julianday('now') - julianday(updated_at) AS days_stale
                FROM documents
                WHERE processing_status IN ({placeholders})
                  AND updated_at < ?
                ORDER BY days_stale DESC""",
            [*early_statuses, cutoff]
        ).fetchall()
        return [dict(r) for r in rows]

    def get_feedback_summary(self, days: int = 30) -> dict:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        rows = self._db().execute(
            "SELECT feedback_type, COUNT(*) as cnt FROM user_feedback "
            "WHERE created_at > ? GROUP BY feedback_type",
            (cutoff,)
        ).fetchall()
        return {r["feedback_type"]: r["cnt"] for r in rows}

    def get_job_failure_rate(self, hours: int = 24) -> dict:
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        rows = self._db().execute(
            "SELECT status, COUNT(*) as cnt FROM processing_jobs "
            "WHERE started_at > ? GROUP BY status",
            (cutoff,)
        ).fetchall()
        d = {r["status"]: r["cnt"] for r in rows}
        total = sum(d.values())
        failed = d.get("failed", 0)
        return {
            "total": total, "failed": failed, "success": d.get("success", 0),
            "running": d.get("running", 0),
            "failure_rate": round(failed / max(total, 1), 3),
        }

    def get_monitoring_report(self) -> MonitoringReport:
        """
        Generate a full pipeline health snapshot.
        Includes stale docs, failure rates, feedback, and alerts.
        """
        stats = self.get_pipeline_stats()
        stale = self.get_stale_documents()
        feedback = self.get_feedback_summary(days=30)
        jobs = self.get_job_failure_rate(hours=24)

        # Ingestion rate last 7 days
        cutoff_7d = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        ing_row = self._db().execute(
            "SELECT COUNT(*) as n FROM documents WHERE created_at > ?", (cutoff_7d,)
        ).fetchone()
        ingestion_rate = ing_row["n"] if ing_row else 0

        # Approval rate last 30 days
        cutoff_30d = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        appr = self._db().execute(
            "SELECT COUNT(*) as n FROM documents WHERE processing_status='approved' "
            "AND updated_at > ?", (cutoff_30d,)
        ).fetchone()["n"]
        rej = self._db().execute(
            "SELECT COUNT(*) as n FROM documents WHERE processing_status='rejected' "
            "AND updated_at > ?", (cutoff_30d,)
        ).fetchone()["n"]
        approval_rate = round(appr / max(appr + rej, 1), 3)

        # Build alerts
        alerts: list[str] = []
        if jobs["failure_rate"] > 0.20:
            alerts.append(f"HIGH job failure rate: {jobs['failure_rate']*100:.0f}% in last 24h.")
        if stats.get("pending_reviews", 0) > 50:
            alerts.append(f"{stats['pending_reviews']} documents pending human review.")
        if stale:
            alerts.append(f"{len(stale)} documents have been stale for >90 days.")
        if approval_rate < 0.50 and (appr + rej) > 10:
            alerts.append(f"Low approval rate: {approval_rate*100:.0f}% in last 30 days.")
        if feedback.get("incorrect_answer", 0) > 10:
            alerts.append(f"{feedback['incorrect_answer']} 'incorrect_answer' reports in last 30 days.")

        return MonitoringReport(
            generated_at=_now(),
            total_documents=stats.get("total", 0),
            ingestion_rate_7d=ingestion_rate,
            approval_rate=approval_rate,
            avg_quality_score=stats.get("avg_quality_score", 0.0),
            stale_documents=stale[:20],
            failed_jobs_24h=jobs["failed"],
            pending_reviews=stats.get("pending_reviews", 0),
            extraction_failure_rate=jobs["failure_rate"],
            feedback_summary=feedback,
            alerts=alerts,
        )

    def get_completeness_report(self) -> dict:
        """Weekly-style report: what's missing by grade × subject."""
        from itertools import product
        all_grades   = list(range(1, 13))
        all_subjects = ["mathematics","english","science","history","geography",
                        "accounting","economics","life_sciences","physical_sciences"]
        required_types = ["textbook","lesson_plan","past_paper","assessment_rubric"]

        approved = self._db().execute(
            "SELECT grade, subject, document_type FROM documents "
            "WHERE processing_status IN ('approved','indexed','training_ready')"
        ).fetchall()
        have: set[tuple] = {(r["grade"], r["subject"], r["document_type"]) for r in approved}

        missing = []
        for g, s, t in product(all_grades, all_subjects, required_types):
            if (g, s, t) not in have:
                missing.append({"grade": g, "subject": s, "document_type": t})

        total_required = len(all_grades) * len(all_subjects) * len(required_types)
        coverage = round((total_required - len(missing)) / total_required * 100, 1)
        return {
            "total_required": total_required,
            "total_present":  total_required - len(missing),
            "coverage_pct":   coverage,
            "missing_count":  len(missing),
            "missing":        missing[:100],  # cap for API response size
        }
