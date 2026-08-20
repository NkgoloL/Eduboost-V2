"""
Unit tests for app.services.content_factory pure service logic:
  - stable_json_hash
  - SourceGateResult / ArtifactProvenanceReport dataclasses
  - ETLProvenanceService.validate_source_bundle
  - ContentValidationService.validate_artifact_payload
  - _enum_value helper
"""
from __future__ import annotations



from app.services.content_factory import (
    ContentValidationService,
    ETLProvenanceService,
    _enum_value,
    stable_json_hash,
)


# ---------------------------------------------------------------------------
# stable_json_hash
# ---------------------------------------------------------------------------

class TestStableJsonHash:
    def test_returns_sha256_prefix(self):
        h = stable_json_hash({"key": "value"})
        assert h.startswith("sha256:")

    def test_deterministic(self):
        payload = {"a": 1, "b": [2, 3]}
        assert stable_json_hash(payload) == stable_json_hash(payload)

    def test_different_payloads_differ(self):
        assert stable_json_hash({"a": 1}) != stable_json_hash({"a": 2})

    def test_key_order_independent(self):
        h1 = stable_json_hash({"a": 1, "b": 2})
        h2 = stable_json_hash({"b": 2, "a": 1})
        assert h1 == h2

    def test_handles_list(self):
        h = stable_json_hash([1, 2, 3])
        assert h.startswith("sha256:")


# ---------------------------------------------------------------------------
# _enum_value
# ---------------------------------------------------------------------------

class TestEnumValue:
    def test_with_enum_value_attr(self):
        class FakeEnum:
            value = "my_value"
        assert _enum_value(FakeEnum()) == "my_value"

    def test_with_plain_string(self):
        assert _enum_value("hello") == "hello"

    def test_with_int(self):
        assert _enum_value(42) == "42"


# ---------------------------------------------------------------------------
# ETLProvenanceService.validate_source_bundle
# ---------------------------------------------------------------------------

GOOD_SOURCE = {
    "source_document_id": "doc-1",
    "source_chunk_id": "chunk-1",
    "document_status": "approved",
    "license_status": "government_open",
    "caps_ref": "CAPS/MATH/GR4",
    "chunk_quality_score": 0.8,
}

class TestETLProvenanceService:
    def setup_method(self):
        self.svc = ETLProvenanceService()

    def test_empty_sources_fails(self):
        result = self.svc.validate_source_bundle(caps_ref="CAPS/MATH/GR4", sources=[])
        assert not result.passed
        assert result.errors

    def test_empty_sources_allowed_when_synthetic(self):
        result = self.svc.validate_source_bundle(
            caps_ref=None, sources=[], allow_synthetic_without_source=True
        )
        assert result.passed

    def test_valid_source_passes(self):
        result = self.svc.validate_source_bundle(
            caps_ref="CAPS/MATH/GR4", sources=[GOOD_SOURCE]
        )
        assert result.passed
        assert result.source_snapshot_hash is not None
        assert result.source_snapshot_hash.startswith("sha256:")

    def test_missing_document_id_fails(self):
        bad = dict(GOOD_SOURCE)
        del bad["source_document_id"]
        result = self.svc.validate_source_bundle(caps_ref=None, sources=[bad])
        assert not result.passed
        assert any("source_document_id" in e for e in result.errors)

    def test_missing_chunk_id_fails(self):
        bad = dict(GOOD_SOURCE)
        del bad["source_chunk_id"]
        result = self.svc.validate_source_bundle(caps_ref=None, sources=[bad])
        assert not result.passed

    def test_bad_document_status_fails(self):
        bad = dict(GOOD_SOURCE, document_status="pending")
        result = self.svc.validate_source_bundle(caps_ref=None, sources=[bad])
        assert not result.passed
        assert any("approved" in e for e in result.errors)

    def test_incompatible_license_fails(self):
        bad = dict(GOOD_SOURCE, license_status="proprietary")
        result = self.svc.validate_source_bundle(caps_ref=None, sources=[bad])
        assert not result.passed

    def test_caps_ref_mismatch_fails(self):
        bad = dict(GOOD_SOURCE, caps_ref="CAPS/SCIENCE/GR4")
        result = self.svc.validate_source_bundle(caps_ref="CAPS/MATH/GR4", sources=[bad])
        assert not result.passed

    def test_low_quality_score_fails(self):
        bad = dict(GOOD_SOURCE, chunk_quality_score=0.3)
        result = self.svc.validate_source_bundle(caps_ref=None, sources=[bad])
        assert not result.passed

    def test_min_sources_not_met_fails(self):
        result = self.svc.validate_source_bundle(
            caps_ref=None, sources=[GOOD_SOURCE], min_sources=2
        )
        assert not result.passed

    def test_snapshot_hash_is_stable(self):
        r1 = self.svc.validate_source_bundle(caps_ref="CAPS/MATH/GR4", sources=[GOOD_SOURCE])
        r2 = self.svc.validate_source_bundle(caps_ref="CAPS/MATH/GR4", sources=[GOOD_SOURCE])
        assert r1.source_snapshot_hash == r2.source_snapshot_hash


# ---------------------------------------------------------------------------
# ContentValidationService.validate_artifact_payload
# ---------------------------------------------------------------------------

class TestContentValidationService:
    def setup_method(self):
        self.svc = ContentValidationService()

    def test_empty_artifact_json_fails(self):
        result = self.svc.validate_artifact_payload(
            artifact_json={},
            caps_ref=None,
            sources=[GOOD_SOURCE],
            artifact_type="lesson",
        )
        assert not result["passed"]
        assert any("empty" in e.lower() for e in result["errors"])

    def test_diagnostic_item_missing_answer_key_fails(self):
        result = self.svc.validate_artifact_payload(
            artifact_json={"title": "Q1"},
            caps_ref=None,
            sources=[GOOD_SOURCE],
            artifact_type="diagnostic_item",
        )
        assert not result["passed"]
        assert any("answer_key" in e for e in result["errors"])

    def test_unsafe_safety_status_fails(self):
        result = self.svc.validate_artifact_payload(
            artifact_json={"safety_status": "flagged"},
            caps_ref=None,
            sources=[GOOD_SOURCE],
            artifact_type="lesson",
        )
        assert not result["passed"]

    def test_valid_lesson_passes(self):
        result = self.svc.validate_artifact_payload(
            artifact_json={"title": "Fractions", "safety_status": "safe"},
            caps_ref="CAPS/MATH/GR4",
            sources=[GOOD_SOURCE],
            artifact_type="lesson",
        )
        assert result["passed"]
        assert result["source_snapshot_hash"] is not None

    def test_diagnostic_item_with_answer_key_passes(self):
        result = self.svc.validate_artifact_payload(
            artifact_json={"title": "Q1", "answer_key": {"q1": "A"}, "safety_status": "passed"},
            caps_ref=None,
            sources=[GOOD_SOURCE],
            artifact_type="diagnostic_item",
        )
        assert result["passed"]
