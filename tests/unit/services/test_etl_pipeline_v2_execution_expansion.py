"""Comprehensive unit tests for EduboostETLv2 Phase 8-12 extensions."""
from __future__ import annotations

import sqlite3
from pathlib import Path
import pytest

from app.services.etl.etl_pipeline_v2 import (
    EduboostETLv2,
    SCHEMA_V2_SQL,
)


class TestEduboostETLv2Lifecycle:
    def test_init_db_and_fts_in_memory(self, tmp_path):
        db_path = tmp_path / "test_etl.db"
        etl = EduboostETLv2(db_url=f"sqlite:///{db_path}", storage_root=str(tmp_path))
        etl.init_db()
        etl.init_fts()

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
            assert "documents" in tables
            assert "document_versions" in tables
            assert "curriculum_mappings" in tables
            assert "chunk_embeddings" in tables
            assert "training_datasets" in tables
            assert "training_examples" in tables
            assert "pipeline_metrics" in tables
            assert "user_feedback" in tables

    def test_record_metric_and_feedback(self, tmp_path):
        db_path = tmp_path / "test_etl_metrics.db"
        etl = EduboostETLv2(db_url=f"sqlite:///{db_path}", storage_root=str(tmp_path))
        etl.init_db()

        etl.record_metric(name="ingestion_count", value=42.0, tags={"grade": "4"})
        etl.submit_feedback(
            document_id="doc-123",
            feedback_type="typo",
            user_id="teacher_1",
            details="Typo in equation on page 2",
        )

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT metric_name, metric_value FROM pipeline_metrics")
            m = cursor.fetchone()
            assert m[0] == "ingestion_count"
            assert m[1] == 42.0

            cursor.execute("SELECT feedback_type, user_id, details FROM user_feedback")
            f = cursor.fetchone()
            assert f[0] == "typo"
            assert f[1] == "teacher_1"
            assert "Typo in equation" in f[2]
