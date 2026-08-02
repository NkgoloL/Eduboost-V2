"""
Unit tests for app.services.curriculum_expansion module.

Covers pure-function helpers (record_sha256, dataset_sha256,
forbidden_training_paths, obvious_pii_findings, validate_language_content,
build_training_record, artifact_eligibility_reasons) and lightweight
class-level stubs.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.curriculum_expansion import (
    artifact_eligibility_reasons,
    build_training_record,
    dataset_sha256,
    forbidden_training_paths,
    obvious_pii_findings,
    record_sha256,
    validate_language_content,
    CurriculumExpansionService,
    TrainingDatasetGovernanceService,
)


# ---------------------------------------------------------------------------
# record_sha256 / dataset_sha256
# ---------------------------------------------------------------------------

class TestRecordSha256:
    def test_deterministic(self):
        record = {"a": 1, "b": "two"}
        assert record_sha256(record) == record_sha256(record)

    def test_key_order_invariant(self):
        assert record_sha256({"x": 1, "y": 2}) == record_sha256({"y": 2, "x": 1})

    def test_returns_64_char_hex(self):
        result = record_sha256({"k": "v"})
        assert isinstance(result, str) and len(result) == 64

    def test_different_values_differ(self):
        assert record_sha256({"a": 1}) != record_sha256({"a": 2})


class TestDatasetSha256:
    def test_deterministic(self):
        h = ["abc", "def"]
        assert dataset_sha256(h) == dataset_sha256(h)

    def test_order_invariant(self):
        assert dataset_sha256(["a", "b"]) == dataset_sha256(["b", "a"])

    def test_empty_list(self):
        assert len(dataset_sha256([])) == 64

    def test_differs_with_different_inputs(self):
        assert dataset_sha256(["a"]) != dataset_sha256(["b"])


# ---------------------------------------------------------------------------
# forbidden_training_paths
# ---------------------------------------------------------------------------

class TestForbiddenTrainingPaths:
    def test_empty_dict(self):
        assert forbidden_training_paths({}) == []

    def test_flat_forbidden_key(self):
        findings = forbidden_training_paths({"learner_id": "123"})
        assert any("learner_id" in f for f in findings)

    def test_nested_forbidden_key(self):
        findings = forbidden_training_paths({"nested": {"email": "a@b.com"}})
        assert any("email" in f for f in findings)

    def test_list_recursion(self):
        findings = forbidden_training_paths([{"user_id": "u1"}])
        assert any("user_id" in f for f in findings)

    def test_clean_record(self):
        assert forbidden_training_paths({"title": "Chapter 1", "content": "Safe text."}) == []

    def test_multiple_forbidden_keys(self):
        data = {"learner_id": "l1", "guardian_id": "g1", "ok_key": "ok"}
        assert len(forbidden_training_paths(data)) >= 2


# ---------------------------------------------------------------------------
# obvious_pii_findings
# ---------------------------------------------------------------------------

class TestObviousPiiFindings:
    def test_no_pii(self):
        assert obvious_pii_findings({"text": "Hello, world!"}) == []

    def test_detects_email(self):
        assert len(obvious_pii_findings({"email": "user@example.com"})) >= 1

    def test_detects_sa_phone(self):
        assert len(obvious_pii_findings({"phone": "061 234 5678"})) >= 1

    def test_detects_13_digit_id(self):
        assert len(obvious_pii_findings({"id_number": "9001015009087"})) >= 1

    def test_nested_pii(self):
        assert len(obvious_pii_findings({"meta": {"contact": "u@site.org"}})) >= 1


# ---------------------------------------------------------------------------
# validate_language_content
# ---------------------------------------------------------------------------

class TestValidateLanguageContent:
    def test_valid_english(self):
        assert validate_language_content({"text": "Good morning learners."}, "en") == []

    def test_placeholder_detected(self):
        findings = validate_language_content({"text": "TODO: write content here."}, "en")
        assert "placeholder_text" in findings

    def test_unsupported_language(self):
        findings = validate_language_content({"text": "Bonjour."}, "fr")
        assert "unsupported_language" in findings

    def test_all_supported_languages(self):
        for lang in ("en", "af", "zu", "xh", "st", "tn", "nso"):
            findings = validate_language_content({"text": "Hello world learning content."}, lang)
            assert "unsupported_language" not in findings, f"Failed for {lang}"


# ---------------------------------------------------------------------------
# build_training_record
# ---------------------------------------------------------------------------

def _make_artifact(**kwargs):
    a = MagicMock()
    a.artifact_id = "art-001"
    a.artifact_hash = "hash001"
    a.scope_id = "scope-gr10"
    a.caps_ref = "CAPS/MATH/GR10/001"
    a.grade = 10
    a.subject_code = "MATH"
    a.language = "en"
    a.content_layer = "lesson_plans"
    a.source_snapshot_hash = "snap001"
    a.quality_score = 0.85
    a.caps_alignment_score = 0.90
    a.artifact_json = {"topic": "algebra"}
    a.version_number = 2
    a.artifact_version = None
    for k, v in kwargs.items():
        setattr(a, k, v)
    return a


class TestBuildTrainingRecord:
    def test_required_fields_present(self):
        record = build_training_record(_make_artifact())
        for f in ("schema_version", "artifact_id", "artifact_hash", "grade", "content"):
            assert f in record

    def test_quality_score_is_float(self):
        assert isinstance(build_training_record(_make_artifact()).get("quality_score"), float)

    def test_none_quality_score(self):
        assert build_training_record(_make_artifact(quality_score=None))["quality_score"] is None

    def test_schema_version_value(self):
        assert build_training_record(_make_artifact())["schema_version"] == "phase7-training-record-v1"


# ---------------------------------------------------------------------------
# artifact_eligibility_reasons
# ---------------------------------------------------------------------------

def _make_eligible_artifact(**kwargs):
    a = MagicMock()
    a.status = MagicMock()
    a.status.value = "published"
    a.artifact_hash = "hash001"
    a.source_snapshot_hash = "snap001"
    a.quality_score = 0.90
    a.caps_alignment_score = 0.90
    a.safety_status = "safe"
    a.content_layer = MagicMock()
    a.content_layer.value = "lesson_plans"
    a.answer_key_verified = True
    a.artifact_json = {"topic": "algebra"}
    a.language = "en"
    src = MagicMock()
    src.license_status = MagicMock()
    src.license_status.value = "cc-by"
    src.source_hash = "src-hash"
    src.chunk_hash = None
    a.sources = [src]
    for k, v in kwargs.items():
        setattr(a, k, v)
    return a


class TestArtifactEligibilityReasons:
    def test_fully_eligible(self):
        reasons = artifact_eligibility_reasons(
            _make_eligible_artifact(),
            require_published=True,
            min_quality_score=0.7,
            min_caps_alignment_score=0.7,
        )
        assert reasons == []

    def test_missing_artifact_hash(self):
        reasons = artifact_eligibility_reasons(
            _make_eligible_artifact(artifact_hash=None),
            require_published=False,
            min_quality_score=0.7,
            min_caps_alignment_score=0.7,
        )
        assert "missing_artifact_hash" in reasons

    def test_low_quality_score(self):
        reasons = artifact_eligibility_reasons(
            _make_eligible_artifact(quality_score=0.3),
            require_published=False,
            min_quality_score=0.7,
            min_caps_alignment_score=0.7,
        )
        assert "quality_below_threshold" in reasons

    def test_safety_not_approved(self):
        reasons = artifact_eligibility_reasons(
            _make_eligible_artifact(safety_status="pending_review"),
            require_published=False,
            min_quality_score=0.7,
            min_caps_alignment_score=0.7,
        )
        assert "safety_not_approved" in reasons

    def test_forbidden_fields(self):
        reasons = artifact_eligibility_reasons(
            _make_eligible_artifact(artifact_json={"learner_id": "l1", "text": "ok"}),
            require_published=False,
            min_quality_score=0.7,
            min_caps_alignment_score=0.7,
        )
        assert "forbidden_operational_fields" in reasons

    def test_missing_sources(self):
        reasons = artifact_eligibility_reasons(
            _make_eligible_artifact(sources=[]),
            require_published=False,
            min_quality_score=0.7,
            min_caps_alignment_score=0.7,
        )
        assert "missing_sources" in reasons


# ---------------------------------------------------------------------------
# Service class initialisation
# ---------------------------------------------------------------------------

class TestCurriculumExpansionServiceInit:
    def test_init_defaults(self):
        db = AsyncMock()
        svc = CurriculumExpansionService(db=db)
        assert svc.db is db
        assert svc.registry is not None

    def test_init_custom_registry(self):
        db = AsyncMock()
        registry = MagicMock()
        svc = CurriculumExpansionService(db=db, registry=registry)
        assert svc.registry is registry

    def test_eligible_statuses_contains_published(self):
        db = AsyncMock()
        svc = CurriculumExpansionService(db=db)
        assert "published" in svc._eligible_statuses()


class TestTrainingDatasetGovernanceServiceInit:
    def test_init(self):
        db = AsyncMock()
        svc = TrainingDatasetGovernanceService(db=db)
        assert svc.db is db
