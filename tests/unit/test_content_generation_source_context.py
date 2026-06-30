from __future__ import annotations

from types import SimpleNamespace

from app.services.content_generation.source_context import ContentGenerationSourceContextService


def _source(**kwargs):
    data = {
        "source_document_id": "doc-1",
        "source_chunk_id": "chunk-1",
        "source_title": "Topic",
        "citation_text": "Grounded text",
        "caps_ref": "4.M.1.1",
        "license_status": "government_open",
        "source_quality_score": 0.9,
        "source_hash": "hash-1",
        "curriculum_mapping_id": "map-1",
        "source_metadata": {"document_status": "approved", "chunk_text": "Grounded text"},
    }
    data.update(kwargs)
    return SimpleNamespace(**data)


def test_source_context_accepts_approved_open_high_quality_chunk() -> None:
    result = ContentGenerationSourceContextService().validate_source_rows([_source()], caps_ref="4.M.1.1")

    assert result.passed is True
    assert result.chunks[0].source_chunk_id == "chunk-1"


def test_source_context_blocks_missing_etl_source_context() -> None:
    result = ContentGenerationSourceContextService().validate_source_rows([], caps_ref="4.M.1.1")

    assert result.passed is False
    assert any("No approved/indexed/training_ready" in error for error in result.errors)


def test_source_context_blocks_rejected_license_and_low_quality() -> None:
    result = ContentGenerationSourceContextService().validate_source_rows([
        _source(license_status="restricted", source_quality_score=0.1),
    ], caps_ref="4.M.1.1")

    assert result.passed is False
    assert result.errors
