"""Comprehensive unit tests for ETL pipeline extraction, normalization, and metadata inference."""
from __future__ import annotations

from types import SimpleNamespace
from pathlib import Path
import pytest

from app.services.etl.etl_pipeline import (
    Extractor,
    Normalizer,
    DocumentType,
)


class TestETLExtractor:
    def test_extract_txt_and_markdown(self, tmp_path):
        txt_file = tmp_path / "sample.txt"
        txt_file.write_text("Hello World\nLine 2", encoding="utf-8")

        extractor = Extractor()
        res_txt = extractor.extract(str(txt_file))
        assert res_txt.extraction_ok is True
        assert "Hello World" in res_txt.raw_text
        assert res_txt.mime_type == "text/plain"

        md_file = tmp_path / "sample.md"
        md_file.write_text("# Chapter 1\n## Section 1.1\nContent", encoding="utf-8")
        res_md = extractor.extract(str(md_file))
        assert res_md.mime_type == "text/markdown"
        assert len(res_md.headings) >= 1

    def test_extract_html(self, tmp_path):
        html_file = tmp_path / "sample.html"
        html_file.write_text("<html><body><h1>Title Heading</h1><p>Paragraph text</p></body></html>", encoding="utf-8")

        extractor = Extractor()
        res_html = extractor.extract(str(html_file))
        assert res_html.extraction_ok is True
        assert "Paragraph text" in res_html.raw_text


class TestETLNormalizer:
    def test_normalize_text_and_whitespace(self):
        norm = Normalizer()
        raw = "   Paragraph 1 with   multiple    spaces.\n\n\n\nParagraph 2.  Page 1 of 10  "
        res = norm.normalize(raw, document_type=DocumentType.textbook)
        assert "Paragraph 1 with multiple spaces." in res["normalized_text"]
        assert "Paragraph 2." in res["normalized_text"]
        assert res["language"] == "en"
        assert res["word_count"] > 0

    def test_detect_afrikaans_language(self):
        norm = Normalizer()
        af_text = "die kinders is in die skool en hulle leer van die boeke met entoesiasme nie"
        lang = norm._detect_language(af_text)
        assert lang == "af"

    def test_infer_metadata_grade_and_phase(self):
        norm = Normalizer()
        mock_doc = SimpleNamespace(
            grade=None,
            subject=None,
            publication_year=None,
            title="Untitled",
        )
        text = "Curriculum and Assessment Policy Statement\nGrade 4 Mathematics Textbook\nPublished 2023"
        updates = norm.infer_metadata(text, mock_doc)

        assert updates.get("grade") == 4
        assert updates.get("phase") == "Intermediate Phase"
        assert updates.get("subject") == "mathematics"
        assert updates.get("publication_year") == 2023
        assert updates.get("title") == "Curriculum and Assessment Policy Statement"
