import pytest
from unittest.mock import MagicMock

from app.services.etl.etl_pipeline import (
    Normalizer,
    Chunker,
    DocumentType,
    Document,
)


def test_normalizer_cleaning_and_metadata():
    norm = Normalizer()
    raw = "  Hello   world  \n\n\n  Page 1 of 10  \n\nGrade 5 mathematics lesson.  "
    res = norm.normalize(raw, DocumentType.lesson_plan)

    assert "Hello world" in res["normalized_text"]
    assert "Page 1 of 10" not in res["normalized_text"]
    assert res["language"] == "en"

    doc = MagicMock(spec=Document)
    doc.grade = None
    doc.subject = None
    doc.publication_year = None
    doc.title = ""

    updates = norm.infer_metadata(res["normalized_text"], doc)
    assert updates.get("grade") == 5
    assert updates.get("phase") == "Intermediate Phase"
    assert updates.get("subject") == "mathematics"


def test_chunker_generic():
    chunker = Chunker()
    text = "Paragraph 1 content here.\n\nParagraph 2 content here."
    chunks = chunker.chunk(text, DocumentType.textbook, "doc-123")

    assert len(chunks) > 0
    assert chunks[0].document_id == "doc-123"
    assert chunks[0].token_count > 0
