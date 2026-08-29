import uuid
import pytest
from unittest.mock import MagicMock

from app.models.content_factory import ContentGenerationArtifact, ContentArtifactSource
from app.services.curriculum_expansion import (
    record_sha256,
    dataset_sha256,
    forbidden_training_paths,
    obvious_pii_findings,
    validate_language_content,
    build_training_record,
    artifact_eligibility_reasons,
)


def test_hash_helpers():
    r1 = {"a": 1, "b": "text"}
    r2 = {"b": "text", "a": 1}
    # Deterministic regardless of dict key order
    assert record_sha256(r1) == record_sha256(r2)

    h1 = record_sha256(r1)
    h2 = record_sha256({"c": 3})
    ds_hash = dataset_sha256([h1, h2])
    assert len(ds_hash) == 64


def test_forbidden_training_paths():
    data = {
        "title": "Grade 4 Addition",
        "nested": {
            "learner_id": "123",
            "ok_field": "val",
        },
        "items": [{"email": "test@eduboost.co.za"}],
    }
    findings = forbidden_training_paths(data)
    assert len(findings) == 2
    assert "$.nested.learner_id" in findings
    assert "$.items[0].email" in findings


def test_obvious_pii_findings():
    data_with_pii = {
        "text": "Contact parent at 0821234567 or parent@example.com with ID 9001015009087"
    }
    findings = obvious_pii_findings(data_with_pii)
    assert len(findings) >= 2


def test_validate_language_content():
    content = {"title": "LOREM IPSUM lesson content"}
    findings = validate_language_content(content, "en")
    assert "placeholder_text" in findings

    findings_lang = validate_language_content({"title": "Valid"}, "invalid_lang")
    assert "unsupported_language" in findings_lang


def test_build_training_record():
    artifact = MagicMock(spec=ContentGenerationArtifact)
    artifact.artifact_id = uuid.uuid4()
    artifact.artifact_hash = "art-hash-123"
    artifact.version_number = 2
    artifact.scope_id = "scope-1"
    artifact.caps_ref = "4.M.1.1"
    artifact.grade = 4
    artifact.subject_code = "MATHS"
    artifact.language = "en"
    artifact.content_layer = "lesson_content"
    artifact.source_snapshot_hash = "src-hash"
    artifact.quality_score = 0.92
    artifact.caps_alignment_score = 0.95
    artifact.artifact_json = {"title": "Fractions"}

    record = build_training_record(artifact)
    assert record["schema_version"] == "phase7-training-record-v1"
    assert record["artifact_version"] == 2
    assert record["quality_score"] == 0.92
