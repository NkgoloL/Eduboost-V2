"""Batch 208: Comprehensive unit tests for etl_pipeline.py covering all phases (Extractor, Normalizer, Chunker, QualityValidator, EduboostETL orchestration)."""
import os
import tempfile
from pathlib import Path
import pytest

from app.services.etl.etl_pipeline import (
    DocumentType,
    SourceType,
    ProcessingStatus,
    LicenseStatus,
    ChunkType,
    DocumentSource,
    Document,
    DocumentChunk,
    QualityCheckResult,
    IngestRequest,
    Extractor,
    Normalizer,
    Chunker,
    QualityValidator,
    EduboostETL,
    _token_count,
    _sha256,
)


# ─────────────────────────────────────────────
# Helper & Extraction Layer Tests
# ─────────────────────────────────────────────


class TestETLExtractor:
    def test_token_count(self):
        assert _token_count("") == 1
        assert _token_count("hello world") == max(1, len("hello world") // 4)

    def test_extract_txt_and_markdown(self, tmp_path):
        extractor = Extractor()
        test_file = tmp_path / "sample.md"
        test_file.write_text("# Chapter 1: Introduction\n\nThis is basic text for testing.")
        
        res = extractor.extract(str(test_file))
        assert res.extraction_ok is True
        assert res.mime_type == "text/markdown"
        assert "Chapter 1: Introduction" in res.headings
        assert res.page_count == 1
        assert "This is basic text" in res.raw_text

    def test_extract_html(self, tmp_path):
        extractor = Extractor()
        test_file = tmp_path / "sample.html"
        test_file.write_text("<html><body><h1>Section Title</h1><p>Paragraph content</p></body></html>")
        
        res = extractor.extract(str(test_file))
        assert res.extraction_ok is True
        assert res.mime_type == "text/html"
        assert "Paragraph content" in res.raw_text

    def test_extract_csv(self, tmp_path):
        extractor = Extractor()
        test_file = tmp_path / "data.csv"
        test_file.write_text("col1,col2\nval1,val2\nval3,val4")
        
        res = extractor.extract(str(test_file))
        assert res.extraction_ok is True
        assert res.mime_type == "text/csv"
        assert "col1" in res.raw_text

    def test_extract_missing_file(self):
        extractor = Extractor()
        res = extractor.extract("/non/existent/path/doc.pdf")
        assert res.extraction_ok is False
        assert res.error is not None


# ─────────────────────────────────────────────
# Normalizer & Metadata Inference Tests
# ─────────────────────────────────────────────


class TestETLNormalizer:
    def test_normalize_clean_artifacts_and_detect_language(self):
        normalizer = Normalizer()
        raw = "Page 1 of 10   Some   text with  l\b OCR artifact and   spaces.\n\n\n\nEnd."
        res = normalizer.normalize(raw, DocumentType.textbook)
        
        assert "Page 1 of 10" not in res["normalized_text"]
        assert "   " not in res["normalized_text"]
        assert res["language"] == "en"
        assert res["word_count"] > 0

    def test_detect_afrikaans_language(self):
        normalizer = Normalizer()
        raw = "Hierdie is die boek van die skool en dat het nie met die werk te doen nie."
        res = normalizer.normalize(raw, DocumentType.textbook)
        assert res["language"] == "af"

    def test_infer_metadata_grade_subject_phase(self):
        normalizer = Normalizer()
        doc = Document(
            document_id="d1", source_id="s1", title="Untitled", description="",
            document_type=DocumentType.textbook, subject=None, grade=None,
            phase=None, curriculum=None, country="ZA", province=None, language="en",
            publisher=None, author=None, publication_year=None, version="1.0",
            license_status=LicenseStatus.unknown, source_url=None, checksum="abc",
            file_path_raw="", file_size_bytes=100, page_count=1, mime_type="text/plain",
            processing_status=ProcessingStatus.raw, quality_score=0.0,
            training_readiness=False, created_at="", updated_at="",
        )
        sample_text = "Mathematics for Grade 5 learners.\nPublished in 2022.\nChapter 1 Algebra."
        updates = normalizer.infer_metadata(sample_text, doc)
        
        assert updates.get("grade") == 5
        assert updates.get("subject") == "mathematics"
        assert updates.get("phase") == "Intermediate Phase"
        assert updates.get("publication_year") == 2022
        assert updates.get("title") is not None


# ─────────────────────────────────────────────
# Chunker & QualityValidator Tests
# ─────────────────────────────────────────────


class TestETLChunker:
    def test_chunk_legal_document(self):
        chunker = Chunker()
        legal_text = (
            "Chapter 1 General Provisions\n"
            "Section 1 Definitions and Scope\n"
            "Here are the rules of the act.\n\n"
            "Section 2 Compliance\n"
            "Organizations must comply."
        )
        chunks = chunker.chunk(legal_text, DocumentType.act_regulation, "doc-legal")
        assert len(chunks) >= 2
        assert any(c.chunk_type == ChunkType.legal_clause for c in chunks)

    def test_chunk_lesson_plan(self):
        chunker = Chunker()
        lesson_text = (
            "Lesson 1 Fractions Basics\n"
            "Learning Objective LO1: Understand parts of a whole.\n\n"
            "Lesson 2 Addition of Fractions\n"
            "Activity 1 Add like denominators."
        )
        chunks = chunker.chunk(lesson_text, DocumentType.lesson_plan, "doc-lesson")
        assert len(chunks) >= 2
        assert any(c.chunk_type == ChunkType.lesson for c in chunks)

    def test_chunk_assessment_questions(self):
        chunker = Chunker()
        assessment_text = (
            "Question 1 Calculate 5 + 7.\n(2 marks)\n\n"
            "Question 2 Solve for x where 2x = 10.\n(3 marks)"
        )
        chunks = chunker.chunk(assessment_text, DocumentType.past_paper, "doc-exam")
        assert len(chunks) >= 2
        assert any(c.chunk_type == ChunkType.assessment_question for c in chunks)

    def test_chunk_generic_paragraphs(self):
        chunker = Chunker()
        generic_text = "Paragraph one with some text.\n\nParagraph two with more details.\n\nParagraph three."
        chunks = chunker.chunk(generic_text, DocumentType.unknown, "doc-gen")
        assert len(chunks) >= 1
        assert chunks[0].chunk_type == ChunkType.paragraph


class TestETLQualityValidator:
    def test_validate_high_quality_document(self):
        validator = QualityValidator()
        doc = Document(
            document_id="d1", source_id="s1", title="Grade 4 Mathematics", description="Textbook",
            document_type=DocumentType.textbook, subject="mathematics", grade=4,
            phase="Intermediate Phase", curriculum="CAPS", country="ZA", province=None, language="en",
            publisher="Dept of Education", author="Author", publication_year=2023, version="1.0",
            license_status=LicenseStatus.creative_commons, source_url="https://example.gov.za",
            checksum="sha256checksum", file_path_raw="", file_size_bytes=50000, page_count=10,
            mime_type="text/plain", processing_status=ProcessingStatus.raw, quality_score=0.0,
            training_readiness=False, created_at="", updated_at="",
        )
        chunks = [
            DocumentChunk("c1", "d1", ChunkType.topic, 0, None, "H1", "Content 1 " * 20, 50, 1, 2, "Path1", "CAPS-01", ""),
            DocumentChunk("c2", "d1", ChunkType.topic, 1, None, "H2", "Content 2 " * 20, 50, 3, 4, "Path2", "CAPS-02", ""),
            DocumentChunk("c3", "d1", ChunkType.paragraph, 2, None, "H3", "Content 3 " * 20, 50, 5, 6, "Path3", None, ""),
            DocumentChunk("c4", "d1", ChunkType.paragraph, 3, None, "H4", "Content 4 " * 20, 50, 7, 8, "Path4", None, ""),
        ]
        from app.services.etl.etl_pipeline import ExtractionResult
        ext = ExtractionResult(
            raw_text="Long text " * 300,
            pages=[{"page_num": i} for i in range(1, 11)],
            tables=[],
            headings=["H1", "H2", "H3", "H4"],
            page_count=10,
            mime_type="text/plain",
            ocr_confidence=None,
            extraction_ok=True,
        )
        report = validator.validate(doc, chunks, ext)
        assert report.quality_score > 0.6
        assert report.status in (ProcessingStatus.validated, ProcessingStatus.needs_review)


# ─────────────────────────────────────────────
# Full Pipeline Orchestration (EduboostETL)
# ─────────────────────────────────────────────


class TestEduboostETLPipeline:
    @pytest.fixture
    def etl_instance(self, tmp_path):
        db_path = tmp_path / "test_etl.db"
        storage_dir = tmp_path / "data_storage"
        etl = EduboostETL(db_url=f"sqlite:///{db_path}", storage_root=str(storage_dir))
        etl.init_db()
        yield etl
        etl.close()

    def test_ingest_and_run_full_pipeline(self, etl_instance, tmp_path):
        sample_doc = tmp_path / "grade7_history.txt"
        sample_doc.write_text(
            "# Grade 7 Social Sciences History\n\n"
            "Published in 2021 by Education Department.\n\n"
            "## Topic 1: The Kingdom of Mali\n\n"
            "Mansa Musa travelled across North Africa to Mecca in 1324.\n"
            "The trade routes established Timbuktu as a center of learning.\n\n"
            "## Topic 2: Trans-Saharan Trade\n\n"
            "Salt, gold and manuscripts were traded across the Sahara desert.\n"
        )
        
        req = IngestRequest(
            file_path=str(sample_doc),
            source_type=SourceType.manual_upload,
            uploaded_by="curriculum_specialist",
            document_type=DocumentType.textbook,
            grade=7,
            subject="history",
            license_status=LicenseStatus.creative_commons,
        )
        
        doc = etl_instance.ingest(req)
        assert doc.document_id is not None
        assert doc.processing_status == ProcessingStatus.acquired
        
        # Test duplicate prevention
        with pytest.raises(ValueError, match="Duplicate detected"):
            etl_instance.ingest(req)

        # Run full pipeline
        quality_res = etl_instance.run_full_pipeline(doc.document_id)
        assert isinstance(quality_res, QualityCheckResult)
        assert quality_res.quality_score > 0.0

        # Approve Document
        approved_doc = etl_instance.approve_document(doc.document_id, reviewer="lead_educator", notes="Ready for training")
        assert approved_doc.processing_status == ProcessingStatus.approved
        assert approved_doc.reviewed_by == "lead_educator"

    def test_reject_document_flow(self, etl_instance, tmp_path):
        sample_bad = tmp_path / "bad_doc.txt"
        sample_bad.write_text("Short empty junk.")
        
        req = IngestRequest(
            file_path=str(sample_bad),
            document_type=DocumentType.unknown,
        )
        doc = etl_instance.ingest(req)
        etl_instance.run_full_pipeline(doc.document_id)
        
        rejected_doc = etl_instance.reject_document(doc.document_id, reviewer="lead_educator", reason="Insufficient quality")
        assert rejected_doc.processing_status == ProcessingStatus.rejected
        assert rejected_doc.rejected_reason == "Insufficient quality"

    def test_etl_queries_and_reprocess(self, etl_instance, tmp_path):
        sample = tmp_path / "query_doc.txt"
        sample.write_text("# Chapter 1\n" + "This is a detailed paragraph about science and nature.\n" * 20)
        req = IngestRequest(
            file_path=str(sample),
            document_type=DocumentType.lesson_plan,
            grade=7,
            subject="natural_sciences",
        )
        doc = etl_instance.ingest(req)
        etl_instance.run_full_pipeline(doc.document_id)

        # list_documents
        all_docs = etl_instance.list_documents()
        assert len(all_docs) >= 1
        docs_by_grade = etl_instance.list_documents(grade=7)
        assert len(docs_by_grade) >= 1
        docs_by_subject = etl_instance.list_documents(subject="natural_sciences")
        assert len(docs_by_subject) >= 1
        docs_by_type = etl_instance.list_documents(document_type="lesson_plan")
        assert len(docs_by_type) >= 1
        docs_by_status = etl_instance.list_documents(status=all_docs[0]["processing_status"])
        assert len(docs_by_status) >= 1

        # get_review_queue
        queue = etl_instance.get_review_queue()
        assert isinstance(queue, list)

        # get_content_gaps
        gaps = etl_instance.get_content_gaps()
        assert isinstance(gaps, list)

        # get_quality_report
        qr = etl_instance.get_quality_report(doc.document_id)
        assert "quality_score" in qr
        assert etl_instance.get_quality_report("nonexistent") == {}

        # get_pipeline_stats
        stats = etl_instance.get_pipeline_stats()
        assert "total" in stats
        assert stats["total"] >= 1

        # _load_ helpers missing branches
        with pytest.raises(ValueError, match="Document not found"):
            etl_instance._load_document("nonexistent-doc")
        assert etl_instance._load_extraction("nonexistent-doc") == {}
        assert etl_instance._load_normalized("nonexistent-doc") == {}

        # reprocess_document
        res = etl_instance.reprocess_document(doc.document_id)
        assert res.status is not None


class TestETLRemainingEdges:
    def test_chunker_window_text(self):
        chunker = Chunker()
        long_text = "word " * 600
        windows = chunker._split_large(long_text)
        assert len(windows) > 1

    def test_extractor_fallbacks(self, tmp_path):
        import unittest.mock as mock
        extractor = Extractor()

        # HTML fallback without BS4
        html_file = tmp_path / "page.html"
        html_file.write_text("<h1>Title</h1><p>Body text</p>")
        with mock.patch("app.services.etl.etl_pipeline.HAS_BS4", False):
            res_html = extractor._html(str(html_file))
            assert "Body text" in res_html.raw_text

        # CSV fallback without pandas
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("a,b,c\n1,2,3")
        with mock.patch("app.services.etl.etl_pipeline.HAS_PANDAS", False):
            res_csv = extractor._csv(str(csv_file))
            assert "1,2,3" in res_csv.raw_text

        # XLSX fallback without pandas
        xlsx_file = tmp_path / "sheet.xlsx"
        xlsx_file.write_text("fake xlsx")
        with mock.patch("app.services.etl.etl_pipeline.HAS_PANDAS", False):
            res_xlsx = extractor._xlsx(str(xlsx_file))
            assert "install pandas" in res_xlsx.raw_text

    def test_extractor_pdf_and_docx_mock(self, tmp_path):
        from unittest.mock import MagicMock, patch
        extractor = Extractor()

        # Mock fitz PDF
        fake_pdf = tmp_path / "test.pdf"
        fake_pdf.write_bytes(b"%PDF-1.4...")
        mock_page = MagicMock()
        mock_page.get_text.side_effect = lambda mode: "Sample PDF Page Text" if mode == "text" else {
            "blocks": [{"type": 0, "lines": [{"spans": [{"text": "PDF Heading", "size": 16}]}]}]
        }
        mock_doc = [mock_page]
        mock_fitz = MagicMock()
        mock_fitz.open.return_value = MagicMock(__enter__=lambda s: mock_doc, __exit__=lambda *a: None)
        with patch.dict("sys.modules", {"fitz": mock_fitz}), \
             patch("app.services.etl.etl_pipeline.fitz", mock_fitz, create=True), \
             patch("app.services.etl.etl_pipeline.HAS_PYMUPDF", True):
            res_pdf = extractor._pdf(str(fake_pdf))
            assert "Sample PDF Page Text" in res_pdf.raw_text
            assert "PDF Heading" in res_pdf.headings

        # Mock docx
        fake_docx = tmp_path / "test.docx"
        fake_docx.write_bytes(b"PK...")
        mock_para = MagicMock(text="Docx Heading", style=MagicMock(name="Heading 1"))
        mock_para.style.name.startswith.return_value = True
        mock_tbl = MagicMock()
        mock_tbl.rows = [
            MagicMock(cells=[MagicMock(text="h1"), MagicMock(text="h2")]),
            MagicMock(cells=[MagicMock(text="r1"), MagicMock(text="r2")]),
        ]
        mock_docx_doc = MagicMock(paragraphs=[mock_para], tables=[mock_tbl])
        mock_docx = MagicMock()
        mock_docx.Document.return_value = mock_docx_doc
        with patch.dict("sys.modules", {"docx": mock_docx}), \
             patch("app.services.etl.etl_pipeline.python_docx", mock_docx, create=True), \
             patch("app.services.etl.etl_pipeline.HAS_DOCX", True):
            res_docx = extractor._docx(str(fake_docx))
            assert "Docx Heading" in res_docx.raw_text
            assert len(res_docx.tables) == 1

    def test_create_etl_pipeline_factory(self, tmp_path):
        from app.services.etl.factory import create_etl_pipeline
        pipe1 = create_etl_pipeline(db_url=f"sqlite:///{tmp_path}/f_v1.db", storage_root=str(tmp_path), version="v1")
        pipe2 = create_etl_pipeline(db_url=f"sqlite:///{tmp_path}/f_v2.db", storage_root=str(tmp_path), version="v2")
        pipe3 = create_etl_pipeline(db_url=f"sqlite:///{tmp_path}/f_v3.db", storage_root=str(tmp_path), version="v3")
        assert pipe1 is not None and pipe2 is not None and pipe3 is not None




