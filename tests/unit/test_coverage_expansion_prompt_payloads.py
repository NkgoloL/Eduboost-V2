"""
Unit tests for app.services.content_generation.prompt_payloads:
  - SourceContextChunk
  - GenerationRequestBase & subclasses
  - GeneratedDiagnosticItem & to_artifact_json
  - GeneratedLesson
"""
from __future__ import annotations


from app.services.content_generation.prompt_payloads import (
    DiagnosticGenerationRequest,
    GeneratedDiagnosticItem,
    GenerationRequestBase,
    LessonGenerationRequest,
    SourceContextChunk,
)


class TestSourceContextChunk:
    def test_instantiation_defaults(self):
        chunk = SourceContextChunk(
            source_document_id="doc-1",
            source_chunk_id="chunk-1",
            text="Some content text",
        )
        assert chunk.source_document_id == "doc-1"
        assert chunk.document_status == "approved"
        assert chunk.source_title is None

    def test_full_instantiation(self):
        chunk = SourceContextChunk(
            source_document_id="doc-1",
            source_chunk_id="chunk-1",
            text="Text",
            source_title="Title",
            source_hash="hash",
            curriculum_mapping_id="map-1",
            source_quality_score=0.9,
            license_status="open",
            document_status="training_ready",
        )
        assert chunk.source_title == "Title"
        assert chunk.source_quality_score == 0.9


class TestGenerationRequest:
    def test_base_request(self):
        req = GenerationRequestBase(
            scope_id="math_g4",
            caps_ref="4.MATH.1",
            grade=4,
            subject_code="MATH",
            language="en",
            topic_title="Fractions",
            required_count=5,
            approved_count=0,
            missing_count=5,
            source_chunks=[],
        )
        assert req.prompt_version == "cf-gen-v1"
        assert req.missing_count == 5

    def test_diagnostic_request_subclass(self):
        req = DiagnosticGenerationRequest(
            scope_id="math_g4",
            caps_ref="4.MATH.1",
            grade=4,
            subject_code="MATH",
            language="en",
            topic_title="Fractions",
            required_count=5,
            approved_count=2,
            missing_count=3,
            source_chunks=[],
        )
        assert isinstance(req, GenerationRequestBase)

    def test_lesson_request_subclass(self):
        req = LessonGenerationRequest(
            scope_id="math_g4",
            caps_ref="4.MATH.1",
            grade=4,
            subject_code="MATH",
            language="en",
            topic_title="Fractions",
            required_count=1,
            approved_count=0,
            missing_count=1,
            source_chunks=[],
        )
        assert isinstance(req, GenerationRequestBase)


class TestGeneratedDiagnosticItem:
    def test_to_artifact_json(self):
        item = GeneratedDiagnosticItem(
            question_text="What is 1/2 of 10?",
            options=["5", "2", "10", "1"],
            correct_answer="5",
            explanation="10 divided by 2 is 5.",
            caps_ref="4.MATH.1",
            grade=4,
            subject_code="MATH",
            language="en",
            source_chunk_ids=["chunk-1"],
        )
        data = item.to_artifact_json()
        assert data["question_text"] == "What is 1/2 of 10?"
        assert data["answer_key"] == {"correct_answer": "5"}
        assert data["safety_status"] == "passed"
