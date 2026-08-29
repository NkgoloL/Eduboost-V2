import os
import sqlite3
import tempfile
import pytest
from pathlib import Path

from app.services.etl.etl_pipeline_v2 import (
    EduboostETLv2,
    DocumentVersion,
    TrainingDataset,
    TrainingExample,
    FeedbackRecord,
    MonitoringReport,
)


def test_v2_dataclasses_initialization():
    v = DocumentVersion(
        version_id="v-1",
        document_id="doc-1",
        version_number="1.0",
        change_summary="Initial import",
        created_by="admin",
        created_at="2026-08-29T12:00:00Z",
    )
    assert v.version_id == "v-1"
    assert v.version_number == "1.0"

    ds = TrainingDataset(
        dataset_id="ds-1",
        name="Grade 4 Maths QA",
        description="Curriculum QA pairs",
        dataset_type="qa_pairs",
        version="1.0",
        split="train",
        document_ids=["doc-1", "doc-2"],
    )
    assert ds.dataset_id == "ds-1"
    assert ds.created_at != ""

    ex = TrainingExample(
        example_id="ex-1",
        dataset_id="ds-1",
        document_id="doc-1",
        chunk_id="chunk-1",
        example_type="qa",
        input_text="What is a fraction?",
        output_text="A fraction represents a part of a whole.",
    )
    assert ex.example_id == "ex-1"
    assert ex.created_at != ""

    fb = FeedbackRecord(
        feedback_id="fb-1",
        document_id="doc-1",
        chunk_id=None,
        user_id="user-42",
        feedback_type="incorrect_answer",
        details="Answer on page 2 is wrong.",
    )
    assert fb.feedback_id == "fb-1"
    assert fb.resolved is False


def test_eduboost_etl_v2_init_db_and_fts():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_etl.db"
        storage_root = Path(tmpdir) / "storage"

        etl = EduboostETLv2(db_url=f"sqlite:///{db_path}", storage_root=storage_root)
        etl.init_db()
        etl.init_fts()

        # Query sqlite_master to verify tables created
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

        assert "document_versions" in tables
        assert "curriculum_mappings" in tables
        assert "training_datasets" in tables
        assert "training_examples" in tables
        assert "user_feedback" in tables
        conn.close()
