import pytest
from app.services.etl.etl_pipeline import Extractor, ExtractionResult


def test_txt_and_md_extraction(tmp_path):
    extractor = Extractor()

    txt_file = tmp_path / "sample.txt"
    txt_file.write_text("This is plain text content.")
    res_txt = extractor.extract(str(txt_file))
    assert res_txt.extraction_ok is True
    assert res_txt.mime_type == "text/plain"
    assert "plain text" in res_txt.raw_text

    md_file = tmp_path / "sample.md"
    md_file.write_text("# Chapter 1\n\nIntroductory content.")
    res_md = extractor.extract(str(md_file))
    assert res_md.extraction_ok is True
    assert res_md.mime_type == "text/markdown"
    assert "Chapter 1" in res_md.headings


def test_html_and_csv_extraction(tmp_path):
    extractor = Extractor()

    html_file = tmp_path / "page.html"
    html_file.write_text("<html><h1>Title</h1><p>Paragraph</p></html>")
    res_html = extractor.extract(str(html_file))
    assert res_html.extraction_ok is True
    assert res_html.mime_type == "text/html"

    csv_file = tmp_path / "data.csv"
    csv_file.write_text("col1,col2\nval1,val2\n")
    res_csv = extractor.extract(str(csv_file))
    assert res_csv.extraction_ok is True
    assert res_csv.mime_type == "text/csv"
