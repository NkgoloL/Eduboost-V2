"""Comprehensive unit test suite for Curriculum and LLM services (Batch 417).

Covers:
- app/services/curriculum/phase02r_closure.py
- app/services/curriculum/grounding.py
- app/services/curriculum/legacy.py
- app/services/curriculum/legacy_migration.py
- app/services/curriculum/claim_validation.py
- app/services/curriculum/retrieval.py
- app/services/curriculum/answer_verification.py
- app/services/llm/json_completion.py
- app/services/llm/gateway.py
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# 1. app/services/curriculum/phase02r_closure.py
# ---------------------------------------------------------------------------
from app.services.curriculum.phase02r_closure import (
    CLOSURE_POLICY_VERSION,
    REQUIRED_PREVIOUS_GATES,
    EvidenceReference,
    Gate2R8ClosureReadiness,
    Phase02RClosureRejectedError,
    build_gate2r8_audit_bundle,
    collect_previous_gate_references,
    evaluate_closure_readiness,
    file_sha256,
)


def test_evidence_reference_and_readiness_dataclasses(tmp_path: Path):
    ref = EvidenceReference(
        gate="2R.1",
        evidence_index_path="docs/evidence.md",
        approval_manifest_path="docs/approval.json",
        evidence_index_sha256="deadbeef",
        approval_decision="approved_with_disclosed_self_review_exception",
        authorised_next_gate="2R.2",
    )
    d = ref.as_dict()
    assert d["gate"] == "2R.1"
    assert d["evidence_index_sha256"] == "deadbeef"

    readiness = Gate2R8ClosureReadiness(
        policy_version=CLOSURE_POLICY_VERSION,
        status="ready_for_candidate_closure_evidence",
        evidence_references=(ref,),
        evaluation_status="passed",
        legacy_migration_status="ready_for_review",
        failure_reasons=(),
    )
    rd = readiness.as_dict()
    assert rd["status"] == "ready_for_candidate_closure_evidence"
    assert len(rd["evidence_references"]) == 1
    assert rd["failure_reasons"] == []

    # file_sha256 test
    dummy_file = tmp_path / "sample.txt"
    dummy_file.write_text("hello world", encoding="utf-8")
    sha = file_sha256(dummy_file)
    assert len(sha) == 64


def test_phase02r_closure_with_repo_root():
    repo_root = Path(__file__).resolve().parents[3]
    refs = collect_previous_gate_references(repo_root)
    assert len(refs) == len(REQUIRED_PREVIOUS_GATES)

    readiness = evaluate_closure_readiness(repo_root)
    assert isinstance(readiness, Gate2R8ClosureReadiness)
    assert readiness.policy_version == CLOSURE_POLICY_VERSION

    bundle = build_gate2r8_audit_bundle(repo_root)
    assert bundle["gate"] == "2R.8"
    assert "audit_bundle_sha256" in bundle
    assert bundle["evidence_reference_count"] == len(REQUIRED_PREVIOUS_GATES)


def test_phase02r_closure_failure_branches(tmp_path: Path):
    # In an empty tmp_path, evidence indices and approvals are missing
    readiness = evaluate_closure_readiness(tmp_path)
    assert readiness.status == "blocked"
    assert any("missing evidence index" in r for r in readiness.failure_reasons)
    assert any("missing approved manifest" in r for r in readiness.failure_reasons)

    # Test error class instantiation
    err = Phase02RClosureRejectedError("closure rejected")
    assert str(err) == "closure rejected"

    # Test when eval_report or legacy_manifest status is not passed/ready
    with patch(
        "app.services.curriculum.phase02r_closure.build_gate2r8_evaluation_report",
        return_value={"status": "failed", "report_sha256": "123"},
    ), patch(
        "app.services.curriculum.phase02r_closure.build_gate2r8_legacy_migration_manifest",
        return_value={"status": "draft", "manifest_sha256": "456"},
    ):
        r = evaluate_closure_readiness(tmp_path)
        assert "Gate 2R.8 evaluation report did not pass" in r.failure_reasons
        assert "Gate 2R.8 legacy migration manifest is not review-ready" in r.failure_reasons


# ---------------------------------------------------------------------------
# 2. app/services/curriculum/grounding.py
# ---------------------------------------------------------------------------
from app.services.curriculum.grounding import (
    GroundingDecision,
    GroundingPolicyEngine,
    GroundingRejectedError,
    RetrievedChunk,
    require_grounded_or_safe_fallback,
)


def test_grounding_policy_engine_validation_branches():
    engine = GroundingPolicyEngine()

    # 1. missing corpus_version_id, objectives, chunks
    dec = engine.validate_generation_grounding(
        corpus_version_id=None,
        requested_objective_ids=[],
        retrieved_chunks=[],
    )
    assert not dec.passed
    assert "active_corpus_version_missing" in dec.failure_reasons
    assert "requested_objectives_missing" in dec.failure_reasons
    assert "retrieved_chunks_missing" in dec.failure_reasons

    # 2. retrieved chunks missing tier_1, mixed corpus, bad rights, bad review, missing objective
    c1 = RetrievedChunk(
        chunk_version_id="c1",
        source_version_id="s1",
        mapping_version_ids=["m1"],
        objective_ids=["obj-1"],
        authority_tier="tier_2",  # not tier_1
        rights_status="rejected",  # not approved
        review_status="draft",  # not approved
        corpus_version_id="corp-other",  # mismatch
        score=0.9,
        language="en",
        text="text 1",
    )
    dec2 = engine.validate_generation_grounding(
        corpus_version_id="corp-1",
        requested_objective_ids=["obj-1", "obj-2"],
        retrieved_chunks=[c1],
    )
    assert not dec2.passed
    assert "tier_1_grounding_missing" in dec2.failure_reasons
    assert "mixed_corpus_version" in dec2.failure_reasons
    assert "rights_not_approved" in dec2.failure_reasons
    assert "chunk_not_approved" in dec2.failure_reasons
    assert "objective_coverage_incomplete:obj-2" in dec2.failure_reasons

    # 3. Successful grounding with tier_1 and approved statuses
    c_ok1 = RetrievedChunk(
        chunk_version_id="c1",
        source_version_id="s1",
        mapping_version_ids=["m1"],
        objective_ids=["obj-1"],
        authority_tier="tier_1",
        rights_status="approved",
        review_status="approved",
        corpus_version_id="corp-1",
        score=0.95,
        language="en",
        text="valid text 1",
    )
    c_ok2 = RetrievedChunk(
        chunk_version_id="c2",
        source_version_id="s2",
        mapping_version_ids=["m2"],
        objective_ids=["obj-2"],
        authority_tier="tier_1",
        rights_status="approved_with_conditions",
        review_status="approved",
        corpus_version_id="corp-1",
        score=0.91,
        language="en",
        text="valid text 2",
    )
    dec_pass = engine.validate_generation_grounding(
        corpus_version_id="corp-1",
        requested_objective_ids=["obj-1", "obj-2"],
        retrieved_chunks=[c_ok1, c_ok2],
    )
    assert dec_pass.passed
    assert dec_pass.status == "passed"
    assert dec_pass.source_snapshot_hash is not None
    assert dec_pass.chunk_version_ids == ["c1", "c2"]
    assert dec_pass.source_version_ids == ["s1", "s2"]
    assert dec_pass.mapping_version_ids == ["m1", "m2"]


def test_require_grounded_or_safe_fallback():
    pass_decision = GroundingDecision(True, "passed", "hash123")
    fail_decision = GroundingDecision(False, "failed", None, failure_reasons=["some reason"])

    # Passed does not raise
    require_grounded_or_safe_fallback(pass_decision)

    # Failed with fallback reason does not raise
    require_grounded_or_safe_fallback(fail_decision, fallback_reason="offline cached lesson")

    # Failed without fallback reason raises GroundingRejectedError
    with pytest.raises(GroundingRejectedError, match="curriculum response requires grounding"):
        require_grounded_or_safe_fallback(fail_decision)


# ---------------------------------------------------------------------------
# 3. app/services/curriculum/legacy.py
# ---------------------------------------------------------------------------
from app.services.curriculum.legacy import (
    LegacyArtifactView as LegacyViewOld,
    LegacyDispositionDecision as LegacyDecOld,
    LegacyDispositionError as LegacyErrOld,
    LegacyMigrationClassifier as LegacyClassifierOld,
)


def test_legacy_disposition_classifier_old():
    classifier = LegacyClassifierOld()

    # 1. Synthetic fixture
    art_synth = LegacyViewOld(
        artifact_id="art-synth",
        artifact_type="lesson",
        published=False,
        source_snapshot_hash="hash",
        source_chunk_ids=["chunk1"],
        synthetic_fixture=True,
    )
    dec_synth = classifier.classify(art_synth)
    assert dec_synth.disposition == "synthetic_fixture"
    assert not dec_synth.learner_serving_allowed

    # 2. Grounded and verified
    art_gv = LegacyViewOld(
        artifact_id="art-gv",
        artifact_type="lesson",
        published=True,
        source_snapshot_hash="hash",
        source_chunk_ids=["chunk1"],
        answer_key_verified=True,
    )
    dec_gv = classifier.classify(art_gv)
    assert dec_gv.disposition == "grounded_verified"
    assert dec_gv.learner_serving_allowed

    # 3. Grounded unverified (e.g. diagnostic_item where answer_key_verified is not True)
    art_gu = LegacyViewOld(
        artifact_id="art-gu",
        artifact_type="diagnostic_item",
        published=True,
        source_snapshot_hash="hash",
        source_chunk_ids=["chunk1"],
        answer_key_verified=False,
    )
    dec_gu = classifier.classify(art_gu)
    assert dec_gu.disposition == "grounded_unverified"
    assert not dec_gu.learner_serving_allowed

    # 4. Published without grounding
    art_pub = LegacyViewOld(
        artifact_id="art-pub",
        artifact_type="lesson",
        published=True,
        source_snapshot_hash=None,
        source_chunk_ids=[],
    )
    dec_pub = classifier.classify(art_pub)
    assert dec_pub.disposition == "published_requires_review"

    # 5. Unpublished without grounding
    art_unpub = LegacyViewOld(
        artifact_id="art-unpub",
        artifact_type="lesson",
        published=False,
        source_snapshot_hash=None,
        source_chunk_ids=[],
    )
    dec_unpub = classifier.classify(art_unpub)
    assert dec_unpub.disposition == "legacy_ungrounded"

    # Summary
    summary = classifier.summarize([art_synth, art_gv, art_gu, art_pub, art_unpub])
    assert summary["synthetic_fixture"] == 1
    assert summary["grounded_verified"] == 1
    assert summary["grounded_unverified"] == 1
    assert summary["published_requires_review"] == 1
    assert summary["legacy_ungrounded"] == 1

    # LegacyDispositionError instantiation
    err = LegacyErrOld("err")
    assert str(err) == "err"


# ---------------------------------------------------------------------------
# 4. app/services/curriculum/legacy_migration.py
# ---------------------------------------------------------------------------
from app.services.curriculum.legacy_migration import (
    ALLOWED_DISPOSITIONS,
    LEGACY_MIGRATION_POLICY_VERSION,
    LegacyArtifactView as LegacyViewMigration,
    LegacyDispositionDecision as LegacyDecMigration,
    LegacyDispositionError as LegacyErrMigration,
    LegacyMigrationClassifier as LegacyClassifierMigration,
    build_gate2r8_legacy_fixture_artifacts,
    build_gate2r8_legacy_migration_manifest,
    sha256_json,
)


def test_legacy_migration_dataclasses_and_normalization():
    # Error when artifact_id or artifact_type is empty
    with pytest.raises(LegacyErrMigration, match="artifact_id and artifact_type are required"):
        LegacyViewMigration(artifact_id="", artifact_type="lesson", published=True, source_snapshot_hash=None).normalized()

    with pytest.raises(LegacyErrMigration, match="artifact_id and artifact_type are required"):
        LegacyViewMigration(artifact_id="art-1", artifact_type="", published=True, source_snapshot_hash=None).normalized()

    valid_view = LegacyViewMigration(
        artifact_id="  art-1  ",
        artifact_type="  lesson  ",
        published=True,
        source_snapshot_hash="hash-1",
        source_chunk_ids=("c1",),
    )
    norm = valid_view.normalized()
    assert norm.artifact_id == "art-1"
    assert norm.artifact_type == "lesson"

    dec = LegacyDecMigration("art-1", "lesson", "grounded_verified", True, False, "ok")
    assert dec.as_dict()["artifact_id"] == "art-1"

    # sha256_json test
    assert len(sha256_json({"key": "value"})) == 64


def test_legacy_migration_classifier():
    classifier = LegacyClassifierMigration()

    # 1. Synthetic fixture
    synth = LegacyViewMigration("art-synth", "lesson", published=False, source_snapshot_hash=None, synthetic_fixture=True)
    d_synth = classifier.classify(synth)
    assert d_synth.disposition == "synthetic_fixture_excluded"
    assert not d_synth.learner_serving_allowed
    assert not d_synth.requires_human_review

    # 2. Grounded and verified with valid tags
    gv = LegacyViewMigration(
        "art-gv",
        "lesson",
        published=True,
        source_snapshot_hash="snap-1",
        source_chunk_ids=("c1",),
        generation_policy_version="phase02r-gate2r6-generation-v1",
        tutor_grounding_trace_id="tutor-trace-abc",
    )
    d_gv = classifier.classify(gv)
    assert d_gv.disposition == "grounded_verified"
    assert d_gv.learner_serving_allowed
    assert not d_gv.requires_human_review

    # 3. Grounded but answer unverified for assessment_item
    gu_assess = LegacyViewMigration(
        "art-gu",
        "assessment_item",
        published=True,
        source_snapshot_hash="snap-1",
        source_chunk_ids=("c1",),
        answer_key_verified=False,
    )
    d_gu = classifier.classify(gu_assess)
    assert d_gu.disposition == "quarantine_requires_review"
    assert d_gu.requires_human_review

    # 4. Unpublished without grounding
    unpub = LegacyViewMigration("art-unpub", "lesson", published=False, source_snapshot_hash=None)
    d_unpub = classifier.classify(unpub)
    assert d_unpub.disposition == "retire_legacy_ungrounded"
    assert not d_unpub.learner_serving_allowed

    # 5. Build manifest error on empty artifacts
    with pytest.raises(LegacyErrMigration, match="legacy migration manifest requires at least one artifact"):
        classifier.build_manifest([])

    # 6. Unknown disposition error branch
    with patch.object(
        classifier,
        "classify",
        return_value=LegacyDecMigration("art-bad", "lesson", "unknown_disposition", False, False, "bad"),
    ):
        with pytest.raises(LegacyErrMigration, match="unknown disposition emitted"):
            classifier.build_manifest([synth])

    # 7. Default fixtures and manifest builder
    fixtures = build_gate2r8_legacy_fixture_artifacts()
    assert len(fixtures) == 5
    manifest = build_gate2r8_legacy_migration_manifest()
    assert manifest["gate"] == "2R.8"
    assert manifest["policy_version"] == LEGACY_MIGRATION_POLICY_VERSION
    assert manifest["status"] == "ready_for_review"
    assert manifest["artifact_count"] == 5
    assert "manifest_sha256" in manifest


# ---------------------------------------------------------------------------
# 5. app/services/curriculum/claim_validation.py
# ---------------------------------------------------------------------------
from app.services.curriculum.claim_validation import (
    Claim,
    ClaimValidationError,
    ClaimValidationOutcome,
    ClaimValidator,
)


def test_claim_validator():
    validator = ClaimValidator(maximum_overlap_ratio=0.35)

    # 1. Valid claims
    claims = [
        Claim(claim_type="pedagogical_guidance", text="Guidance text"),
        Claim(claim_type="mathematical_fact", text="2 + 2 = 4"),
        Claim(claim_type="curriculum_requirement", text="CAPS Math requirement", supporting_chunk_ids=["chk-1"]),
        Claim(claim_type="enrichment", text="Optional extension"),
    ]
    outcome = validator.validate(claims)
    assert outcome.status == "passed"
    assert outcome.errors == []

    # 2. Errors on invalid claims
    bad_claims = [
        Claim(claim_type="unsupported_type", text="bad"),
        Claim(claim_type="assessment_claim", text="missing chunks", supporting_chunk_ids=[]),
        Claim(claim_type="mathematical_fact", text="high overlap", overlap_ratio=0.5),
        Claim(claim_type="enrichment", text="CAPS requires topic A"),
    ]
    outcome_bad = validator.validate(bad_claims)
    assert outcome_bad.status == "failed"
    assert len(outcome_bad.errors) == 4
    assert any("unsupported claim_type" in e for e in outcome_bad.errors)
    assert any("requires supporting source chunks" in e for e in outcome_bad.errors)
    assert any("exceeds permitted textual overlap" in e for e in outcome_bad.errors)
    assert any("enrichment cannot be promoted" in e for e in outcome_bad.errors)

    # ClaimValidationError instantiation
    err = ClaimValidationError("claim error")
    assert str(err) == "claim error"


# ---------------------------------------------------------------------------
# 6. app/services/curriculum/retrieval.py
# ---------------------------------------------------------------------------
import app.services.curriculum.retrieval as curriculum_retrieval


def test_curriculum_retrieval_facade():
    assert hasattr(curriculum_retrieval, "ActiveCorpusBinding")
    assert hasattr(curriculum_retrieval, "ActiveCorpusRetriever")
    assert hasattr(curriculum_retrieval, "CorpusRetrievalRecord")
    assert hasattr(curriculum_retrieval, "RetrievalHit")
    assert hasattr(curriculum_retrieval, "RetrievalProjection")
    assert hasattr(curriculum_retrieval, "RetrievalProjectionBuilder")
    assert hasattr(curriculum_retrieval, "RetrievalQuery")
    assert hasattr(curriculum_retrieval, "RetrievalResult")


# ---------------------------------------------------------------------------
# 7. app/services/curriculum/answer_verification.py
# ---------------------------------------------------------------------------
from app.services.curriculum.answer_verification import (
    AnswerVerificationError,
    AnswerVerificationOutcome,
    DeterministicMathAnswerVerifier,
)


def test_deterministic_math_answer_verifier():
    verifier = DeterministicMathAnswerVerifier()

    # Successful arithmetic tests
    res_add = verifier.verify_arithmetic_expression(question_expression="2 + 3", proposed_answer="5")
    assert res_add.status == "passed"
    assert res_add.expected_answer == "5"

    res_sub = verifier.verify_arithmetic_expression(question_expression="10 - 4", proposed_answer="6")
    assert res_sub.status == "passed"

    res_mul = verifier.verify_arithmetic_expression(question_expression="3 * 4", proposed_answer="12")
    assert res_mul.status == "passed"

    res_div_float = verifier.verify_arithmetic_expression(question_expression="5 / 2", proposed_answer="2.5")
    assert res_div_float.status == "passed"

    res_floordiv = verifier.verify_arithmetic_expression(question_expression="7 // 2", proposed_answer="3")
    assert res_floordiv.status == "passed"

    res_mod = verifier.verify_arithmetic_expression(question_expression="10 % 3", proposed_answer="1")
    assert res_mod.status == "passed"

    res_neg = verifier.verify_arithmetic_expression(question_expression="-5 + 2", proposed_answer="-3")
    assert res_neg.status == "passed"

    # Mismatched answer
    res_fail = verifier.verify_arithmetic_expression(question_expression="2 + 2", proposed_answer="5")
    assert res_fail.status == "failed"
    assert res_fail.expected_answer == "4"
    assert res_fail.observed_answer == "5"

    # Unsupported expressions
    with pytest.raises(AnswerVerificationError, match="unsupported arithmetic expression"):
        verifier.verify_arithmetic_expression(question_expression="pow(2, 3)", proposed_answer="8")

    with pytest.raises(AnswerVerificationError, match="unsupported arithmetic expression"):
        verifier.verify_arithmetic_expression(question_expression="x + 1", proposed_answer="2")

    # Syntax error in question
    with pytest.raises(SyntaxError):
        verifier.verify_arithmetic_expression(question_expression="2 +++ ", proposed_answer="2")


# ---------------------------------------------------------------------------
# 8. app/services/llm/json_completion.py
# ---------------------------------------------------------------------------
from app.services.llm.json_completion import (
    JsonCompletionError,
    JsonCompletionGateway,
    JsonCompletionResponse,
    parse_json_response,
)


def test_parse_json_response():
    # Normal JSON
    assert parse_json_response('{"test": 123}') == {"test": 123}

    # Markdown wrapped JSON
    assert parse_json_response('```json\n{"test": "abc"}\n```') == {"test": "abc"}
    assert parse_json_response('```\n{"test": 456}\n```') == {"test": 456}

    # Invalid JSON
    with pytest.raises(JsonCompletionError, match="LLM response is not valid JSON"):
        parse_json_response("not a json string")


@pytest.mark.asyncio
async def test_json_completion_mock_provider():
    gateway = JsonCompletionGateway()

    with patch("app.core.config.settings.LLM_PROVIDER", "mock"):
        resp = await gateway.complete(prompt="Tell me about fractions")
        assert resp.provider == "mock"
        assert resp.content == "{}"

        resp_ans = await gateway.complete(prompt="Provide correct_answer for question")
        assert resp_ans.provider == "mock"
        data = json.loads(resp_ans.content)
        assert data["correct_answer"] == "A"

        parsed = await gateway.complete_json(prompt="Provide correct_answer for question")
        assert parsed["correct_answer"] == "A"


@pytest.mark.asyncio
async def test_json_completion_google_provider():
    gateway = JsonCompletionGateway()

    # No API key
    with patch("app.core.config.settings.LLM_PROVIDER", "google"), patch(
        "app.core.config.settings.GOOGLE_API_KEY", ""
    ):
        with pytest.raises(JsonCompletionError, match="Google Gemini API key not configured"):
            await gateway.complete(prompt="test")

    # Successful call
    mock_payload = {
        "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5},
        "candidates": [{"content": {"parts": [{"text": '{"result": "success"}'}]}}],
    }
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value=mock_payload)

    with patch("app.core.config.settings.LLM_PROVIDER", "google"), patch(
        "app.core.config.settings.GOOGLE_API_KEY", "fake-key"
    ), patch("app.core.config.settings.GOOGLE_MODEL", "models/gemini-pro"), patch(
        "httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp
    ):
        res = await gateway.complete(prompt="test prompt")
        assert res.provider == "google"
        assert res.prompt_tokens == 10
        assert res.completion_tokens == 5
        assert res.content == '{"result": "success"}'

    # Google returned no candidates
    mock_resp_no_cand = MagicMock()
    mock_resp_no_cand.raise_for_status = MagicMock()
    mock_resp_no_cand.json = MagicMock(return_value={"candidates": []})
    with patch("app.core.config.settings.LLM_PROVIDER", "google"), patch(
        "app.core.config.settings.GOOGLE_API_KEY", "fake-key"
    ), patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp_no_cand):
        with pytest.raises(JsonCompletionError, match="Google Gemini returned no candidates"):
            await gateway.complete(prompt="test prompt")

    # Google returned empty text
    mock_resp_empty = MagicMock()
    mock_resp_empty.raise_for_status = MagicMock()
    mock_resp_empty.json = MagicMock(return_value={"candidates": [{"content": {"parts": [{"text": ""}]}}]})
    with patch("app.core.config.settings.LLM_PROVIDER", "google"), patch(
        "app.core.config.settings.GOOGLE_API_KEY", "fake-key"
    ), patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp_empty):
        with pytest.raises(JsonCompletionError, match="Google Gemini returned an empty response"):
            await gateway.complete(prompt="test prompt")


@pytest.mark.asyncio
async def test_json_completion_groq_and_anthropic_providers():
    gateway = JsonCompletionGateway()

    # Groq no API key
    with patch("app.core.config.settings.LLM_PROVIDER", "groq"), patch(
        "app.core.config.settings.GROQ_API_KEY", ""
    ):
        with pytest.raises(JsonCompletionError, match="Groq API key not configured"):
            await gateway.complete(prompt="test")

    # Groq success
    mock_groq_completion = MagicMock()
    mock_groq_completion.choices = [MagicMock(message=MagicMock(content='{"groq": true}'))]
    mock_groq_completion.usage = MagicMock(prompt_tokens=15, completion_tokens=7)
    with patch("app.core.config.settings.LLM_PROVIDER", "groq"), patch(
        "app.core.config.settings.GROQ_API_KEY", "fake-groq-key"
    ), patch("groq.AsyncGroq.chat") as mock_chat:
        mock_chat.completions.create = AsyncMock(return_value=mock_groq_completion)
        res_groq = await gateway.complete(prompt="groq test")
        assert res_groq.provider == "groq"
        assert res_groq.prompt_tokens == 15
        assert res_groq.content == '{"groq": true}'

    # Anthropic no API key
    with patch("app.core.config.settings.LLM_PROVIDER", "anthropic"), patch(
        "app.core.config.settings.ANTHROPIC_API_KEY", ""
    ):
        with pytest.raises(JsonCompletionError, match="Anthropic API key not configured"):
            await gateway.complete(prompt="test")

    # Anthropic success
    mock_ant_msg = MagicMock()
    mock_ant_block = MagicMock()
    mock_ant_block.text = '{"anthropic": true}'
    mock_ant_msg.content = [mock_ant_block]
    mock_ant_msg.usage = MagicMock(input_tokens=22, output_tokens=9)
    with patch("app.core.config.settings.LLM_PROVIDER", "anthropic"), patch(
        "app.core.config.settings.ANTHROPIC_API_KEY", "fake-ant-key"
    ), patch("anthropic.AsyncAnthropic.messages") as mock_messages:
        mock_messages.create = AsyncMock(return_value=mock_ant_msg)
        res_ant = await gateway.complete(prompt="ant test")
        assert res_ant.provider == "anthropic"
        assert res_ant.prompt_tokens == 22
        assert res_ant.content == '{"anthropic": true}'


@pytest.mark.asyncio
async def test_json_completion_fallback_chain():
    gateway = JsonCompletionGateway()

    # Provider is None or "auto", no keys configured
    with patch("app.core.config.settings.LLM_PROVIDER", "auto"), patch(
        "app.core.config.settings.GOOGLE_API_KEY", ""
    ), patch("app.core.config.settings.GROQ_API_KEY", ""), patch(
        "app.core.config.settings.ANTHROPIC_API_KEY", ""
    ):
        with pytest.raises(JsonCompletionError, match="No JSON LLM provider succeeded"):
            await gateway.complete(prompt="test")

    # Fallback chain with GOOGLE_API_KEY succeeding
    with patch("app.core.config.settings.LLM_PROVIDER", "auto"), patch(
        "app.core.config.settings.GOOGLE_API_KEY", "fake-key"
    ), patch.object(
        gateway, "_call_google", new_callable=AsyncMock, return_value=JsonCompletionResponse("{}", "google", "gemini")
    ):
        resp_google = await gateway.complete(prompt="test")
        assert resp_google.provider == "google"

    # Fallback chain with GOOGLE failing and GROQ succeeding
    with patch("app.core.config.settings.LLM_PROVIDER", "auto"), patch(
        "app.core.config.settings.GOOGLE_API_KEY", "fake-key"
    ), patch("app.core.config.settings.GROQ_API_KEY", "fake-groq"), patch.object(
        gateway, "_call_google", new_callable=AsyncMock, side_effect=Exception("google down")
    ), patch.object(
        gateway, "_call_groq", new_callable=AsyncMock, return_value=JsonCompletionResponse("{}", "groq", "llama")
    ):
        resp_groq = await gateway.complete(prompt="test")
        assert resp_groq.provider == "groq"

    # Fallback chain with GOOGLE & GROQ failing and ANTHROPIC succeeding
    with patch("app.core.config.settings.LLM_PROVIDER", "auto"), patch(
        "app.core.config.settings.GOOGLE_API_KEY", "fake-key"
    ), patch("app.core.config.settings.GROQ_API_KEY", "fake-groq"), patch(
        "app.core.config.settings.ANTHROPIC_API_KEY", "fake-ant"
    ), patch.object(
        gateway, "_call_google", new_callable=AsyncMock, side_effect=Exception("google down")
    ), patch.object(
        gateway, "_call_groq", new_callable=AsyncMock, side_effect=Exception("groq down")
    ), patch.object(
        gateway, "_call_anthropic", new_callable=AsyncMock, return_value=JsonCompletionResponse("{}", "anthropic", "claude")
    ):
        resp_ant = await gateway.complete(prompt="test")
        assert resp_ant.provider == "anthropic"


# ---------------------------------------------------------------------------
# 9. app/services/llm/gateway.py
# ---------------------------------------------------------------------------
from app.services.llm.gateway import (
    DISABLE_LESSON_GENERATION_ENV,
    CanonicalLLMGateway,
    DeterministicMockProvider,
    LLMGatewayRequest,
    ProviderHealth,
    ProviderPolicy,
    ProviderResult,
    TokenUsage,
)


def test_llm_gateway_token_usage_and_mock_provider():
    tu = TokenUsage(prompt_tokens=5, completion_tokens=10)
    assert tu.total_tokens == 15

    mock_p = DeterministicMockProvider(content='{"data": 1}', healthy=True)
    h = mock_p.health()
    assert h.healthy
    assert h.provider_name == "deterministic_mock"

    req = LLMGatewayRequest(
        prompt="Hello lesson prompt",
        pseudonym_id="user-1",
        prompt_template_version="v1",
        input_schema="schema-in",
        output_schema="schema-out",
    )
    res = mock_p.complete(req, timeout_seconds=10.0)
    assert res.content == '{"data": 1}'
    assert res.token_usage.total_tokens > 0

    # Unhealthy provider complete raises RuntimeError
    unhealthy_p = DeterministicMockProvider(healthy=False)
    assert not unhealthy_p.health().healthy
    with pytest.raises(RuntimeError, match="deterministic provider unavailable"):
        unhealthy_p.complete(req, timeout_seconds=10.0)


def test_canonical_llm_gateway_execution_flows():
    req = LLMGatewayRequest(
        prompt="Explain place values",
        pseudonym_id="user-123",
        prompt_template_version="tpl-v1",
        input_schema="json-in",
        output_schema="json-out",
    )

    # 1. Lesson generation disabled via environment variable
    gateway = CanonicalLLMGateway(providers=[DeterministicMockProvider()])
    with patch.dict("os.environ", {DISABLE_LESSON_GENERATION_ENV: "1"}):
        with pytest.raises(RuntimeError, match="lesson generation disabled"):
            gateway.complete(req)

    # 2. Primary succeeds
    p1 = DeterministicMockProvider(content='{"lesson": 1}', healthy=True)
    gateway_single = CanonicalLLMGateway(providers=[p1])
    health_list = gateway_single.health_checks()
    assert len(health_list) == 1
    assert health_list[0].healthy

    resp = gateway_single.complete(req)
    assert resp.content == '{"lesson": 1}'
    assert resp.metadata.fallback_status == "primary"
    assert resp.metadata.circuit_breaker_status == "closed"
    assert resp.metadata.budget_status == "within_budget"

    # 3. Empty providers list -> falls back to development_fallback
    gateway_empty = CanonicalLLMGateway(providers=[])
    resp_empty = gateway_empty.complete(req)
    assert resp_empty.metadata.fallback_status == "development_fallback"

    # 4. Primary is unhealthy -> falls back to secondary provider
    p_bad = DeterministicMockProvider(healthy=False)
    p_good = DeterministicMockProvider(content='{"backup": true}', healthy=True)
    gateway_failover = CanonicalLLMGateway(providers=[p_bad, p_good])
    resp_failover = gateway_failover.complete(req)
    assert resp_failover.content == '{"backup": true}'
    assert resp_failover.metadata.fallback_status == "provider_fallback"

    # 5. Primary succeeds after retry -> recovered_after_retry
    call_count = 0

    class FlakyPrimaryProvider:
        provider_name = "flaky"
        model_version = "v1"

        def health(self) -> ProviderHealth:
            return ProviderHealth("flaky", True, "ok")

        def complete(self, request: LLMGatewayRequest, timeout_seconds: float) -> ProviderResult:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise TimeoutError("timeout on attempt 1")
            return ProviderResult(
                content='{"recovered": true}',
                provider_name=self.provider_name,
                model_version=self.model_version,
                token_usage=TokenUsage(1, 1),
            )

    gw_flaky = CanonicalLLMGateway(
        providers=[FlakyPrimaryProvider()],
        policy=ProviderPolicy(max_retries=2),
    )
    resp_recovered = gw_flaky.complete(req)
    assert resp_recovered.metadata.fallback_status == "recovered_after_retry"

    # 6. Primary fails with exception during complete() -> falls back to dev fallback
    class BrokenProvider:
        provider_name = "broken"
        model_version = "v0"

        def health(self) -> ProviderHealth:
            return ProviderHealth("broken", True, "ok")

        def complete(self, request: LLMGatewayRequest, timeout_seconds: float) -> ProviderResult:
            raise ValueError("connection timeout")

    gateway_broken = CanonicalLLMGateway(
        providers=[BrokenProvider()],
        policy=ProviderPolicy(max_retries=1, daily_budget_tokens=2),
    )
    resp_dev = gateway_broken.complete(req)
    assert resp_dev.metadata.fallback_status == "development_fallback"
    assert resp_dev.metadata.circuit_breaker_status == "open"
    assert resp_dev.metadata.retry_count == 2


# ---------------------------------------------------------------------------
# 10. app/services/curriculum/evaluation.py edge cases
# ---------------------------------------------------------------------------
from app.services.curriculum.evaluation import (
    EvaluationRejectedError,
    Gate2R8EvaluationPolicy,
    RetrievalEvaluationCase,
    RetrievalEvaluationScorer,
)


def test_curriculum_evaluation_edge_cases():
    # 1. Normalized errors
    with pytest.raises(EvaluationRejectedError, match="case_id and query are required"):
        RetrievalEvaluationCase(case_id="", language="en", strand="math", term=1, query="q").normalized()

    with pytest.raises(EvaluationRejectedError, match="case_id and query are required"):
        RetrievalEvaluationCase(case_id="c1", language="en", strand="math", term=1, query="").normalized()

    with pytest.raises(EvaluationRejectedError, match="unsupported language"):
        RetrievalEvaluationCase(case_id="c1", language="fr", strand="math", term=1, query="q").normalized()

    with pytest.raises(EvaluationRejectedError, match="negative case c1 must not define expected chunks"):
        RetrievalEvaluationCase(
            case_id="c1", language="en", strand="math", term=1, query="q", is_negative_case=True, expected_chunk_ids=("chk",)
        ).normalized()

    with pytest.raises(EvaluationRejectedError, match="positive case c1 must define expected chunks"):
        RetrievalEvaluationCase(
            case_id="c1", language="en", strand="math", term=1, query="q", is_negative_case=False, expected_chunk_ids=()
        ).normalized()

    # 2. Scorer errors
    scorer = RetrievalEvaluationScorer()
    with pytest.raises(EvaluationRejectedError, match="evaluation dataset is empty"):
        scorer.score([])

    valid_case = RetrievalEvaluationCase(
        case_id="c1", language="en", strand="math", term=1, query="q", is_negative_case=False, expected_chunk_ids=("chk",)
    )
    with pytest.raises(EvaluationRejectedError, match="k must be positive"):
        scorer.score([valid_case], k=0)

    # Prohibited hit count error
    prohibited_case = RetrievalEvaluationCase(
        case_id="c1", language="en", strand="math", term=1, query="q", is_negative_case=False, expected_chunk_ids=("chk",),
        prohibited_hit_count=1,
    )
    with pytest.raises(EvaluationRejectedError, match="blocked, wrong-version, or wrong-language"):
        scorer.score([prohibited_case])

    # Negative case returning hits error
    neg_case_with_hits = RetrievalEvaluationCase(
        case_id="c_neg", language="en", strand="math", term=1, query="q", is_negative_case=True,
        retrieved_chunk_ids=("chk_wrong",),
    )
    with pytest.raises(EvaluationRejectedError, match="negative case c_neg returned authoritative hits"):
        scorer.score([neg_case_with_hits])

    # Positive count < MIN_POSITIVE_CASES error
    pos_cases = [
        RetrievalEvaluationCase(case_id=f"p{i}", language="en", strand="math", term=1, query=f"q{i}", is_negative_case=False, expected_chunk_ids=("chk",))
        for i in range(5)
    ]
    with pytest.raises(EvaluationRejectedError, match="requires at least 18 positive cases"):
        scorer.score(pos_cases)

    # Negative count < MIN_NEGATIVE_CASES error
    pos_cases_18 = [
        RetrievalEvaluationCase(case_id=f"p{i}", language="en", strand="math", term=1, query=f"q{i}", is_negative_case=False, expected_chunk_ids=("chk",), retrieved_chunk_ids=("chk",))
        for i in range(18)
    ]
    with pytest.raises(EvaluationRejectedError, match="requires at least 10 negative cases"):
        scorer.score(pos_cases_18)

    # 3. Policy failure branches (low recall, low precision, low mrr)
    policy = Gate2R8EvaluationPolicy()
    mock_metrics = MagicMock(recall_at_k=0.5, precision_at_k=0.5, mrr=0.5, as_dict=lambda: {})
    with patch.object(policy.scorer, "score", return_value=mock_metrics):
        eval_res = policy.evaluate([valid_case])
        assert eval_res.status == "failed"
        assert "recall_at_k below threshold" in eval_res.failure_reasons
        assert "precision_at_k below threshold" in eval_res.failure_reasons
        assert "mrr below threshold" in eval_res.failure_reasons

