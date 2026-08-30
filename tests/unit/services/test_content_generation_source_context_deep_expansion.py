"""Comprehensive unit tests for ContentGenerationSourceContextService validation and results."""
from __future__ import annotations

from types import SimpleNamespace
import pytest

from app.services.content_generation.source_context import (
    SourceContextResult,
    ContentGenerationSourceContextService,
)


class TestSourceContextModels:
    def test_source_context_result_dataclass(self):
        res = SourceContextResult(
            passed=True,
            errors=[],
            chunks=[],
        )
        assert res.passed is True
        assert len(res.errors) == 0
        assert len(res.chunks) == 0

    def test_source_context_service_init(self):
        service = ContentGenerationSourceContextService(min_quality_score=0.75)
        assert service.min_quality_score == 0.75

    def test_validate_source_rows_ineligible_document_status(self):
        service = ContentGenerationSourceContextService()
        bad_source = SimpleNamespace(
            source_document_id="doc_rejected",
            source_metadata={"document_status": "rejected", "license_status": "cc-by"},
            source_quality_score=0.9,
        )
        res = service.validate_source_rows([bad_source], caps_ref="4.M.1.1")
        assert res.passed is False
        assert any("has status rejected" in err for err in res.errors)

    def test_validate_source_rows_incompatible_license(self):
        service = ContentGenerationSourceContextService()
        bad_license_source = SimpleNamespace(
            source_document_id="doc_copyrighted",
            source_metadata={"document_status": "approved", "license_status": "proprietary_all_rights_reserved"},
            source_quality_score=0.9,
        )
        res = service.validate_source_rows([bad_license_source], caps_ref="4.M.1.1")
        assert res.passed is False
        assert any("incompatible license" in err for err in res.errors)
