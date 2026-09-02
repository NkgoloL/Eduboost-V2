import json
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from app.services.etl.etl_pipeline import (
    EduboostETL,
    Document,
    DocumentChunk,
    ExtractionResult,
    Extractor,
    Chunker,
    QualityValidator,
    ProcessingStatus,
    SourceType,
    DocumentType,
    LicenseStatus,
    IngestRequest,
    _now,
    _uid,
)



@pytest.fixture
def etl_instance(tmp_path):
    db_path = tmp_path / "test_etl.db"
    storage_path = tmp_path / "data"
    etl = EduboostETL(db_url=f"sqlite:///{db_path}", storage_root=str(storage_path))
    etl.init_db()
    yield etl
    etl.close()


def test_document_extractor_all_formats(tmp_path):
    extractor = Extractor()

    # 1. Plain text and Markdown

    txt_file = tmp_path / "sample.txt"
    txt_file.write_text("Introduction\n\nSome body text.")
    res_txt = extractor.extract(str(txt_file))
    assert res_txt.extraction_ok
    assert res_txt.mime_type == "text/plain"

    md_file = tmp_path / "sample.md"
    md_file.write_text("# Heading 1\nContent under heading.")
    res_md = extractor.extract(str(md_file))
    assert res_md.extraction_ok
    assert res_md.mime_type == "text/markdown"

    # 2. HTML extraction with and without BS4
    html_file = tmp_path / "sample.html"
    html_file.write_text("<html><body><h1>Title</h1><p>Paragraph text</p></body></html>")
    
    # With BS4
    res_html = extractor._html(str(html_file))
    assert res_html.extraction_ok
    assert "Title" in res_html.raw_text or "Paragraph text" in res_html.raw_text

    # Without BS4
    with patch("app.services.etl.etl_pipeline.HAS_BS4", False):
        res_html_no_bs4 = extractor._html(str(html_file))
        assert res_html_no_bs4.extraction_ok
        assert "Paragraph text" in res_html_no_bs4.raw_text

    # 3. CSV extraction with and without pandas
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text("col1,col2\nval1,val2\n")

    res_csv = extractor._csv(str(csv_file))
    assert res_csv.extraction_ok

    with patch("app.services.etl.etl_pipeline.HAS_PANDAS", False):
        res_csv_no_pd = extractor._csv(str(csv_file))
        assert res_csv_no_pd.extraction_ok
        assert "col1,col2" in res_csv_no_pd.raw_text

    # 4. XLSX extraction with and without pandas
    xlsx_file = tmp_path / "sample.xlsx"
    xlsx_file.write_text("dummy xlsx")

    with patch("app.services.etl.etl_pipeline.HAS_PANDAS", False):
        res_xlsx_no_pd = extractor._xlsx(str(xlsx_file))
        assert res_xlsx_no_pd.extraction_ok
        assert "install pandas+openpyxl" in res_xlsx_no_pd.raw_text

    # Mock pandas read_excel
    with patch("app.services.etl.etl_pipeline.HAS_PANDAS", True), \
         patch("pandas.read_excel") as mock_read_excel:
        mock_df = MagicMock()
        mock_df.to_string.return_value = "col1 col2\nval1 val2"
        mock_df.columns = ["col1", "col2"]
        mock_df.values.tolist.return_value = [["val1", "val2"]]
        mock_read_excel.return_value = mock_df

        res_xlsx = extractor._xlsx(str(xlsx_file))
        assert res_xlsx.extraction_ok
        assert "col1 col2" in res_xlsx.raw_text

    # 5. DOCX extraction with and without python_docx
    docx_file = tmp_path / "sample.docx"
    docx_file.write_text("dummy docx")

    with patch("app.services.etl.etl_pipeline.HAS_DOCX", False):
        res_docx_no_docx = extractor._docx(str(docx_file))
        assert res_docx_no_docx.extraction_ok

    # Mock python_docx
    mock_doc = MagicMock()
    para1 = MagicMock(text="Heading 1", style=MagicMock(name="Heading 1"))
    para2 = MagicMock(text="Body paragraph", style=MagicMock(name="Normal"))
    mock_doc.paragraphs = [para1, para2]
    
    mock_tbl = MagicMock()
    cell1 = MagicMock(text="H1")
    cell2 = MagicMock(text="H2")
    row1 = MagicMock(cells=[cell1, cell2])
    cell3 = MagicMock(text="D1")
    cell4 = MagicMock(text="D2")
    row2 = MagicMock(cells=[cell3, cell4])
    mock_tbl.rows = [row1, row2]
    mock_doc.tables = [mock_tbl]

    import app.services.etl.etl_pipeline as etl_mod
    with patch.object(etl_mod, "HAS_DOCX", True), \
         patch.object(etl_mod, "python_docx", MagicMock(Document=MagicMock(return_value=mock_doc)), create=True):
        res_docx = extractor._docx(str(docx_file))
        assert res_docx.extraction_ok
        assert "Heading 1" in res_docx.raw_text
        assert len(res_docx.tables) == 1

    # 6. PDF extraction with and without PyMuPDF (fitz)
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_text("dummy pdf")

    with patch("app.services.etl.etl_pipeline.HAS_PYMUPDF", False):
        res_pdf_no_fitz = extractor._pdf(str(pdf_file))
        assert res_pdf_no_fitz.extraction_ok

    mock_fitz_doc = MagicMock()
    mock_fitz_doc.__len__.return_value = 1
    mock_page = MagicMock()
    mock_page.get_text.side_effect = lambda mode: (
        "Sample PDF text on page 1" if mode == "text" else {
            "blocks": [
                {
                    "type": 0,
                    "lines": [
                        {
                            "spans": [{"text": "Major Section Heading", "size": 16}]
                        }
                    ]
                }
            ]
        }
    )
    mock_fitz_doc.__iter__.return_value = [mock_page]
    mock_fitz_doc.__enter__.return_value = [mock_page]


    with patch.object(etl_mod, "HAS_PYMUPDF", True), \
         patch.object(etl_mod, "fitz", MagicMock(open=MagicMock(return_value=mock_fitz_doc)), create=True):
        res_pdf = extractor._pdf(str(pdf_file))
        assert res_pdf.extraction_ok
        assert "Sample PDF text" in res_pdf.raw_text
        assert "Major Section Heading" in res_pdf.headings


def test_chunker_split_large():
    chunker = Chunker()
    large_text = "word " * 1000
    parts = chunker._split_large(large_text)
    assert len(parts) > 1

    short_text = "short text"
    short_parts = chunker._split_large(short_text)
    assert len(short_parts) == 1


def test_etl_queries_and_reprocess(etl_instance, tmp_path):
    sample_file = tmp_path / "lesson.md"
    sample_file.write_text(
        "# Grade 4 Maths Lesson\n\n"
        "## Fractions\n\n"
        "Fractions represent equal parts of a whole.\n\n"
        "### Example\n\n"
        "Half of an apple is 1/2."
    )

    req = IngestRequest(
        file_path=str(sample_file),
        source_type=SourceType.manual_upload,
        uploaded_by="editor_1",
        document_type=DocumentType.lesson_plan,
        grade=4,
        subject="mathematics",
        license_status=LicenseStatus.government_open,
        title="Grade 4 Fractions",
    )
    doc = etl_instance.ingest(req)
    result = etl_instance.run_full_pipeline(doc.document_id)
    assert result.status is not None

    # 1. list_documents with all filters
    docs_all = etl_instance.list_documents()
    assert len(docs_all) >= 1

    fresh_doc = etl_instance._load_document(doc.document_id)
    docs_filtered = etl_instance.list_documents(
        status=fresh_doc.processing_status,
        grade=4,
        subject="mathematics",
        document_type=DocumentType.lesson_plan.value,
        limit=10,
    )
    assert len(docs_filtered) >= 1
    assert docs_filtered[0]["document_id"] == doc.document_id


    # 2. get_pipeline_stats
    stats = etl_instance.get_pipeline_stats()
    assert stats["total"] >= 1
    assert "pending_reviews" in stats

    # 3. get_content_gaps
    gaps = etl_instance.get_content_gaps()
    assert isinstance(gaps, list)
    assert len(gaps) >= 1

    # 4. get_quality_report
    qr = etl_instance.get_quality_report(doc.document_id)
    assert qr != {}
    assert "issues" in qr

    qr_empty = etl_instance.get_quality_report("non_existent_doc_id")
    assert qr_empty == {}

    # 5. get_review_queue and review task creation
    etl_instance._create_review_task(doc.document_id, "Needs human validation")
    queue = etl_instance.get_review_queue()
    assert len(queue) >= 1
    assert queue[0]["document_id"] == doc.document_id

    # 6. reprocess_document
    reprocessed_result = etl_instance.reprocess_document(doc.document_id)
    assert reprocessed_result.status is not None

    # 7. _load_extraction and _load_normalized file existence checks
    ext_data = etl_instance._load_extraction(doc.document_id)
    assert ext_data != {}
    missing_ext = etl_instance._load_extraction("missing_id")
    assert missing_ext == {}

    norm_data = etl_instance._load_normalized(doc.document_id)
    assert norm_data != {}
    missing_norm = etl_instance._load_normalized("missing_id")
    assert missing_norm == {}
