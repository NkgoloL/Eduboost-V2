import os
from typing import Any, cast
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from app.services.curriculum import retrieval
from app.services.curriculum.phase02r_verification import validate_required_paths
from app.services.curriculum.legacy import (
    LegacyArtifactView,
    LegacyMigrationClassifier,
    LegacyDispositionDecision,
)
from app.services.curriculum.grounding import (
    GroundingPolicyEngine,
    GroundingDecision,
    RetrievedChunk,
    GroundingRejectedError,
    require_grounded_or_safe_fallback,
)
from app.services.curriculum.object_storage import (
    LocalImmutableObjectStore,
    ObjectStorageRejectedError,
)
from app.services.curriculum.rights_policy import (
    RightsPolicyEngine,
    RightsDeniedError,
    RightsRequestContext,
    RightsDecisionView,
    RightsUse,
)
from app.services.curriculum.acquisition import (
    ControlledAcquisitionService,
    AcquisitionPolicy,
    AcquisitionRejectedError,
    validate_may_store_original,
)
from app.services.curriculum.evaluation import (
    RetrievalEvaluationCase,
    RetrievalEvaluationScorer,
    Gate2R8EvaluationPolicy,
    EvaluationRejectedError,
)
from app.services.curriculum.generation import (
    GroundedGenerationRequest,
    GroundedGenerationRejectedError,
    GroundedGenerationService,
    GeneratedClaim,
    GeneratedAssessmentItem,
    SourceReference,
)


def test_curriculum_retrieval_facade():
    assert hasattr(retrieval, "ActiveCorpusRetriever")
    assert hasattr(retrieval, "RetrievalHit")
    assert len(retrieval.__all__) == 8


def test_phase02r_verification_paths():
    # Missing gate returns empty errors
    assert validate_required_paths("unknown_gate") == []

    # Valid gate returns list
    res = validate_required_paths("2R.2")
    assert isinstance(res, list)


def test_legacy_migration_classifier_branches():
    classifier = LegacyMigrationClassifier()

    # 1. Synthetic fixture
    art_synth = LegacyArtifactView(
        artifact_id="a_synth",
        artifact_type="lesson",
        published=False,
        source_snapshot_hash=None,
        source_chunk_ids=[],
        synthetic_fixture=True,
    )
    assert classifier.classify(art_synth).disposition == "synthetic_fixture"

    # 2. Grounded and verified
    art_gv = LegacyArtifactView(
        artifact_id="a_gv",
        artifact_type="diagnostic_item",
        published=True,
        source_snapshot_hash="sha_snap",
        source_chunk_ids=["c1"],
        answer_key_verified=True,
    )
    assert classifier.classify(art_gv).disposition == "grounded_verified"

    # 3. Grounded unverified
    art_gu = LegacyArtifactView(
        artifact_id="a_gu",
        artifact_type="diagnostic_item",
        published=True,
        source_snapshot_hash="sha_snap",
        source_chunk_ids=["c1"],
        answer_key_verified=False,
    )
    assert classifier.classify(art_gu).disposition == "grounded_unverified"

    # 4. Published requires review (not grounded, published)
    art_pub = LegacyArtifactView(
        artifact_id="a_pub",
        artifact_type="lesson",
        published=True,
        source_snapshot_hash=None,
        source_chunk_ids=[],
    )
    assert classifier.classify(art_pub).disposition == "published_requires_review"

    # 5. Legacy ungrounded (not grounded, not published)
    art_ung = LegacyArtifactView(
        artifact_id="a_ung",
        artifact_type="lesson",
        published=False,
        source_snapshot_hash=None,
        source_chunk_ids=[],
    )
    assert classifier.classify(art_ung).disposition == "legacy_ungrounded"

    # Summarize
    summary = classifier.summarize([art_synth, art_gv, art_gu, art_pub, art_ung])
    assert summary["synthetic_fixture"] == 1
    assert summary["grounded_verified"] == 1
    assert summary["grounded_unverified"] == 1
    assert summary["published_requires_review"] == 1
    assert summary["legacy_ungrounded"] == 1


def test_grounding_policy_engine_branches():
    engine = GroundingPolicyEngine()

    chunk_ok = RetrievedChunk(
        chunk_version_id="chk_1",
        source_version_id="src_1",
        mapping_version_ids=["m1"],
        objective_ids=["obj_1"],
        authority_tier="tier_1",
        rights_status="approved",
        review_status="approved",
        corpus_version_id="corpus_v1",
        score=0.9,
        language="en",
        text="Sample curriculum chunk text.",
    )

    # 1. Missing objectives
    dec1 = engine.validate_generation_grounding(
        corpus_version_id="corpus_v1",
        requested_objective_ids=[],
        retrieved_chunks=[chunk_ok],
    )
    assert dec1.passed is False
    assert "requested_objectives_missing" in dec1.failure_reasons

    # 2. Tier 1 grounding missing
    chunk_tier2 = RetrievedChunk(
        chunk_version_id="chk_2",
        source_version_id="src_1",
        mapping_version_ids=["m1"],
        objective_ids=["obj_1"],
        authority_tier="tier_2",
        rights_status="approved",
        review_status="approved",
        corpus_version_id="corpus_v1",
        score=0.8,
        language="en",
        text="Sample tier 2 text.",
    )
    dec2 = engine.validate_generation_grounding(
        corpus_version_id="corpus_v1",
        requested_objective_ids=["obj_1"],
        retrieved_chunks=[chunk_tier2],
    )
    assert dec2.passed is False
    assert "tier_1_grounding_missing" in dec2.failure_reasons

    # 3. Mixed corpus version, rights not approved, chunk not approved
    chunk_bad = RetrievedChunk(
        chunk_version_id="chk_bad",
        source_version_id="src_1",
        mapping_version_ids=["m1"],
        objective_ids=["obj_1"],
        authority_tier="tier_1",
        rights_status="rejected",
        review_status="pending",
        corpus_version_id="different_corpus",
        score=0.7,
        language="en",
        text="Bad chunk",
    )
    dec3 = engine.validate_generation_grounding(
        corpus_version_id="corpus_v1",
        requested_objective_ids=["obj_1"],
        retrieved_chunks=[chunk_bad],
    )
    assert dec3.passed is False
    assert "mixed_corpus_version" in dec3.failure_reasons
    assert "rights_not_approved" in dec3.failure_reasons
    assert "chunk_not_approved" in dec3.failure_reasons

    # 4. require_grounded_or_safe_fallback
    passed_dec = GroundingDecision(passed=True, status="passed", source_snapshot_hash="hash")
    require_grounded_or_safe_fallback(passed_dec)

    failed_dec = GroundingDecision(passed=False, status="failed", source_snapshot_hash=None)
    require_grounded_or_safe_fallback(failed_dec, fallback_reason="safe_deterministic_fallback")

    with pytest.raises(GroundingRejectedError, match="requires grounding or explicit safe fallback"):
        require_grounded_or_safe_fallback(failed_dec, fallback_reason=None)


def test_object_storage_additional_branches(tmp_path):
    store = LocalImmutableObjectStore(root=tmp_path)

    # 1. to_uri path outside root
    outside = Path("/tmp/outside_path_for_storage_test")
    with pytest.raises(ObjectStorageRejectedError, match="outside storage root"):
        store.to_uri(outside)

    # 2. Existing object with different bytes
    content1 = b"first content"
    content2 = b"second content"
    f1 = tmp_path / "f1.txt"
    f2 = tmp_path / "f2.txt"
    f1.write_bytes(content1)
    f2.write_bytes(content2)

    import hashlib
    sha1 = hashlib.sha256(content1).hexdigest()

    obj1 = store.put_file(f1, expected_sha256=sha1, suffix=".txt")

    # Corrupt the target file
    obj1.path.write_bytes(b"corrupted bytes")
    with pytest.raises(ObjectStorageRejectedError, match="contains different bytes"):
        store.put_file(f1, expected_sha256=sha1, suffix=".txt")


def test_rights_policy_branches():
    use = RightsUse.GENERATE_DERIVATIVE

    # 1. Inactive decision status
    bad_dec = {
        "decision_status": "revoked",
        "may_generate_derivatives": True,
        "conditions": {},
    }
    with pytest.raises(RightsDeniedError, match="decision status is 'revoked'"):
        RightsPolicyEngine.require_allowed(bad_dec, use)

    # 2. Naive datetime expires_at
    naive_expired = {
        "decision_status": "approved",
        "expires_at": datetime(2020, 1, 1),
        "may_generate_derivatives": True,
        "conditions": {},
    }
    with pytest.raises(RightsDeniedError, match="rights decision has expired"):
        RightsPolicyEngine.require_allowed(naive_expired, use)

    # 3. Conditional approval without conditions
    cond_empty = {
        "decision_status": "approved_with_conditions",
        "may_generate_derivatives": True,
        "conditions": {},
    }
    with pytest.raises(RightsDeniedError, match="no machine-readable conditions"):
        RightsPolicyEngine.require_allowed(cond_empty, use)

    # 4. Malformed conditions
    cond_mal_lang = {
        "decision_status": "approved",
        "may_generate_derivatives": True,
        "conditions": {"permitted_languages": "not_a_list"},
    }
    with pytest.raises(RightsDeniedError, match="permitted_languages is malformed"):
        RightsPolicyEngine.require_allowed(cond_mal_lang, use)

    cond_mal_chan = {
        "decision_status": "approved",
        "may_generate_derivatives": True,
        "conditions": {"permitted_channels": "not_a_list"},
    }
    with pytest.raises(RightsDeniedError, match="permitted_channels is malformed"):
        RightsPolicyEngine.require_allowed(cond_mal_chan, use)

    cond_mal_jur = {
        "decision_status": "approved",
        "may_generate_derivatives": True,
        "conditions": {"permitted_jurisdictions": "not_a_list"},
    }
    with pytest.raises(RightsDeniedError, match="permitted_jurisdictions is malformed"):
        RightsPolicyEngine.require_allowed(cond_mal_jur, use)

    cond_mal_len = {
        "decision_status": "approved",
        "may_generate_derivatives": True,
        "conditions": {"maximum_excerpt_length": "not_an_int"},
    }
    with pytest.raises(RightsDeniedError, match="maximum_excerpt_length is malformed"):
        RightsPolicyEngine.require_allowed(cond_mal_len, use)

    # 5. Excerpt length exceeded
    cond_len = {
        "decision_status": "approved",
        "may_generate_derivatives": True,
        "conditions": {"maximum_excerpt_length": 100},
    }
    ctx_len = RightsRequestContext(excerpt_length=150)
    with pytest.raises(RightsDeniedError, match="exceeds the permitted length"):
        RightsPolicyEngine.require_allowed(cond_len, use, context=ctx_len)

    # 6. is_allowed
    assert RightsPolicyEngine.is_allowed(bad_dec, use) is False
    valid_dec = {
        "decision_status": "approved",
        "may_generate_derivatives": True,
        "conditions": {},
    }
    assert RightsPolicyEngine.is_allowed(valid_dec, use) is True


def test_acquisition_policy_branches(tmp_path):
    store = LocalImmutableObjectStore(root=tmp_path)
    service = ControlledAcquisitionService(object_store=store)

    # 1. validate_may_store_original
    with pytest.raises(AcquisitionRejectedError, match="missing rights decision"):
        validate_may_store_original(None)

    with pytest.raises(AcquisitionRejectedError, match="rights decision is not approved"):
        validate_may_store_original({"decision_status": "rejected"})

    with pytest.raises(AcquisitionRejectedError, match="does not allow storing original"):
        validate_may_store_original({"decision_status": "approved", "may_store_original": False})

    with pytest.raises(AcquisitionRejectedError, match="rights decision is expired"):
        validate_may_store_original({
            "decision_status": "approved",
            "may_store_original": True,
            "expires_at": "2020-01-01T00:00:00Z",
        })

    valid_rights = {
        "decision_status": "approved",
        "may_store_original": True,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
    }

    # 2. Source file missing
    with pytest.raises(AcquisitionRejectedError, match="does not exist"):
        service.acquire_local_file(tmp_path / "missing.txt", expected_sha256=None, rights_decision=valid_rights)

    # 3. Media type for .md
    md_file = tmp_path / "doc.md"
    md_file.write_text("# Markdown Title\nContent here")
    import hashlib
    md_sha = hashlib.sha256(md_file.read_bytes()).hexdigest()
    assert service._media_type_for(md_file) == "text/markdown"

    # 4. Source file empty
    empty_file = tmp_path / "empty.pdf"
    empty_file.write_bytes(b"")
    with pytest.raises(AcquisitionRejectedError, match="source file is empty"):
        service.acquire_local_file(empty_file, expected_sha256=None, rights_decision=valid_rights)

    # 5. Source file exceeds max size
    pol_small = AcquisitionPolicy(max_file_size_bytes=5)
    srv_small = ControlledAcquisitionService(policy=pol_small, object_store=store)
    with pytest.raises(AcquisitionRejectedError, match="exceeds maximum allowed size"):
        srv_small.acquire_local_file(md_file, expected_sha256=None, rights_decision=valid_rights)

    # 6. Expected sha required
    pol_req_sha = AcquisitionPolicy(require_expected_sha256=True)
    srv_sha = ControlledAcquisitionService(policy=pol_req_sha, object_store=store)
    with pytest.raises(AcquisitionRejectedError, match="expected_sha256 is required"):
        srv_sha.acquire_local_file(md_file, expected_sha256=None, rights_decision=valid_rights)

    # 7. Media type not allowed
    bin_file = tmp_path / "file.bin"
    bin_file.write_bytes(b"12345")
    with pytest.raises(AcquisitionRejectedError, match="file extension is not allowed"):
        service.acquire_local_file(bin_file, expected_sha256=None, rights_decision=valid_rights)

    # 8. persist_object=False
    acq_nofile = service.acquire_local_file(
        md_file,
        expected_sha256=md_sha,
        rights_decision=valid_rights,
        persist_object=False,
    )
    assert acq_nofile.storage_backend == "local-fixture"
    assert md_sha in acq_nofile.object_uri


def test_evaluation_branches():
    # 1. RetrievalEvaluationCase validation errors
    with pytest.raises(EvaluationRejectedError, match="case_id and query are required"):
        RetrievalEvaluationCase(case_id="", language="en", strand="S", term=1, query="").normalized()

    with pytest.raises(EvaluationRejectedError, match="unsupported language"):
        RetrievalEvaluationCase(case_id="c1", language="fr", strand="S", term=1, query="Q", expected_chunk_ids=("c1",)).normalized()

    with pytest.raises(EvaluationRejectedError, match="negative case.*must not define expected"):
        RetrievalEvaluationCase(case_id="c1", language="en", strand="S", term=1, query="Q", is_negative_case=True, expected_chunk_ids=("c1",)).normalized()

    with pytest.raises(EvaluationRejectedError, match="positive case.*must define expected"):
        RetrievalEvaluationCase(case_id="c1", language="en", strand="S", term=1, query="Q", is_negative_case=False, expected_chunk_ids=()).normalized()

    # 2. Scorer validation errors
    scorer = RetrievalEvaluationScorer()
    with pytest.raises(EvaluationRejectedError, match="evaluation dataset is empty"):
        scorer.score([])

    c_valid = RetrievalEvaluationCase(case_id="c1", language="en", strand="S", term=1, query="Q", expected_chunk_ids=("c1",))
    with pytest.raises(EvaluationRejectedError, match="k must be positive"):
        scorer.score([c_valid], k=0)

    with pytest.raises(EvaluationRejectedError, match="requires at least.*positive cases"):
        scorer.score([c_valid], k=5)

    # 3. Policy threshold failures
    policy = Gate2R8EvaluationPolicy()
    assert policy.thresholds["min_recall_at_k"] == 0.90


def test_generation_request_and_validation_branches():
    # 1. GroundedGenerationRequest.normalized validation errors
    def _make_req(**kwargs):
        data = {
            "artifact_type": "lesson",
            "activation_key": "act_key",
            "corpus_version_id": "corp_v1",
            "binding_epoch": 1,
            "language": "en",
            "topic": "Addition",
            "objective_ids": ("obj_1",),
        }
        data.update(kwargs)
        return GroundedGenerationRequest(**data)

    with pytest.raises(GroundedGenerationRejectedError, match="activation_key is required"):
        _make_req(activation_key="").normalized()

    with pytest.raises(GroundedGenerationRejectedError, match="corpus_version_id is required"):
        _make_req(corpus_version_id="").normalized()

    with pytest.raises(GroundedGenerationRejectedError, match="binding_epoch must be positive"):
        _make_req(binding_epoch=0).normalized()

    with pytest.raises(GroundedGenerationRejectedError, match="unsupported language"):
        _make_req(language="fr").normalized()

    with pytest.raises(GroundedGenerationRejectedError, match="topic is required"):
        _make_req(topic="").normalized()

    with pytest.raises(GroundedGenerationRejectedError, match="at least one objective_id"):
        _make_req(objective_ids=()).normalized()

    with pytest.raises(GroundedGenerationRejectedError, match="top_k must be positive"):
        _make_req(top_k=0).normalized()

    # 2. _validate_artifact_parts errors
    gen_service = GroundedGenerationService(retriever=MagicMock())

    claim_ok = GeneratedClaim(
        claim_type="curriculum_requirement",
        text="Text",
        supporting_chunk_ids=("chk_1",),
        overlap_ratio=0.05,
    )
    item_fail = GeneratedAssessmentItem(
        item_id="item_fail",
        prompt="2+2",
        answer_expression="2+2",
        proposed_answer="5",
        expected_answer="4",
        answer_verification_status="failed",
        source_chunk_ids=("chk_1",),
        answer_verification_hash="hash",
    )

    def _make_source_ref(**kwargs) -> SourceReference:
        data = {
            "chunk_version_id": "chk_1",
            "source_version_id": "src_1",
            "mapping_version_id": "map_1",
            "curriculum_node_version_id": "node_1",
            "corpus_version_id": "corp_1",
            "binding_epoch": 1,
            "authority_tier": "tier_1",
            "rights_status": "approved",
            "review_status": "approved",
            "page_start": 1,
            "page_end": 2,
            "source_snapshot_hash": "snap_hash",
            "text_sha256": "text_hash",
            "retrieval_score": 0.9,
            "matched_terms": ("term",),
        }
        data.update(kwargs)
        return SourceReference(**data)

    ref_tier2 = _make_source_ref(authority_tier="tier_2")
    with pytest.raises(GroundedGenerationRejectedError, match="tier_1 source reference is required"):
        gen_service._validate_artifact_parts(claims=(claim_ok,), items=(), refs=(ref_tier2,))

    ref_unapproved = _make_source_ref(review_status="pending")
    with pytest.raises(GroundedGenerationRejectedError, match="all source references must be approved"):
        gen_service._validate_artifact_parts(claims=(claim_ok,), items=(), refs=(ref_unapproved,))


def test_phase02r_verification_missing_path(monkeypatch):
    from unittest.mock import MagicMock
    from app.services.curriculum import phase02r_verification

    # Mock Path.is_file to return False for a path to test line 78
    original_is_file = Path.is_file
    def mock_is_file(self):
        if "acquisition.py" in str(self):
            return False
        return original_is_file(self)

    monkeypatch.setattr(Path, "is_file", mock_is_file)
    errors = phase02r_verification.validate_required_paths("2R.2")
    assert any("missing required 2R.2 implementation path" in e for e in errors)


def test_extraction_additional_branches(tmp_path, monkeypatch):
    import sys
    from typing import cast
    from app.services.curriculum.extraction import (
        StructuredTextExtractor,
        ExtractionRejectedError,
        validate_extraction_result,
        ExtractionResult,
        ExtractedPage,
        ChunkProposal,
        ExtractedSection,
    )

    # 1. Invalid extractor params
    with pytest.raises(ExtractionRejectedError, match="max_chunk_chars must be at least 120"):
        StructuredTextExtractor(max_chunk_chars=100)

    with pytest.raises(ExtractionRejectedError, match="min_chunk_chars cannot be negative"):
        StructuredTextExtractor(min_chunk_chars=-1)

    extractor = StructuredTextExtractor()

    # 2. Missing text fixture
    with pytest.raises(ExtractionRejectedError, match="source text fixture does not exist"):
        extractor.extract_text_fixture(tmp_path / "missing.txt", language="en")

    # 3. Missing pdf source
    with pytest.raises(ExtractionRejectedError, match="source PDF does not exist"):
        extractor.extract_pdf(tmp_path / "missing.pdf", language="en")

    # 4. Native pdf extraction with mock pypdf
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 mock")

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "NUMBERS AND OPERATIONS:\nLearners count to 100."
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_reader.is_encrypted = True

    mock_pypdf = MagicMock()
    mock_pypdf.PdfReader.return_value = mock_reader
    monkeypatch.setitem(sys.modules, "pypdf", mock_pypdf)

    res_pdf = extractor.extract_pdf(pdf_file, language="en")
    assert len(res_pdf.pages) == 1
    assert "pdf_was_encrypted_empty_password_accepted" in res_pdf.warnings

    # 5. validate_extraction_result errors
    valid_sha = "a" * 64
    page_ok = ExtractedPage(page_number=1, text="Page 1", text_sha256=valid_sha, language="en", extraction_confidence=1.0)
    sec_ok = ExtractedSection(section_order=1, heading="Intro", page_start=1, page_end=1, text_sha256=valid_sha)
    chunk_ok = ChunkProposal(
        chunk_order=1,
        page_start=1,
        page_end=1,
        text="Sample chunk content.",
        text_sha256=valid_sha,
        section_heading="Intro",
        language="en",
        quality_score=0.9,
    )

    # Empty pages
    res_no_pages = ExtractionResult(pages=[], sections=[sec_ok], chunks=[chunk_ok], text_sha256=valid_sha, warnings=[], quality_score=0.9)
    assert any("has no pages" in e for e in validate_extraction_result(res_no_pages))

    # Empty sections
    res_no_sec = ExtractionResult(pages=[page_ok], sections=[], chunks=[chunk_ok], text_sha256=valid_sha, warnings=[], quality_score=0.9)
    assert any("has no sections" in e for e in validate_extraction_result(res_no_sec))

    # Empty chunks
    res_no_chunk = ExtractionResult(pages=[page_ok], sections=[sec_ok], chunks=[], text_sha256=valid_sha, warnings=[], quality_score=0.9)
    assert any("has no chunks" in e for e in validate_extraction_result(res_no_chunk))

    # Low quality
    res_low_q = ExtractionResult(pages=[page_ok], sections=[sec_ok], chunks=[chunk_ok], text_sha256=valid_sha, warnings=[], quality_score=0.1)
    assert any("quality score is below" in e for e in validate_extraction_result(res_low_q))

    # Invalid sha and language
    page_bad_sha = ExtractedPage(page_number=1, text="Page", text_sha256="bad", language="zu", extraction_confidence=1.0)
    res_bad_page = ExtractionResult(pages=[page_bad_sha], sections=[sec_ok], chunks=[chunk_ok], text_sha256=valid_sha, warnings=[], quality_score=0.9)
    errs = validate_extraction_result(res_bad_page)
    assert any("invalid text_sha256" in e for e in errs)
    assert any("invalid language" in e for e in errs)

    # Invalid chunk
    chunk_bad = ChunkProposal(chunk_order=1, page_start=2, page_end=1, text="  ", text_sha256="bad", section_heading="H", language="zu", quality_score=0.9)
    res_bad_chk = ExtractionResult(pages=[page_ok], sections=[sec_ok], chunks=[chunk_bad], text_sha256=valid_sha, warnings=[], quality_score=0.9)
    chk_errs = validate_extraction_result(res_bad_chk)
    assert any("invalid language" in e for e in chk_errs)
    assert any("invalid text_sha256" in e for e in chk_errs)
    assert any("invalid page range" in e for e in chk_errs)
    assert any("empty text" in e for e in chk_errs)


def test_corpus_additional_branches():
    from app.services.curriculum.corpus import (
        _require_non_empty,
        build_activation_key,
        parse_activation_key,
        CorpusBuilder,
        CorpusRejectedError,
        CorpusChunkCandidate,
    )

    # 1. _require_non_empty
    with pytest.raises(CorpusRejectedError, match="field_x is required"):
        _require_non_empty("", "field_x")

    # 2. build_activation_key
    with pytest.raises(CorpusRejectedError, match="unsupported delivery language"):
        build_activation_key(delivery_language="fr")

    with pytest.raises(CorpusRejectedError, match="grade must be positive"):
        build_activation_key(grade=0)

    with pytest.raises(CorpusRejectedError, match="parts must be non-empty and must not contain ':'"):
        build_activation_key(curriculum_code="CAPS:EXTRA")

    key = build_activation_key()
    assert key == "CAPS:g4:MATH:en:global"

    # 3. parse_activation_key
    with pytest.raises(CorpusRejectedError, match="must contain curriculum, grade, subject, language, tenant"):
        parse_activation_key("CAPS:g4")

    with pytest.raises(CorpusRejectedError, match="grade must be encoded as g<number>"):
        parse_activation_key("CAPS:grade4:MATH:en:global")

    with pytest.raises(CorpusRejectedError, match="language is unsupported"):
        parse_activation_key("CAPS:g4:MATH:fr:global")

    # 4. CorpusBuilder candidate evaluation
    builder = CorpusBuilder()

    def _make_candidate(**kwargs) -> CorpusChunkCandidate:
        data = {
            "chunk_version_id": "chk_v1",
            "source_version_id": "src_v1",
            "mapping_version_id": "map_v1",
            "curriculum_node_version_id": "node_v1",
            "language": "en",
            "rights_status": "approved",
            "may_use_for_retrieval": True,
            "may_embed": True,
            "source_status": "active",
            "chunk_review_status": "approved",
            "extraction_review_status": "approved",
            "mapping_review_status": "approved",
            "authority_tier": "tier_1",
            "quality_score": 0.95,
            "language_status": "official_source",
            "synthetic_fixture": False,
            "unresolved_security_warnings": (),
            "page_start": 1,
            "page_end": 2,
            "text_sha256": "a" * 64,
            "retrieval_text": "Sample text",
        }
        data.update(kwargs)
        return CorpusChunkCandidate(**cast(Any, data))

    cand_ok = _make_candidate()
    dec_ok = builder.evaluate_candidate(cand_ok, language="en")
    assert dec_ok.eligible is True

    # Rejection reasons
    cand_bad = _make_candidate(
        language="af",
        rights_status="rejected",
        may_use_for_retrieval=False,
        may_embed=False,
        source_status="draft",
        chunk_review_status="pending",
        extraction_review_status="pending",
        mapping_review_status="pending",
        authority_tier="tier_unknown",
        quality_score=0.5,
        language_status="machine_translated",
        synthetic_fixture=True,
        unresolved_security_warnings=("warning",),
        page_start=5,
        page_end=2,
        text_sha256="bad",
        retrieval_text="",
    )
    dec_bad = builder.evaluate_candidate(cand_bad, language="en")
    assert dec_bad.eligible is False
    assert len(dec_bad.reasons) >= 10

    # 5. build_manifest validation errors
    with pytest.raises(CorpusRejectedError, match="invalid corpus language"):
        builder.build_manifest(
            corpus_code="MATH_G4",
            version_number=1,
            scope={"grade": 4},
            language="fr",
            embedding_model="emb",
            embedding_version="v1",
            candidates=[cand_ok],
        )

    with pytest.raises(CorpusRejectedError, match="version_number must be positive"):
        builder.build_manifest(
            corpus_code="MATH_G4",
            version_number=0,
            scope={"grade": 4},
            language="en",
            embedding_model="emb",
            embedding_version="v1",
            candidates=[cand_ok],
        )

    with pytest.raises(CorpusRejectedError, match="scope is required"):
        builder.build_manifest(
            corpus_code="MATH_G4",
            version_number=1,
            scope={},
            language="en",
            embedding_model="emb",
            embedding_version="v1",
            candidates=[cand_ok],
        )

    with pytest.raises(CorpusRejectedError, match="activation_key language must match"):
        builder.build_manifest(
            corpus_code="MATH_G4",
            version_number=1,
            scope={"grade": 4},
            language="en",
            embedding_model="emb",
            embedding_version="v1",
            candidates=[cand_ok],
            activation_key="CAPS:g4:MATH:af:global",
        )

    with pytest.raises(CorpusRejectedError, match="requires at least one approved candidate"):
        builder.build_manifest(
            corpus_code="MATH_G4",
            version_number=1,
            scope={"grade": 4},
            language="en",
            embedding_model="emb",
            embedding_version="v1",
            candidates=[],
        )

    cand_tier2 = _make_candidate(authority_tier="tier_2")
    with pytest.raises(CorpusRejectedError, match="requires Tier 1 authority coverage"):
        builder.build_manifest(
            corpus_code="MATH_G4",
            version_number=1,
            scope={"grade": 4},
            language="en",
            embedding_model="emb",
            embedding_version="v1",
            candidates=[cand_tier2],
        )


def test_corpus_retriever_and_projections_expansion():
    from app.services.curriculum.corpus import (
        CorpusBuilder,
        CorpusChunkCandidate,
        FrozenCorpusPackage,
        RetrievalProjection,
        RetrievalProjectionBuilder,
        ActiveCorpusBinding,
        ActiveCorpusRetriever,
        RetrievalQuery,
        CorpusActivationPlanner,
        versioned_cache_key,
        CorpusRejectedError,
    )

    builder = CorpusBuilder()

    def _make_candidate(**kwargs) -> CorpusChunkCandidate:
        data = {
            "chunk_version_id": "chk_v1",
            "source_version_id": "src_v1",
            "mapping_version_id": "map_v1",
            "curriculum_node_version_id": "node_v1",
            "language": "en",
            "rights_status": "approved",
            "may_use_for_retrieval": True,
            "may_embed": True,
            "source_status": "active",
            "chunk_review_status": "approved",
            "extraction_review_status": "approved",
            "mapping_review_status": "approved",
            "authority_tier": "tier_1",
            "quality_score": 0.95,
            "language_status": "official_source",
            "synthetic_fixture": False,
            "unresolved_security_warnings": (),
            "page_start": 1,
            "page_end": 2,
            "text_sha256": "a" * 64,
            "retrieval_text": "Sample text for mathematics",
        }
        data.update(kwargs)
        return CorpusChunkCandidate(**cast(Any, data))

    cand = _make_candidate()

    # 1. candidate language unsupported check
    cand_bad_lang = _make_candidate(language="fr")
    dec = builder.evaluate_candidate(cand_bad_lang, language="fr")
    assert "candidate language is unsupported" in dec.reasons

    # 2. _require_eligible
    eligible = CorpusBuilder._require_eligible(cand, language="en")
    assert eligible.chunk_version_id == cand.chunk_version_id
    with pytest.raises(CorpusRejectedError):
        CorpusBuilder._require_eligible(cand_bad_lang, language="en")

    # 3. FrozenCorpusPackage export
    manifest = builder.build_manifest(
        corpus_code="MATH_G4",
        version_number=1,
        scope={"grade": 4},
        language="en",
        embedding_model="emb",
        embedding_version="v1",
        candidates=[cand],
        activation_key="CAPS:g4:MATH:en:global",
    )
    pkg = FrozenCorpusPackage(manifest=manifest, candidates=(cand,), freeze_sha256="f" * 64)
    exported = pkg.export()
    assert exported["freeze_sha256"] == "f" * 64
    assert len(exported["candidates"]) == 1

    # 4. RetrievalProjectionBuilder errors and build
    proj_builder = RetrievalProjectionBuilder()

    with pytest.raises(CorpusRejectedError, match="binding_epoch must be positive"):
        proj_builder.build_projection(
            corpus_version_id="corp_1",
            activation_key="CAPS:g4:MATH:en:global",
            binding_epoch=0,
            manifest=manifest,
            candidates=[cand],
        )

    with pytest.raises(CorpusRejectedError, match="manifest activation_key does not match"):
        proj_builder.build_projection(
            corpus_version_id="corp_1",
            activation_key="CAPS:g5:MATH:en:global",
            binding_epoch=1,
            manifest=manifest,
            candidates=[cand],
        )

    cand_other = _make_candidate(chunk_version_id="chk_other")
    with pytest.raises(CorpusRejectedError, match="projection candidates must match manifest chunk membership"):
        proj_builder.build_projection(
            corpus_version_id="corp_1",
            activation_key="CAPS:g4:MATH:en:global",
            binding_epoch=1,
            manifest=manifest,
            candidates=[cand_other],
        )

    proj = proj_builder.build_projection(
        corpus_version_id="corp_1",
        activation_key="CAPS:g4:MATH:en:global",
        binding_epoch=1,
        manifest=manifest,
        candidates=[cand],
    )
    proj_exp = proj.export()
    assert proj_exp["corpus_version_id"] == "corp_1"
    assert len(proj_exp["records"]) == 1

    # 5. ActiveCorpusRetriever
    binding = ActiveCorpusBinding(
        activation_key="CAPS:g4:MATH:en:global",
        corpus_version_id="corp_1",
        binding_epoch=1,
        manifest_sha256=manifest.manifest_sha256,
        status="active",
    )

    inactive_binding = ActiveCorpusBinding(
        activation_key="CAPS:g4:MATH:en:global",
        corpus_version_id="corp_1",
        binding_epoch=1,
        manifest_sha256=manifest.manifest_sha256,
        status="inactive",
    )
    with pytest.raises(CorpusRejectedError, match="binding is not active"):
        ActiveCorpusRetriever(proj, inactive_binding)

    wrong_key_proj = RetrievalProjection(
        corpus_version_id="corp_1",
        activation_key="CAPS:g5:MATH:en:global",
        binding_epoch=1,
        manifest_sha256=manifest.manifest_sha256,
        retrieval_policy_version="v1",
        records=proj.records,
        projection_sha256="p" * 64,
    )
    with pytest.raises(CorpusRejectedError, match="projection activation_key does not match"):
        ActiveCorpusRetriever(wrong_key_proj, binding)

    wrong_epoch_proj = RetrievalProjection(
        corpus_version_id="corp_1",
        activation_key="CAPS:g4:MATH:en:global",
        binding_epoch=2,
        manifest_sha256=manifest.manifest_sha256,
        retrieval_policy_version="v1",
        records=proj.records,
        projection_sha256="p" * 64,
    )
    with pytest.raises(CorpusRejectedError, match="projection binding_epoch does not match"):
        ActiveCorpusRetriever(wrong_epoch_proj, binding)

    wrong_sha_proj = RetrievalProjection(
        corpus_version_id="corp_1",
        activation_key="CAPS:g4:MATH:en:global",
        binding_epoch=1,
        manifest_sha256="m" * 64,
        retrieval_policy_version="v1",
        records=proj.records,
        projection_sha256="p" * 64,
    )
    with pytest.raises(CorpusRejectedError, match="projection manifest_sha256 does not match"):
        ActiveCorpusRetriever(wrong_sha_proj, binding)

    retriever = ActiveCorpusRetriever(proj, binding)

    def _make_q(**kwargs) -> RetrievalQuery:
        d = {
            "activation_key": "CAPS:g4:MATH:en:global",
            "corpus_version_id": "corp_1",
            "binding_epoch": 1,
            "query_text": "mathematics",
            "language": "en",
            "top_k": 5,
        }
        d.update(kwargs)
        return RetrievalQuery(**d)

    with pytest.raises(CorpusRejectedError, match="query activation_key does not match"):
        retriever.search(_make_q(activation_key="CAPS:g5:MATH:en:global"))

    with pytest.raises(CorpusRejectedError, match="query corpus_version_id does not match"):
        retriever.search(_make_q(corpus_version_id="other_corp"))

    with pytest.raises(CorpusRejectedError, match="query binding_epoch is stale"):
        retriever.search(_make_q(binding_epoch=99))

    with pytest.raises(CorpusRejectedError, match="query language is unsupported"):
        retriever.search(_make_q(language="fr"))

    with pytest.raises(CorpusRejectedError, match="top_k must be positive"):
        retriever.search(_make_q(top_k=0))

    with pytest.raises(CorpusRejectedError, match="query_text must contain searchable terms"):
        retriever.search(_make_q(query_text="   "))

    res = retriever.search(_make_q(query_text="mathematics"))
    assert len(res.hits) == 1
    assert res.hits[0].score > 0
    res_exp = res.export()
    assert len(res_exp["hits"]) == 1

    # 6. CorpusActivationPlanner
    with pytest.raises(CorpusRejectedError, match="unsupported corpus activation event type"):
        CorpusActivationPlanner.plan_activation(
            activation_key="CAPS:g4:MATH:en:global",
            corpus_version_id="corp_1",
            previous_corpus_version_id=None,
            current_epoch=1,
            event_type="invalid_event",
        )

    with pytest.raises(CorpusRejectedError, match="binding epoch must be positive"):
        CorpusActivationPlanner.plan_activation(
            activation_key="CAPS:g4:MATH:en:global",
            corpus_version_id="corp_1",
            previous_corpus_version_id=None,
            current_epoch=-1,
        )

    with pytest.raises(CorpusRejectedError, match="rollback requires previous_corpus_version_id"):
        CorpusActivationPlanner.plan_activation(
            activation_key="CAPS:g4:MATH:en:global",
            corpus_version_id="corp_1",
            previous_corpus_version_id=None,
            current_epoch=1,
            event_type="rollback",
        )

    plan = CorpusActivationPlanner.plan_activation(
        activation_key="CAPS:g4:MATH:en:global",
        corpus_version_id="corp_2",
        previous_corpus_version_id="corp_1",
        current_epoch=1,
        event_type="rollback",
    )
    assert plan.binding_epoch == 2
    assert len(plan.outbox_events) == 3

    # 7. versioned_cache_key
    with pytest.raises(CorpusRejectedError, match="binding_epoch must be positive"):
        versioned_cache_key(activation_key="key", corpus_version_id="corp_1", binding_epoch=0)
    assert "epoch:1" in versioned_cache_key(activation_key="key", corpus_version_id="corp_1", binding_epoch=1)


