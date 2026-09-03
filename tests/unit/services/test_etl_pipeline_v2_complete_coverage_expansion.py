"""Complete branch coverage expansion for EduboostETLv2."""
from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.services.etl.etl_pipeline import DocumentChunk, IngestRequest
from app.services.etl.etl_pipeline_v2 import (
    EduboostETLv2,
    HAS_NUMPY,
    HAS_PARQUET,
    DocumentVersion,
    FeedbackRecord,
    MonitoringReport,
    TrainingDataset,
    TrainingExample,
)



@pytest.fixture
def etl_v2():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_etl.db"
        pipeline = EduboostETLv2(db_url=f"sqlite:///{db_path}", storage_root=tmpdir)
        pipeline.init_db()
        pipeline.init_fts()
        yield pipeline


def _create_sample_doc(etl: EduboostETLv2, filename: str, content: str, **kwargs) -> str:
    temp_file = etl.storage_root / filename
    temp_file.write_text(content, encoding="utf-8")
    req = IngestRequest(
        file_path=str(temp_file),
        title=kwargs.get("title", filename),
        grade=kwargs.get("grade", 4),
        subject=kwargs.get("subject", "Mathematics"),
        document_type=kwargs.get("document_type", "textbook"),
    )
    doc = etl.ingest(req)
    return doc.document_id


def test_document_versions_and_curriculum_mappings(etl_v2: EduboostETLv2):
    # 1. Ingest a document and create versions
    doc_id = _create_sample_doc(etl_v2, "test.txt", "Fractions Basics sample content", title="Fractions Basics", grade=4, subject="Mathematics")

    # Create document version
    ver_id = etl_v2.create_version(
        document_id=doc_id,
        change_summary="Initial release",
        created_by="editor_1",
    )
    assert ver_id is not None

    versions = etl_v2.list_versions(doc_id)
    assert len(versions) >= 1
    assert versions[0]["change_summary"] == "Initial release"

    # Add curriculum mapping
    map_id = etl_v2.add_curriculum_mapping(
        document_id=doc_id,
        chunk_id=None,
        curriculum="CAPS",
        grade=4,
        subject="Mathematics",
        topic_code="CAPS-G4-MATH-FRACTIONS",
        learning_outcome="Understand equivalent fractions",
    )
    assert map_id is not None

    # Update metadata
    etl_v2.update_document_metadata(doc_id, {"description": "Updated fractions doc"})
    
    # Deprecate document
    dep = etl_v2.deprecate_document(doc_id, reason="Superseded by v2")
    assert dep["status"] == "archived"


def test_search_fulltext_and_indexing(etl_v2: EduboostETLv2):
    doc_id = _create_sample_doc(etl_v2, "fractions.txt", "Equivalent fractions content", title="Grade 5 Fractions", grade=5, subject="Mathematics", document_type="textbook")
    
    # Update document status to approved
    db = etl_v2._db()
    db.execute("UPDATE documents SET processing_status='approved' WHERE document_id=?", (doc_id,))
    db.commit()

    chunk = DocumentChunk(
        chunk_id="chunk-1",
        document_id=doc_id,
        chunk_type="concept",
        chunk_index=0,
        parent_chunk_id=None,
        heading="Equivalent Fractions",
        content="Equivalent fractions have the same value even though they look different.",
        token_count=15,
        page_start=1,
        page_end=2,
        section_path="Chapter 1 > Fractions",
        curriculum_code="CAPS-G5-MATH",
        created_at="2026-01-01T00:00:00",
    )
    db.execute(
        "INSERT INTO document_chunks (chunk_id, document_id, chunk_type, chunk_index, parent_chunk_id, "
        "heading, content, token_count, page_start, page_end, section_path, curriculum_code, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (chunk.chunk_id, chunk.document_id, chunk.chunk_type, chunk.chunk_index, chunk.parent_chunk_id,
         chunk.heading, chunk.content, chunk.token_count, chunk.page_start, chunk.page_end,
         chunk.section_path, chunk.curriculum_code, chunk.created_at),
    )
    db.commit()

    etl_v2.index_chunk_for_search(chunk)
    etl_v2.mark_indexed(doc_id)

    # 1. Search fulltext (FTS5 path) with filters
    results = etl_v2.search_fulltext("equivalent", grade=5, subject="Mathematics", document_type="textbook")
    assert len(results) >= 1
    assert results[0]["chunk_id"] == "chunk-1"
    assert "citation" in results[0]
    assert results[0]["citation"]["title"] == "Grade 5 Fractions"

    # 2. Search fulltext with no matching query
    no_results = etl_v2.search_fulltext("quantum physics")
    assert len(no_results) == 0

    # 3. Get document chunks
    chunks = etl_v2.get_document_chunks(doc_id)
    assert len(chunks) == 1


def test_embeddings_and_semantic_search(etl_v2: EduboostETLv2):
    doc_id = _create_sample_doc(etl_v2, "geo.txt", "Map skills content", title="Map Skills", grade=6, subject="Geography")

    db = etl_v2._db()
    db.execute("UPDATE documents SET processing_status='approved' WHERE document_id=?", (doc_id,))
    db.commit()

    chunk_geo = DocumentChunk(
        chunk_id="chunk-geo-1",
        document_id=doc_id,
        chunk_type="concept",
        chunk_index=0,
        parent_chunk_id=None,
        heading="Latitude",
        content="Latitude lines run east to west around the Earth.",
        token_count=10,
        page_start=1,
        page_end=1,
        section_path="Maps",
        curriculum_code="CAPS-G6-GEO",
        created_at="2026-01-01T00:00:00",
    )
    db.execute(
        "INSERT INTO document_chunks (chunk_id, document_id, chunk_type, chunk_index, parent_chunk_id, "
        "heading, content, token_count, page_start, page_end, section_path, curriculum_code, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (chunk_geo.chunk_id, chunk_geo.document_id, chunk_geo.chunk_type, chunk_geo.chunk_index, chunk_geo.parent_chunk_id,
         chunk_geo.heading, chunk_geo.content, chunk_geo.token_count, chunk_geo.page_start, chunk_geo.page_end,
         chunk_geo.section_path, chunk_geo.curriculum_code, chunk_geo.created_at),
    )
    db.commit()

    etl_v2.index_chunk_for_search(chunk_geo)

    # Store embedding
    emb_vec = [0.1, 0.2, 0.3, 0.4]
    emb_id = etl_v2.store_embedding("chunk-geo-1", doc_id, emb_vec, model_name="test-embed-v1")
    assert emb_id is not None

    # Semantic search
    hits = etl_v2.semantic_search_stub(query_embedding=[0.1, 0.2, 0.3, 0.4], grade=6, subject="Geography", limit=5)
    assert len(hits) >= 1
    assert hits[0]["chunk_id"] == "chunk-geo-1"
    assert "score" in hits[0]

    # Hybrid search
    hybrid_hits = etl_v2.hybrid_search(
        query="Latitude",
        query_embedding=[0.1, 0.2, 0.3, 0.4],
        grade=6,
        subject="Geography",
        limit=5,
    )
    assert len(hybrid_hits) >= 1
    assert hybrid_hits[0]["chunk_id"] == "chunk-geo-1"


def test_training_dataset_generation_and_export(etl_v2: EduboostETLv2):
    doc_id = _create_sample_doc(etl_v2, "hist.txt", "Ancient Egypt history", title="Ancient Egypt", grade=7, subject="History")

    db = etl_v2._db()
    db.execute("UPDATE documents SET processing_status='approved' WHERE document_id=?", (doc_id,))
    
    # Text with explicit Q&A patterns to exercise _extract_qa_candidates and summaries
    content_text = (
        "The Nile River was central to Ancient Egyptian civilization. "
        "Question: Why was the Nile important to Ancient Egypt? "
        "Answer: The Nile provided fertile soil for agriculture through annual flooding. "
        "In summary, geography shaped Egyptian society."
    )
    db.execute(
        "INSERT INTO document_chunks (chunk_id, document_id, chunk_type, chunk_index, parent_chunk_id, "
        "heading, content, token_count, page_start, page_end, section_path, curriculum_code, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("chunk-hist-1", doc_id, "narrative", 0, None, "The Nile",
         content_text, 60, 1, 2, "Chapter 1", "CAPS-G7-HIST", "2026-01-01T00:00:00"),
    )
    db.commit()

    # Generate training dataset
    dataset = etl_v2.generate_training_dataset(document_ids=[doc_id], example_type="qa", dataset_name="history-qa")
    dataset_id = dataset.dataset_id
    assert dataset.example_count >= 1

    # List datasets and get examples
    datasets = etl_v2.list_training_datasets()
    assert len(datasets) >= 1
    examples = etl_v2.get_training_examples(dataset_id)
    assert len(examples) >= 1

    # Export dataset in JSONL and CSV formats
    with tempfile.TemporaryDirectory() as export_dir:
        jsonl_path = etl_v2.export_dataset(dataset_id, fmt="jsonl", out_dir=export_dir)
        assert Path(jsonl_path).exists()
        assert Path(jsonl_path).stat().st_size > 0

        csv_path = etl_v2.export_dataset(dataset_id, fmt="csv", out_dir=export_dir)
        assert Path(csv_path).exists()
        assert Path(csv_path).stat().st_size > 0

        # Parquet export (if available)
        if HAS_PARQUET:
            pq_path = etl_v2.export_dataset(dataset_id, fmt="parquet", out_dir=export_dir)
            assert Path(pq_path).exists()

    # Create second dataset for contamination check
    dataset2 = etl_v2.generate_training_dataset(document_ids=[doc_id], example_type="summary", dataset_name="history-summary")
    contamination_report = etl_v2.contamination_check(dataset_id, dataset2.dataset_id)
    assert "contamination_pct" in contamination_report


    # Mark training ready
    status = etl_v2.mark_training_ready(doc_id)
    assert status == "training_ready"


def test_monitoring_feedback_and_stale_content(etl_v2: EduboostETLv2):
    doc_id = _create_sample_doc(etl_v2, "sci.txt", "Energy science content", title="Energy", grade=4, subject="Science")

    # 1. Record metric
    etl_v2.record_metric(name="etl_latency", value=42.5, tags={"doc": doc_id})

    # 2. Submit feedback
    fb_id = etl_v2.submit_feedback(
        document_id=doc_id,
        feedback_type="factual_error",
        user_id="educator_1",
        details="Potential discrepancy in kinetic energy definition.",
    )
    assert fb_id is not None

    summary = etl_v2.get_feedback_summary(days=30)
    assert "factual_error" in summary


    # 3. Detect stale documents & failure rates
    stale_docs = etl_v2.get_stale_documents(days_threshold=0)
    assert isinstance(stale_docs, list)

    fail_rate = etl_v2.get_job_failure_rate(hours=24)
    assert "failure_rate" in fail_rate

    # 4. Monitoring health report & completeness report
    report = etl_v2.get_monitoring_report()
    assert isinstance(report, MonitoringReport)
    assert report.total_documents >= 1

    comp_report = etl_v2.get_completeness_report()
    assert "total_present" in comp_report


def test_etl_pipeline_v2_edge_branches(etl_v2: EduboostETLv2):
    # 1. Fulltext search LIKE fallback when FTS raises OperationalError
    mock_db = MagicMock()
    mock_db.execute.side_effect = [
        sqlite3.OperationalError("fts error"),
        MagicMock(fetchall=MagicMock(return_value=[])),
    ]
    with patch.object(etl_v2, "_db", return_value=mock_db):
        res = etl_v2.search_fulltext("test query", grade=4, subject="Science", document_type="textbook")
        assert res == []



    # 2. Generate training dataset with concept and rubric types
    doc_id = _create_sample_doc(etl_v2, "concepts.txt", "Concept: Osmosis is water diffusion. Rubric: Award 2 marks for correct definition.", title="Biology Concepts")
    db = etl_v2._db()
    db.execute("UPDATE documents SET processing_status='approved' WHERE document_id=?", (doc_id,))
    db.execute(
        "INSERT INTO document_chunks (chunk_id, document_id, chunk_type, chunk_index, parent_chunk_id, "
        "heading, content, token_count, page_start, page_end, section_path, curriculum_code, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("chunk-bio-1", doc_id, "concept", 0, None, "Osmosis",
         "Concept: Osmosis is water diffusion. Rubric: Award 2 marks for definition.", 20, 1, 1, "Ch 1", "CAPS-BIO", "2026-01-01T00:00:00"),
    )
    db.commit()

    ds_concept = etl_v2.generate_training_dataset(document_ids=[doc_id], example_type="concept", dataset_name="bio-concepts")
    assert ds_concept.dataset_id is not None

    ds_rubric = etl_v2.generate_training_dataset(document_ids=[doc_id], example_type="rubric", dataset_name="bio-rubrics")
    assert ds_rubric.dataset_id is not None

    # 3. Export dataset unsupported format
    with pytest.raises(ValueError, match="Unsupported format"):
        etl_v2.export_dataset(ds_concept.dataset_id, fmt="unsupported_fmt")

    # 4. Export dataset non-existent dataset returns empty string
    assert etl_v2.export_dataset("non-existent-ds-id", fmt="jsonl") == ""


    # 5. Export dataset parquet when HAS_PARQUET is False
    with patch("app.services.etl.etl_pipeline_v2.HAS_PARQUET", False):
        with pytest.raises(RuntimeError, match="pyarrow is required"):
            etl_v2.export_dataset(ds_concept.dataset_id, fmt="parquet")

    # 6. Index chunk FTS error branch
    mock_db_fts = MagicMock()
    mock_db_fts.execute.side_effect = sqlite3.OperationalError("fts disabled")
    with patch.object(etl_v2, "_db", return_value=mock_db_fts):
        etl_v2.index_chunk_for_search(MagicMock(chunk_id="c1", document_id="d1", heading="h", content="c", section_path="s"))

    # 7. Update document metadata non-existent doc
    with pytest.raises(ValueError, match="Document not found"):
        etl_v2.update_document_metadata("non-existent-doc", {"title": "new"})

    # 8. Monitoring report alerts branches
    with patch.object(etl_v2, "get_job_failure_rate", return_value={"failed": 5, "total": 10, "failure_rate": 0.5}), \
         patch.object(etl_v2, "get_pipeline_stats", return_value={"total": 100, "pending_reviews": 60, "avg_quality_score": 0.8}), \
         patch.object(etl_v2, "get_stale_documents", return_value=[{"document_id": "d1"}]), \
         patch.object(etl_v2, "get_feedback_summary", return_value={"incorrect_answer": 15}):
        # Mock approval and rejection counts to trigger approval_rate < 0.50 with (appr+rej) > 10
        mock_db_appr = MagicMock()
        mock_db_appr.execute.side_effect = [
            MagicMock(fetchone=MagicMock(return_value={"n": 5})),   # ingestion_rate
            MagicMock(fetchone=MagicMock(return_value={"n": 2})),   # appr
            MagicMock(fetchone=MagicMock(return_value={"n": 10})),  # rej
        ]
        with patch.object(etl_v2, "_db", return_value=mock_db_appr):
            rep = etl_v2.get_monitoring_report()
            assert len(rep.alerts) >= 5

    # 9. Semantic search without numpy
    with patch("app.services.etl.etl_pipeline_v2.HAS_NUMPY", False):
        res_no_numpy = etl_v2.semantic_search_stub([0.1, 0.2])
        assert "warning" in res_no_numpy[0]

    # 10. Completeness report with matching document
    doc_match_id = _create_sample_doc(etl_v2, "math1.txt", "Math 1 text", grade=1, subject="mathematics", document_type="textbook")
    etl_v2._db().execute("UPDATE documents SET processing_status='approved' WHERE document_id=?", (doc_match_id,))
    etl_v2._db().commit()
    comp_rep2 = etl_v2.get_completeness_report()
    assert comp_rep2["total_present"] >= 1





