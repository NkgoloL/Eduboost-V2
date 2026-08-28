"""Comprehensive unit tests for Content Factory domain schemas and citations."""
from __future__ import annotations

import pytest

from app.models.content_factory import ContentLayer, ContentArtifactType
from app.domain.content_factory_schemas import (
    ETLSourceCitation,
    SourceBundleValidationRequest,
    SourceBundleValidationResponse,
    ContentFactoryHealthResponse,
    ContentArtifactCreate,
)


class TestContentFactoryDomainSchemas:
    def test_etl_source_citation(self):
        citation = ETLSourceCitation(
            source_document_id="doc_123",
            source_chunk_id="chunk_456",
            source_role="primary_context",
            caps_ref="4.M.1.1",
            chunk_quality_score=0.98,
        )
        assert citation.source_document_id == "doc_123"
        assert citation.source_chunk_id == "chunk_456"
        assert citation.chunk_quality_score == 0.98

    def test_source_bundle_validation_request_and_response(self):
        req = SourceBundleValidationRequest(
            caps_ref="4.M.1.1",
            min_sources=1,
            require_approved_documents=True,
            sources=[
                ETLSourceCitation(
                    source_document_id="doc_123",
                    caps_ref="4.M.1.1",
                )
            ],
        )
        assert req.min_sources == 1
        assert len(req.sources) == 1

        resp = SourceBundleValidationResponse(
            passed=True,
            errors=[],
            source_snapshot_hash="hash-abc-123",
        )
        assert resp.passed is True
        assert resp.source_snapshot_hash == "hash-abc-123"

    def test_content_factory_health_response(self):
        health = ContentFactoryHealthResponse(
            status="healthy",
            route_scope="admin",
            generation_enabled=True,
        )
        assert health.status == "healthy"
        assert health.generation_enabled is True

    def test_content_artifact_create(self):
        art = ContentArtifactCreate(
            scope_id="grade4_maths",
            content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
            artifact_type=ContentArtifactType.DIAGNOSTIC_ITEM,
            artifact_json={"question": "5+5", "answer": "10"},
            grade=4,
            caps_ref="4.M.1.1",
        )
        assert art.scope_id == "grade4_maths"
        assert art.grade == 4
        assert art.artifact_json["answer"] == "10"
