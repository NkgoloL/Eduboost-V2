"""Comprehensive unit tests for ETL pipeline v2 dataclasses and schema extension."""
from __future__ import annotations

import pytest

from app.services.etl.etl_pipeline_v2 import (
    DocumentVersion,
    TrainingDataset,
    SCHEMA_V2_SQL,
)


class TestETLPipelineV2Dataclasses:
    def test_document_version_dataclass(self):
        ver = DocumentVersion(
            version_id="v-123",
            document_id="doc-456",
            version_number="1.0",
            change_summary="Initial upload",
            created_by="admin",
            created_at="2026-08-28T10:00:00Z",
        )
        assert ver.version_id == "v-123"
        assert ver.version_number == "1.0"
        assert ver.snapshot_path is None

    def test_training_dataset_dataclass(self):
        ds = TrainingDataset(
            dataset_id="ds-789",
            name="grade4_maths_qa",
            description="Grade 4 maths question-answer pairs",
            dataset_type="qa_pairs",
            version="1.0",
            split="train",
            document_ids=["doc-456", "doc-457"],
            example_count=50,
            is_synthetic=True,
        )
        assert ds.dataset_id == "ds-789"
        assert ds.example_count == 50
        assert ds.is_synthetic is True
        assert len(ds.document_ids) == 2

    def test_schema_v2_sql_tables(self):
        assert "CREATE TABLE IF NOT EXISTS document_versions" in SCHEMA_V2_SQL
        assert "CREATE TABLE IF NOT EXISTS curriculum_mappings" in SCHEMA_V2_SQL
        assert "CREATE TABLE IF NOT EXISTS chunk_embeddings" in SCHEMA_V2_SQL
        assert "CREATE TABLE IF NOT EXISTS training_datasets" in SCHEMA_V2_SQL
        assert "CREATE TABLE IF NOT EXISTS training_examples" in SCHEMA_V2_SQL
        assert "CREATE TABLE IF NOT EXISTS pipeline_metrics" in SCHEMA_V2_SQL
        assert "CREATE TABLE IF NOT EXISTS user_feedback" in SCHEMA_V2_SQL
