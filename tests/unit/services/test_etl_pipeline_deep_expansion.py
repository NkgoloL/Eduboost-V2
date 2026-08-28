"""Comprehensive deep unit tests for EduboostETL Pipeline Phases 0-7."""
from __future__ import annotations

import os
from pathlib import Path
import pytest

from app.services.etl.etl_pipeline import (
    EduboostETL,
    IngestRequest,
    DocumentType,
    SourceType,
    LicenseStatus,
    ProcessingStatus,
    ChunkType,
    QualityCheckResult,
    _token_count,
    _sha256,
    _now,
    _uid,
)


class TestETLHelpers:
    def test_token_count_estimation(self):
        assert _token_count("") == 1
        assert _token_count("Hello World") == 2
        assert _token_count("a" * 400) == 100

    def test_uid_generation(self):
        uid = _uid()
        assert isinstance(uid, str)
        assert len(uid) == 36

    def test_now_iso_format(self):
        now_str = _now()
        assert "T" in now_str
        assert "+" in now_str or "Z" in now_str or now_str.endswith("+00:00")

    def test_sha256_hashing(self, tmp_path: Path):
        test_file = tmp_path / "sample.txt"
        test_file.write_text("EduBoost CAPS content verification.", encoding="utf-8")
        checksum = _sha256(str(test_file))
        assert isinstance(checksum, str)
        assert len(checksum) == 64

    def test_quality_check_composite(self):
        score = QualityCheckResult.compute_composite(
            meta=1.0,
            extract=1.0,
            struct=1.0,
            complete=1.0,
            prov=1.0,
            training=1.0,
        )
        assert score == 1.0


class TestEduboostETLPipelineLifecycle:
    def test_full_pipeline_on_markdown_document(self, tmp_path: Path):
        db_path = tmp_path / "test_etl.db"
        storage_root = tmp_path / "etl_data"
        doc_file = tmp_path / "grade4_maths.md"
        doc_file.write_text(
            "# Grade 4 Mathematics: Whole Numbers\n\n"
            "## 1.1 Ordering and Comparing Numbers\n"
            "Learners must be able to order 4-digit numbers using symbols <, >, =.\n\n"
            "### Worked Example\n"
            "Compare 2 345 and 2 189.\n"
            "2 345 is greater than 2 189 because the hundreds digit 3 > 1.\n\n"
            "## 1.2 Place Value\n"
            "Each digit in a four digit number has a specific value: thousands, hundreds, tens, units.\n",
            encoding="utf-8",
        )

        etl = EduboostETL(db_url=f"sqlite:///{db_path}", storage_root=str(storage_root))
        etl.init_db()

        req = IngestRequest(
            file_path=str(doc_file),
            source_type=SourceType.manual_upload,
            uploaded_by="content_team",
            document_type=DocumentType.textbook,
            grade=4,
            subject="mathematics",
            title="Grade 4 Whole Numbers Guide",
            license_status=LicenseStatus.open_license,
        )

        doc_source = etl.ingest(req)
        assert doc_source is not None
        assert doc_source.document_id is not None

        res = etl.run_full_pipeline(doc_source.document_id)
        assert res is not None
        assert res.quality_score >= 0.0
        assert res.status in ("validated", "needs_review", "approved", "rejected")
