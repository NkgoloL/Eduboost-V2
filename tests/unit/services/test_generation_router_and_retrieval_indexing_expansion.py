"""Comprehensive unit tests for generation schemas and semantic retrieval indexing."""
from __future__ import annotations

from datetime import UTC, datetime
import pytest

from app.api_v2_routers.generation import (
    TaskSpecRequest,
    StartRunRequest,
    RunResponse,
    TaskResponse,
)
from app.services.semantic_retrieval.indexing import (
    SourceDocumentInput,
    SourceChunkInput,
)


class TestGenerationSchemas:
    def test_task_spec_request_validation_valid(self):
        spec = TaskSpecRequest(
            caps_ref="4.M.1.1",
            content_type="diagnostic_item",
            count=5,
            language="en",
            grade=4,
            subject="Mathematics",
            subject_code="MATHS",
        )
        assert spec.caps_ref == "4.M.1.1"
        assert spec.count == 5

    def test_task_spec_request_invalid_caps_ref(self):
        with pytest.raises(Exception):
            TaskSpecRequest(
                caps_ref="invalid_ref_format",
                content_type="diagnostic_item",
            )

    def test_start_run_request(self):
        spec = TaskSpecRequest(
            caps_ref="4.M.1.1",
            content_type="diagnostic_item",
        )
        req = StartRunRequest(
            scope_id="grade4_maths",
            task_specs=[spec],
        )
        assert req.scope_id == "grade4_maths"
        assert len(req.task_specs) == 1

    def test_run_response_model(self):
        now = datetime.now(UTC)
        res = RunResponse(
            run_id="run_123",
            scope_id="grade4_maths",
            status="completed",
            requested_by="admin_user",
            provider="groq",
            run_metadata={"tasks": 5},
            created_at=now,
            updated_at=now,
        )
        assert res.run_id == "run_123"
        assert res.status == "completed"

    def test_task_response_model(self):
        now = datetime.now(UTC)
        res = TaskResponse(
            task_id="task_456",
            caps_ref="4.M.1.1",
            content_layer="diagnostic_items",
            status="succeeded",
            attempt_number=1,
            provider="groq",
            model="llama-3.3-70b-versatile",
            prompt_version="cf-gen-v1",
            token_usage={"total_tokens": 150},
            cost_metadata={"usd": 0.001},
            validation_failures=[],
            output_artifact_ids=["art_1"],
            started_at=now,
            finished_at=now,
            created_at=now,
        )
        assert res.task_id == "task_456"
        assert res.status == "succeeded"


class TestSemanticRetrievalInputs:
    def test_source_document_input_dataclass(self):
        doc = SourceDocumentInput(
            document_id="doc_1",
            document_version_id="ver_1",
            title="Whole Numbers Guide",
            scope_id="grade4_maths",
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="MATHS",
            language="en",
            status="approved",
            permission_scope="internal",
            license_status="cc_by",
            quality_score=0.95,
        )
        assert doc.document_id == "doc_1"
        assert doc.quality_score == 0.95

    def test_source_chunk_input_dataclass(self):
        chunk = SourceChunkInput(
            chunk_id="chunk_1",
            chunk_index=0,
            content="Ordering and comparing whole numbers up to 4 digits.",
            heading="Whole Numbers",
            scope_id="grade4_maths",
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="MATHS",
            language="en",
            quality_score=0.90,
            status="approved",
        )
        assert chunk.chunk_id == "chunk_1"
        assert chunk.chunk_index == 0
        assert "Ordering and comparing" in chunk.content
