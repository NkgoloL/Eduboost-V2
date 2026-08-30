import uuid
import pytest

from app.services.content_factory import (
    APPROVED_SOURCE_STATUSES,
    ACCEPTABLE_LICENSE_STATUSES,
    SourceGateResult,
    ArtifactProvenanceReport,
    stable_json_hash,
    ETLProvenanceService,
)


def test_constants_and_dataclasses():
    assert "approved" in APPROVED_SOURCE_STATUSES
    assert "government_open" in ACCEPTABLE_LICENSE_STATUSES

    res = SourceGateResult(passed=True, errors=[], source_snapshot_hash="sha256:abc")
    assert res.passed is True

    rep = ArtifactProvenanceReport(
        artifact_id=uuid.uuid4(),
        passed=True,
        errors=[],
        source_snapshot_hash="sha256:abc",
        sources=[],
    )
    assert rep.passed is True


def test_stable_json_hash():
    h1 = stable_json_hash({"b": 2, "a": 1})
    h2 = stable_json_hash({"a": 1, "b": 2})
    assert h1 == h2
    assert h1.startswith("sha256:")


def test_validate_source_bundle_empty():
    service = ETLProvenanceService()
    res = service.validate_source_bundle(caps_ref="4.M.1.1", sources=[])
    assert res.passed is False
    assert len(res.errors) > 0

    res_synthetic = service.validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[],
        allow_synthetic_without_source=True,
    )
    assert res_synthetic.passed is True
    assert res_synthetic.errors == []


def test_validate_source_bundle_valid():
    service = ETLProvenanceService()
    sources = [
        {
            "source_document_id": "doc-1",
            "source_chunk_id": "chunk-1",
            "document_status": "approved",
            "license_status": "government_open",
            "caps_ref": "4.M.1.1",
            "chunk_quality_score": 0.85,
        }
    ]
    res = service.validate_source_bundle(caps_ref="4.M.1.1", sources=sources)
    assert res.passed is True
    assert res.errors == []
    assert res.source_snapshot_hash is not None
