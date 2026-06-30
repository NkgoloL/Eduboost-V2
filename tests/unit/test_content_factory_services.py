from __future__ import annotations


import pytest

from app.services.content_factory import (
    ContentFactoryService,
    ContentValidationService,
    ETLProvenanceService,
    stable_json_hash,
)


def test_source_bundle_requires_approved_etl_source() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "caps_ref": "4.M.1.1",
                "document_status": "needs_review",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert not result.passed
    assert "approved, indexed, or training_ready" in result.errors[0]


def test_source_bundle_accepts_training_ready_source_and_hashes_snapshot() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "curriculum_mapping_id": "map-1",
                "caps_ref": "4.M.1.1",
                "document_status": "training_ready",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert result.passed
    assert result.errors == []
    assert result.source_snapshot_hash.startswith("sha256:")


def test_validation_blocks_diagnostic_item_without_answer_key() -> None:
    result = ContentValidationService().validate_artifact_payload(
        artifact_json={"stem": "What is 2 + 2?", "safety_status": "passed"},
        caps_ref="4.M.1.1",
        artifact_type="diagnostic_item",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "caps_ref": "4.M.1.1",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.8,
            }
        ],
    )

    assert not result["passed"]
    assert "answer_key" in result["errors"][0]


def test_content_factory_router_is_registered() -> None:
    from app.api_v2 import ROUTER_REGISTRY

    names = {name for name, _router in ROUTER_REGISTRY}

    assert "content_factory" in names


# Additional comprehensive tests for ETLProvenanceService


def test_source_bundle_rejects_empty_sources_by_default() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[],
    )

    assert not result.passed
    assert "At least one ETL source citation is required" in result.errors[0]
    assert result.source_snapshot_hash is None


def test_source_bundle_allows_synthetic_without_source_when_flagged() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[],
        allow_synthetic_without_source=True,
    )

    assert result.passed
    assert result.errors == []
    assert result.source_snapshot_hash is None


def test_source_bundle_requires_document_id() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[
            {
                "source_chunk_id": "chunk-1",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert not result.passed
    assert "source_document_id is required" in result.errors[0]


def test_source_bundle_requires_chunk_id() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[
            {
                "source_document_id": "doc-1",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert not result.passed
    assert "source_chunk_id is required" in result.errors[0]


def test_source_bundle_rejects_incompatible_license() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "document_status": "approved",
                "license_status": "all_rights_reserved",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert not result.passed
    assert "incompatible license_status" in result.errors[0]


def test_source_bundle_rejects_caps_ref_mismatch() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "caps_ref": "5.M.2.1",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert not result.passed
    assert "does not match artifact caps_ref" in result.errors[0]


def test_source_bundle_rejects_low_quality_score() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.3,
            }
        ],
    )

    assert not result.passed
    assert "chunk_quality_score must be at least 0.5" in result.errors[0]


def test_source_bundle_enforces_min_sources() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
        min_sources=2,
    )

    assert not result.passed
    assert "requires at least 2 cited ETL source(s)" in result.errors[0]


def test_source_bundle_accepts_indexed_status() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "document_status": "indexed",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert result.passed


def test_source_bundle_accepts_various_licenses() -> None:
    for license_status in ["government_open", "open_license", "public_domain", "cc_by", "cc_by_sa"]:
        result = ETLProvenanceService().validate_source_bundle(
            caps_ref="4.M.1.1",
            sources=[
                {
                    "source_document_id": "doc-1",
                    "source_chunk_id": "chunk-1",
                    "document_status": "approved",
                    "license_status": license_status,
                    "chunk_quality_score": 0.9,
                }
            ],
        )
        assert result.passed, f"Failed for license_status: {license_status}"


def test_source_bundle_does_not_require_approved_when_flagged() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "document_status": "needs_review",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
        require_approved_documents=False,
    )

    assert result.passed


def test_source_bundle_handles_multiple_sources() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            },
            {
                "source_document_id": "doc-2",
                "source_chunk_id": "chunk-2",
                "document_status": "approved",
                "license_status": "cc_by",
                "chunk_quality_score": 0.85,
            }
        ],
    )

    assert result.passed


# Tests for stable_json_hash


def test_stable_json_hash_produces_consistent_hash() -> None:
    payload1 = {"a": 1, "b": 2, "c": 3}
    payload2 = {"c": 3, "b": 2, "a": 1}
    hash1 = stable_json_hash(payload1)
    hash2 = stable_json_hash(payload2)
    assert hash1 == hash2
    assert hash1.startswith("sha256:")


def test_stable_json_hash_handles_nested_dicts() -> None:
    payload = {"a": {"b": {"c": 1}}, "d": [1, 2, 3]}
    result = stable_json_hash(payload)
    assert result.startswith("sha256:")


def test_stable_json_hash_handles_special_characters() -> None:
    payload = {"key": "value with spaces and üñíçödé"}
    result = stable_json_hash(payload)
    assert result.startswith("sha256:")


# Tests for ContentValidationService


def test_validation_rejects_empty_artifact_json() -> None:
    result = ContentValidationService().validate_artifact_payload(
        artifact_json={},
        caps_ref="4.M.1.1",
        artifact_type="lesson",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert not result["passed"]
    assert any("artifact_json must not be empty" in error for error in result["errors"])


def test_validation_accepts_non_diagnostic_without_answer_key() -> None:
    result = ContentValidationService().validate_artifact_payload(
        artifact_json={"content": "lesson content"},
        caps_ref="4.M.1.1",
        artifact_type="lesson",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert result["passed"]


def test_validation_rejects_bad_safety_status() -> None:
    result = ContentValidationService().validate_artifact_payload(
        artifact_json={"stem": "question", "answer_key": "4", "safety_status": "failed"},
        caps_ref="4.M.1.1",
        artifact_type="diagnostic_item",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert not result["passed"]
    assert "safety_status must be passed/safe/approved" in result["errors"][0]


def test_validation_accepts_various_safety_statuses() -> None:
    for status in ["passed", "safe", "approved"]:
        result = ContentValidationService().validate_artifact_payload(
            artifact_json={"stem": "question", "answer_key": "4", "safety_status": status},
            caps_ref="4.M.1.1",
            artifact_type="diagnostic_item",
            sources=[
                {
                    "source_document_id": "doc-1",
                    "source_chunk_id": "chunk-1",
                    "document_status": "approved",
                    "license_status": "government_open",
                    "chunk_quality_score": 0.9,
                }
            ],
        )
        assert result["passed"], f"Failed for safety_status: {status}"


def test_validation_includes_source_snapshot_hash() -> None:
    result = ContentValidationService().validate_artifact_payload(
        artifact_json={"content": "lesson content"},
        caps_ref="4.M.1.1",
        artifact_type="lesson",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert result["source_snapshot_hash"] is not None
    assert result["source_snapshot_hash"].startswith("sha256:")


def test_validation_returns_check_flags() -> None:
    result = ContentValidationService().validate_artifact_payload(
        artifact_json={"stem": "question", "answer_key": "4", "safety_status": "passed"},
        caps_ref="4.M.1.1",
        artifact_type="diagnostic_item",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert "checks" in result
    assert result["checks"]["schema_present"] is True
    assert result["checks"]["answer_key_verified"] is True
    assert result["checks"]["source_traceability"] is True
    assert result["checks"]["safety_status"] == "passed"


# Tests for ContentFactoryService


@pytest.mark.unit
def test_content_factory_service_initializes_with_default_validation() -> None:
    service = ContentFactoryService()
    assert service.validation_service is not None
    assert isinstance(service.validation_service, ContentValidationService)


@pytest.mark.unit
def test_content_factory_service_accepts_custom_validation() -> None:
    custom_validation = ContentValidationService()
    service = ContentFactoryService(validation_service=custom_validation)
    assert service.validation_service is custom_validation
