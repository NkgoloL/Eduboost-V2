"""Batch 209: Unit tests for etl_pipeline_v2.py covering Phases 8-12 (Versioning, FTS/Search, Embeddings, Dataset Builder, Feedback & Monitoring)."""
import os
import json
import pytest
from pathlib import Path

from app.services.etl.etl_pipeline import (
    DocumentType,
    SourceType,
    ProcessingStatus,
    LicenseStatus,
    IngestRequest,
)
from app.services.etl.etl_pipeline_v2 import (
    EduboostETLv2,
    DocumentVersion,
    TrainingDataset,
    TrainingExample,
    FeedbackRecord,
    MonitoringReport,
)


@pytest.fixture
def etl_v2(tmp_path):
    db_path = tmp_path / "etl_v2_test.db"
    storage_dir = tmp_path / "v2_storage"
    etl = EduboostETLv2(db_url=f"sqlite:///{db_path}", storage_root=str(storage_dir))
    etl.init_db()
    etl.init_fts()
    yield etl
    etl.close()


class TestEduboostETLv2Phases:
    def test_versioning_and_metadata_updates(self, etl_v2, tmp_path):
        # Create a document
        doc_file = tmp_path / "doc.txt"
        doc_file.write_text("# Chapter 1\n\nContent for testing versioning.")
        
        req = IngestRequest(
            file_path=str(doc_file),
            source_type=SourceType.manual_upload,
            document_type=DocumentType.textbook,
            license_status=LicenseStatus.open_license,
        )
        doc = etl_v2.ingest(req)
        etl_v2.run_full_pipeline(doc.document_id)
        
        # Test creating versions
        v1 = etl_v2.create_version(doc.document_id, change_summary="Initial version")
        assert isinstance(v1, DocumentVersion)
        assert v1.version_number == "1.0"
        
        v2 = etl_v2.create_version(doc.document_id, change_summary="Second minor update")
        assert v2.version_number == "1.1"

        versions = etl_v2.list_versions(doc.document_id)
        assert len(versions) == 2

        # Test metadata update auto-versioning
        res = etl_v2.update_document_metadata(
            doc.document_id,
            {"title": "Updated Grade 6 Maths", "grade": 6, "subject": "mathematics"},
            updated_by="editor_1"
        )
        assert res["updated"] == 3
        
        # Test soft-delete deprecation
        dep = etl_v2.deprecate_document(doc.document_id, reason="Superseded by new syllabus")
        assert dep["status"] == "archived"

    def test_curriculum_mappings_and_chunk_retrieval(self, etl_v2, tmp_path):
        doc_file = tmp_path / "math_sample.txt"
        doc_file.write_text("Lesson 1: Addition of numbers.\n\nPractice adding 1 + 2 = 3.")
        req = IngestRequest(
            file_path=str(doc_file),
            document_type=DocumentType.lesson_plan,
            license_status=LicenseStatus.open_license,
        )
        doc = etl_v2.ingest(req)
        etl_v2.run_full_pipeline(doc.document_id)

        chunks = etl_v2.get_document_chunks(doc.document_id)
        assert len(chunks) > 0
        chunk_id = chunks[0]["chunk_id"]

        mapping_id = etl_v2.add_curriculum_mapping(
            document_id=doc.document_id,
            chunk_id=chunk_id,
            grade=4,
            subject="mathematics",
            topic_code="CAPS-G4-MATH-ADDITION",
            learning_outcome="Perform addition of whole numbers"
        )
        assert mapping_id is not None

    def test_search_and_embedding_pipeline(self, etl_v2, tmp_path):
        doc_file = tmp_path / "search_doc.txt"
        doc_file.write_text("# Photosynthesis in Plants\n\nGreen plants make food using sunlight and chlorophyll.")
        req = IngestRequest(
            file_path=str(doc_file),
            document_type=DocumentType.textbook,
            grade=8,
            subject="science",
            license_status=LicenseStatus.open_license,
        )
        doc = etl_v2.ingest(req)
        etl_v2.run_full_pipeline(doc.document_id)
        etl_v2.approve_document(doc.document_id, reviewer="lead")
        etl_v2._populate_fts()

        # Full-text search
        hits = etl_v2.search_fulltext("Photosynthesis", grade=8, subject="science")
        assert len(hits) > 0
        assert "Photosynthesis" in hits[0]["content"] or "Photosynthesis" in hits[0]["heading"]
        assert "citation" in hits[0]

        # Storing embeddings
        chunks = etl_v2.get_document_chunks(doc.document_id)
        emb_id = etl_v2.store_embedding(chunks[0]["chunk_id"], doc.document_id, [0.1, 0.2, 0.3, 0.4])
        assert emb_id is not None

    def test_feedback_and_monitoring_reports(self, etl_v2, tmp_path):
        doc_file = tmp_path / "feedback_doc.txt"
        doc_file.write_text("Basic facts on Geography.")
        req = IngestRequest(file_path=str(doc_file), document_type=DocumentType.textbook)
        doc = etl_v2.ingest(req)
        etl_v2.run_full_pipeline(doc.document_id)

        # Submit feedback
        fb = etl_v2.submit_feedback(
            document_id=doc.document_id,
            user_id="user_123",
            feedback_type="incorrect_answer",
            details="Typo in coordinates."
        )
        assert isinstance(fb, FeedbackRecord)
        assert fb.resolved is False

        # Get monitoring report
        report = etl_v2.get_monitoring_report()
        assert isinstance(report, MonitoringReport)
        assert report.total_documents >= 1
