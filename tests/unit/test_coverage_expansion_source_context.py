"""
Unit tests for app.services.content_generation.source_context:
  - SourceContextResult dataclass
  - ContentGenerationSourceContextService (validate_source_rows)
  - source_rows_for_chunks helper
"""
from __future__ import annotations

from types import SimpleNamespace

from app.services.content_generation.prompt_payloads import SourceContextChunk
from app.services.content_generation.source_context import (
    ContentGenerationSourceContextService,
    SourceContextResult,
    source_rows_for_chunks,
)


class TestSourceContextResult:
    def test_init_and_properties(self):
        res = SourceContextResult(passed=True, errors=[], chunks=[])
        assert res.passed is True
        assert res.errors == []
        assert res.chunks == []


class TestValidateSourceRows:
    def setup_method(self):
        self.svc = ContentGenerationSourceContextService(min_quality_score=0.5)

    def _make_source(self, **overrides):
        defaults = {
            "source_document_id": "doc-01",
            "source_chunk_id": "chunk-01",
            "source_title": "CAPS Mathematics Grade 4",
            "citation_text": "Sample text content",
            "license_status": "government_open",
            "source_metadata": {
                "document_status": "approved",
                "chunk_text": "Detailed math explanation",
            },
            "source_quality_score": 0.8,
            "source_hash": "hash-123",
            "curriculum_mapping_id": "map-456",
        }
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def test_valid_source_passes(self):
        source = self._make_source()
        res = self.svc.validate_source_rows([source], caps_ref="4.MATH.1.1")
        assert res.passed is True
        assert len(res.chunks) == 1
        assert res.chunks[0].source_document_id == "doc-01"

    def test_empty_sources_fails(self):
        res = self.svc.validate_source_rows([], caps_ref="4.MATH.1.1")
        assert res.passed is False
        assert any("No approved" in e for e in res.errors)

    def test_unapproved_status_fails(self):
        source = self._make_source(
            source_metadata={"document_status": "pending"}
        )
        res = self.svc.validate_source_rows([source], caps_ref="4.MATH.1.1")
        assert res.passed is False

    def test_incompatible_license_fails(self):
        source = self._make_source(license_status="proprietary")
        res = self.svc.validate_source_rows([source], caps_ref="4.MATH.1.1")
        assert res.passed is False

    def test_low_quality_fails(self):
        source = self._make_source(source_quality_score=0.2)
        res = self.svc.validate_source_rows([source], caps_ref="4.MATH.1.1")
        assert res.passed is False

    def test_missing_chunk_id_fails(self):
        source = self._make_source(source_chunk_id=None)
        res = self.svc.validate_source_rows([source], caps_ref="4.MATH.1.1")
        assert res.passed is False


class TestSourceRowsForChunks:
    def test_transforms_chunks_to_dicts(self):
        chunk = SourceContextChunk(
            source_document_id="doc-1",
            source_chunk_id="chunk-1",
            text="Fractions intro",
            source_title="Math Textbook",
            source_hash="sha256-abc",
            curriculum_mapping_id="map-1",
            source_quality_score=0.9,
            license_status="government_open",
            document_status="approved",
        )
        rows = source_rows_for_chunks(
            [chunk],
            caps_ref="4.MATH.1.1",
            grade=4,
            subject_code="MATH",
            language="en",
        )
        assert len(rows) == 1
        row = rows[0]
        assert row["source_document_id"] == "doc-1"
        assert row["source_chunk_id"] == "chunk-1"
        assert row["grade"] == 4
        assert row["subject_code"] == "MATH"
        assert row["language"] == "en"
        assert row["caps_ref"] == "4.MATH.1.1"
