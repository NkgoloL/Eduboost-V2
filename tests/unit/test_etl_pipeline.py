import textwrap



from app.services.etl.etl_pipeline import (
    Extractor,
    Normalizer,
    Chunker,
    QualityValidator,
    EduboostETL,
    IngestRequest,
    ExtractionResult,
    Document,
    DocumentChunk,
    DocumentType,
    SourceType,
    LicenseStatus,
    ProcessingStatus,
    _now,
)


def make_sample_text():
    return textwrap.dedent("""
    # Grade 5 Sample Lesson

    ## Week 1: Intro

    **Learning Objective:** LO1 — Understand basic place value.

    This is an example lesson plan used by unit tests. """)


def test_extractor_txt_html_csv(tmp_path):
    ext = Extractor()

    # plain text / markdown
    txt = tmp_path / "sample.md"
    txt.write_text(make_sample_text())
    r = ext.extract(str(txt))
    assert r.extraction_ok
    assert r.page_count == 1
    assert any("Grade 5 Sample" in h for h in r.headings) or len(r.raw_text) > 0

    # html fallback (without bs4)
    html = tmp_path / "p.html"
    html.write_text("<h1>Title</h1><p>Paragraph</p>")
    r2 = ext.extract(str(html))
    assert r2.extraction_ok
    assert "Paragraph" in r2.raw_text

    # csv fallback when pandas not present
    csv = tmp_path / "t.csv"
    csv.write_text("a,b\n1,2\n3,4\n")
    r3 = ext.extract(str(csv))
    assert r3.extraction_ok
    assert r3.mime_type == "text/csv"


def test_normalizer_and_infer_metadata():
    norm = Normalizer()
    text = "Grade 5\nThis mathematics text mentions algebra and numeracy. CAPS-1.2.3"
    out = norm.normalize(text, DocumentType.lesson_plan)
    assert "normalized_text" in out
    assert out["language"] in ("en", "af")

    # create a minimal Document with missing metadata to infer
    now = _now()
    doc = Document(
        document_id="d1",
        source_id="s1",
        title="",
        description="",
        document_type=DocumentType.lesson_plan,
        subject=None,
        grade=None,
        phase=None,
        curriculum=None,
        country="ZA",
        province=None,
        language="",
        publisher=None,
        author=None,
        publication_year=None,
        version="1.0",
        license_status=LicenseStatus.unknown,
        source_url=None,
        checksum="abc",
        file_path_raw="/tmp/f",
        file_size_bytes=0,
        page_count=0,
        mime_type="text/plain",
        processing_status=ProcessingStatus.raw,
        quality_score=0.0,
        training_readiness=False,
        created_at=now,
        updated_at=now,
    )

    updates = norm.infer_metadata(out["normalized_text"], doc)
    assert "grade" in updates and updates["grade"] == 5
    assert "subject" in updates


def test_chunker_generic_and_split():
    chunker = Chunker()
    # generate long text to force splitting
    words = ["word"] * (Chunker.MAX_TOKENS * 10)
    long_text = " ".join(words)
    chunks = chunker.chunk(long_text, DocumentType.unknown, "doc-x")
    assert len(chunks) >= 1
    for c in chunks:
        assert c.chunk_id != ""
        assert c.token_count >= 1


def test_quality_validator_valid_and_failed():
    validator = QualityValidator()
    now = _now()
    # create a document with approved license and metadata
    doc = Document(
        document_id="d2",
        source_id="s2",
        title="Good Document",
        description="",
        document_type=DocumentType.textbook,
        subject="mathematics",
        grade=5,
        phase="Intermediate",
        curriculum="CAPS",
        country="ZA",
        province=None,
        language="en",
        publisher=None,
        author=None,
        publication_year=2020,
        version="1.0",
        license_status=LicenseStatus.open_license,
        source_url=None,
        checksum="c1",
        file_path_raw="/tmp/f2",
        file_size_bytes=0,
        page_count=12,
        mime_type="text/plain",
        processing_status=ProcessingStatus.extracted,
        quality_score=0.0,
        training_readiness=False,
        created_at=now,
        updated_at=now,
    )

    # sufficient extraction
    large_text = "x" * 6000
    extraction = ExtractionResult(raw_text=large_text, pages=[{"page_num":1}], tables=[], headings=["H1"], page_count=12, mime_type="text/plain", ocr_confidence=None, extraction_ok=True)

    chunks = [DocumentChunk(chunk_id="", document_id="d2", chunk_type="paragraph", chunk_index=0, parent_chunk_id=None, heading="h", content=f"para {i}", token_count=0, page_start=None, page_end=None, section_path="", curriculum_code=None, created_at="") for i in range(10)]

    res = validator.validate(doc, chunks, extraction)
    assert res.status == ProcessingStatus.validated
    assert res.quality_score > 0.7

    # extraction failed case
    bad_ext = ExtractionResult(raw_text="", pages=[], tables=[], headings=[], page_count=0, mime_type="unknown", ocr_confidence=None, extraction_ok=False, error="boom")
    res2 = validator.validate(doc, [], bad_ext)
    assert any("Extraction failed" in s for s in res2.issues)


def test_etl_end_to_end(tmp_path):
    # integration style test: ingest -> run_full_pipeline
    sample = tmp_path / "lesson.md"
    sample.write_text(make_sample_text() * 50)

    db = tmp_path / "etl.db"
    storage = tmp_path / "data"
    etl = EduboostETL(db_url=f"sqlite:///{db}", storage_root=str(storage))
    etl.init_db()

    req = IngestRequest(
        file_path=str(sample),
        source_type=SourceType.manual_upload,
        uploaded_by="tester",
        document_type=DocumentType.lesson_plan,
        grade=5,
        subject="mathematics",
        license_status=LicenseStatus.government_open,
        title="Test Lesson",
    )
    doc = etl.ingest(req)
    assert doc.document_id

    result = etl.run_full_pipeline(doc.document_id)
    assert result.quality_score >= 0.0
    chunks = etl._load_chunks(doc.document_id)
    assert len(chunks) > 0

    etl.close()
