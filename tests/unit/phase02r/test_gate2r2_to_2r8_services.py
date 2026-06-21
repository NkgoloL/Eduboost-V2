from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from app.services.curriculum.acquisition import (
    AcquisitionPolicy,
    AcquisitionRejectedError,
    ControlledAcquisitionService,
    assert_no_learner_pii_in_source_metadata,
)
from app.services.curriculum.answer_verification import DeterministicMathAnswerVerifier
from app.services.curriculum.claim_validation import Claim, ClaimValidator
from app.services.curriculum.corpus import CorpusBuilder, CorpusChunkCandidate, CorpusRejectedError, versioned_cache_key
from app.services.curriculum.evaluation import RetrievalEvaluationCase, RetrievalEvaluationScorer
from app.services.curriculum.extraction import StructuredTextExtractor
from app.services.curriculum.graph import MappingDraft, MappingRejectedError, build_grade4_mathematics_skeleton
from app.services.curriculum.grounding import GroundingPolicyEngine, RetrievedChunk, require_grounded_or_safe_fallback
from app.services.curriculum.legacy import LegacyArtifactView, LegacyMigrationClassifier
from app.services.curriculum.tutor_grounding import TutorGroundingError, TutorGroundingPolicy, TutorGroundingTrace


def test_gate2r2_acquisition_requires_hash_and_rejects_pii(tmp_path: Path) -> None:
    source = tmp_path / "caps.txt"
    source.write_text("Numbers, operations and relationships", encoding="utf-8")
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    acquired = ControlledAcquisitionService().acquire_local_file(source, expected_sha256=sha)
    assert acquired.sha256 == sha
    with pytest.raises(AcquisitionRejectedError):
        ControlledAcquisitionService().acquire_local_file(source, expected_sha256="0" * 64)
    with pytest.raises(AcquisitionRejectedError):
        assert_no_learner_pii_in_source_metadata({"learner_id": "L1"})


def test_gate2r3_extraction_preserves_page_and_chunk_hashes(tmp_path: Path) -> None:
    source = tmp_path / "caps.txt"
    source.write_text("PAGE ONE\n\nWhole numbers\fPAGE TWO\n\nFractions", encoding="utf-8")
    result = StructuredTextExtractor(max_chunk_chars=80).extract_text_fixture(source, language="en")
    assert [page.page_number for page in result.pages] == [1, 2]
    assert all(len(page.text_sha256) == 64 for page in result.pages)
    assert result.chunks and result.chunks[0].page_start == 1


def test_gate2r4_mapping_requires_human_approval_metadata() -> None:
    for node in build_grade4_mathematics_skeleton():
        node.validate()
    with pytest.raises(MappingRejectedError):
        MappingDraft("chunk", "node", "DEFINED_IN", "machine_proposed", "review_required").validate_for_retrieval()
    MappingDraft("chunk", "node", "DEFINED_IN", "manual", "approved", "reviewer", "2026-06-18T00:00:00Z").validate_for_retrieval()


def test_gate2r5_corpus_requires_approved_tier1_and_versioned_cache() -> None:
    builder = CorpusBuilder()
    candidate = CorpusChunkCandidate(
        chunk_version_id="chunk-1",
        source_version_id="source-1",
        mapping_version_id="map-1",
        authority_tier="tier_1",
        rights_status="approved",
        chunk_review_status="approved",
        mapping_review_status="approved",
        quality_score=0.95,
        language="en",
    )
    manifest = builder.build_manifest(
        corpus_code="g4-maths-en",
        version_number=1,
        scope={"grade": 4, "subject": "Mathematics"},
        language="en",
        embedding_model="test-embedding",
        embedding_version="v1",
        candidates=[candidate],
    )
    assert len(manifest.manifest_sha256) == 64
    assert "epoch:1" in versioned_cache_key(activation_key="g4-maths:en", corpus_version_id="corpus-1", binding_epoch=1)
    with pytest.raises(CorpusRejectedError):
        builder.build_manifest(
            corpus_code="g4-maths-en",
            version_number=1,
            scope={},
            language="en",
            embedding_model="test",
            embedding_version="v1",
            candidates=[candidate.__class__(**{**candidate.__dict__, "authority_tier": "tier_2"})],
        )


def test_gate2r6_generation_grounding_claims_and_answers_are_fail_closed() -> None:
    engine = GroundingPolicyEngine()
    decision = engine.validate_generation_grounding(corpus_version_id=None, requested_objective_ids=["obj-1"], retrieved_chunks=[])
    assert not decision.passed
    with pytest.raises(Exception):
        require_grounded_or_safe_fallback(decision)
    chunk = RetrievedChunk(
        chunk_version_id="chunk-1",
        source_version_id="source-1",
        mapping_version_ids=["map-1"],
        objective_ids=["obj-1"],
        authority_tier="tier_1",
        rights_status="approved",
        review_status="approved",
        corpus_version_id="corpus-1",
        score=0.9,
        language="en",
        text="Learners compare and order whole numbers.",
    )
    passed = engine.validate_generation_grounding(corpus_version_id="corpus-1", requested_objective_ids=["obj-1"], retrieved_chunks=[chunk])
    assert passed.passed and passed.source_snapshot_hash
    claims = ClaimValidator().validate([Claim("curriculum_requirement", "Learners compare whole numbers", ["chunk-1"])])
    assert claims.status == "passed"
    assert DeterministicMathAnswerVerifier().verify_arithmetic_expression(question_expression="2 + 3 * 4", proposed_answer="14").status == "passed"


def test_gate2r7_tutor_requires_grounding_or_explicit_fallback() -> None:
    policy = TutorGroundingPolicy()
    with pytest.raises(TutorGroundingError):
        policy.validate(TutorGroundingTrace("what is CAPS?", [], [], [], None, "passed"))
    policy.validate(TutorGroundingTrace("what is CAPS?", [], [], [], None, "fallback", "No approved corpus available"))


def test_gate2r8_legacy_classification_and_real_eval_thresholds() -> None:
    classifier = LegacyMigrationClassifier()
    assert classifier.classify(LegacyArtifactView("a1", "lesson", True, None, [])).disposition == "published_requires_review"
    positives = [
        RetrievalEvaluationCase(f"p{i}", "en", "Numbers", 1, "query", [f"c{i}"], [f"c{i}"])
        for i in range(18)
    ]
    negatives = [RetrievalEvaluationCase(f"n{i}", "en", "Numbers", 1, "bad query", [], [], True) for i in range(10)]
    metrics = RetrievalEvaluationScorer().score(positives + negatives)
    assert metrics.positive_case_count == 18
    assert metrics.negative_case_count == 10
