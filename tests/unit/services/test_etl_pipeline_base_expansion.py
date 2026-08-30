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
    _now,
    _uid,
    _sha256,
    _token_count,
)


def test_enums_and_constants():
    assert DocumentType.textbook == "textbook"
    assert SourceType.manual_upload == "manual_upload"
    assert ProcessingStatus.approved == "approved"
    assert LicenseStatus.open_license == "open_license"
    assert ChunkType.section == "section"


def test_composite_quality_score():
    score = QualityCheckResult.compute_composite(
        meta=1.0,
        extract=1.0,
        struct=1.0,
        complete=1.0,
        prov=1.0,
        training=1.0,
    )
    assert score == pytest.approx(1.0, 0.01)


def test_helpers(tmp_path):
    now_str = _now()
    assert "T" in now_str
    uid_str = _uid()
    assert len(uid_str) > 0
    assert _token_count("12345678") == 2

    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"hello world")
    h = _sha256(str(test_file))
    assert len(h) == 64
