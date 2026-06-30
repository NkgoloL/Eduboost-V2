from app.services.content_factory import ETLProvenanceService


def test_artifact_without_sources_fails_provenance() -> None:
    result = ETLProvenanceService().validate_source_bundle(caps_ref="4.M.1.1", sources=[])
    assert result.passed is False
    assert "At least one ETL source citation is required." in result.errors


def test_rejected_source_fails_provenance() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[{"source_document_id": "doc", "source_chunk_id": "chunk", "document_status": "rejected", "license_status": "government_open", "caps_ref": "4.M.1.1"}],
    )
    assert result.passed is False
    assert any("approved, indexed, or training_ready" in error for error in result.errors)


def test_caps_ref_mismatch_fails_provenance() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[{"source_document_id": "doc", "source_chunk_id": "chunk", "document_status": "approved", "license_status": "government_open", "caps_ref": "4.M.9.9"}],
    )
    assert result.passed is False
    assert any("does not match" in error for error in result.errors)
