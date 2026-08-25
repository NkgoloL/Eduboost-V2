from __future__ import annotations

import uuid

import pytest

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentArtifactType,
    ContentArtifactSource,
    ContentGenerationArtifact,
    ContentLayer,
)
from app.services.content_review_governance import ContentReviewEligibilityService
from app.services.content_review_governance import ReviewGovernancePolicy
from app.services.content_review_governance import _rubric_passed, _source_payload
from app.services.curriculum_expansion import (
    artifact_eligibility_reasons,
    build_training_record,
    dataset_sha256,
    forbidden_training_paths,
    obvious_pii_findings,
    record_sha256,
    validate_language_content,
)
from app.services.llm_provider import (
    AllProvidersFailedError,
    AnthropicProvider,
    AzureOpenAIProvider,
    DeterministicProvider,
    GenerationResult,
    GroqProvider,
    ProviderError,
    ProviderRouter,
    TokenUsage,
    _anthropic_cost,
    build_provider_router,
)


def _artifact(**overrides):
    data = {
        "artifact_id": uuid.uuid4(),
        "scope_id": "grade4_mathematics_en",
        "content_layer": ContentLayer.LESSONS,
        "artifact_type": ContentArtifactType.LESSON,
        "caps_ref": "4.M.1.1",
        "grade": 4,
        "subject_code": "MAT",
        "language": "en",
        "status": ContentArtifactStatus.PUBLISHED,
        "published_at": object(),
        "publication_eligible": True,
        "artifact_json": {
            "title": "Whole numbers",
            "summary": "CAPS aligned learner content.",
        },
        "artifact_hash": "a" * 64,
        "source_snapshot_hash": "s" * 64,
        "quality_score": 0.92,
        "caps_alignment_score": 0.91,
        "safety_status": "approved",
        "answer_key_verified": True,
    }
    data.update(overrides)
    artifact = ContentGenerationArtifact(**data)
    artifact.sources = [
        ContentArtifactSource(
            source_document_id="caps-grade4-maths",
            source_chunk_id="chunk-1",
            license_status="government_open",
            source_hash="h" * 64,
            source_role="primary_context",
            source_metadata={},
        )
    ]
    return artifact


def test_curriculum_training_record_hashes_are_stable_and_pii_safe() -> None:
    artifact = _artifact()

    record = build_training_record(artifact)
    first_hash = record_sha256(record)
    second_hash = record_sha256({**record})

    assert first_hash == second_hash
    assert dataset_sha256([first_hash, "b" * 64]) == dataset_sha256(["b" * 64, first_hash])
    assert forbidden_training_paths(record) == []
    assert obvious_pii_findings(record) == []
    assert validate_language_content(record["content"], "en") == []


def test_curriculum_training_eligibility_reports_privacy_quality_and_source_blockers() -> None:
    unsafe = _artifact(
        status=ContentArtifactStatus.PENDING_REVIEW,
        artifact_hash="",
        source_snapshot_hash="",
        quality_score=0.1,
        caps_alignment_score=0.2,
        safety_status="pending",
        artifact_json={
            "title": "TODO learner phone 071 234 5678",
            "learner_id": "learner-123",
            "email": "child@example.com",
        },
    )
    unsafe.sources = [
        ContentArtifactSource(
            source_document_id="caps-grade4-maths",
            source_chunk_id="chunk-2",
            license_status="unknown",
            source_hash="",
            source_role="primary_context",
            source_metadata={},
        )
    ]

    reasons = artifact_eligibility_reasons(
        unsafe,
        require_published=True,
        min_quality_score=0.8,
        min_caps_alignment_score=0.8,
    )

    assert "ineligible_lifecycle_state" in reasons
    assert "forbidden_operational_fields" in reasons
    assert "obvious_pii" in reasons
    assert "language_validation_failed" in reasons
    assert "disallowed_source_license" in reasons
    assert "missing_source_hash" in reasons


def test_content_review_eligibility_separates_retrieval_from_learner_delivery() -> None:
    promoted = _artifact(
        status=ContentArtifactStatus.PROMOTED_PRODUCTION,
        published_at=None,
    )
    published = _artifact(status=ContentArtifactStatus.PUBLISHED)
    pending = _artifact(
        status=ContentArtifactStatus.PENDING_REVIEW,
        publication_eligible=False,
        published_at=None,
    )

    assert ContentReviewEligibilityService.is_retrieval_eligible(promoted) is True
    assert ContentReviewEligibilityService.is_learner_eligible(promoted) is False
    assert ContentReviewEligibilityService.is_learner_eligible(published) is True

    with pytest.raises(ValueError, match="semantic retrieval"):
        ContentReviewEligibilityService.assert_retrieval_eligible(pending)
    with pytest.raises(ValueError, match="learner delivery"):
        ContentReviewEligibilityService.assert_learner_eligible(promoted)


class _FlakyProvider(DeterministicProvider):
    name = "flaky"

    def __init__(self, failures: int) -> None:
        super().__init__()
        self.failures = failures
        self.calls = 0

    async def generate(self, *, system: str, user: str, **kwargs):
        self.calls += 1
        if self.calls <= self.failures:
            raise ProviderError("temporary provider failure", self.name, retryable=True)
        return GenerationResult(
            text="safe fallback explanation",
            provider=self.name,
            model="fake",
            usage=TokenUsage(1, 2, 3, 0.0),
            latency_ms=1.0,
        )


class _UnexpectedProvider(DeterministicProvider):
    name = "unexpected"

    async def generate(self, *, system: str, user: str, **kwargs):
        raise RuntimeError("sdk exploded")


@pytest.mark.asyncio
async def test_llm_router_retries_retryable_provider_then_records_success() -> None:
    provider = _FlakyProvider(failures=1)
    router = ProviderRouter(
        [provider],
        max_retries_per_provider=2,
        request_timeout_seconds=1,
    )

    result = await router.generate(system="safe", user="learner question")

    assert provider.calls == 2
    assert result.text == "safe fallback explanation"
    assert router.provider_states() == {"flaky": "closed"}


@pytest.mark.asyncio
async def test_llm_router_normalizes_unexpected_provider_failures() -> None:
    router = ProviderRouter(
        [_UnexpectedProvider()],
        max_retries_per_provider=1,
        request_timeout_seconds=1,
    )

    with pytest.raises(AllProvidersFailedError) as excinfo:
        await router.generate(system="safe", user="learner question")

    assert "Unexpected unexpected failure" in str(excinfo.value)


def test_llm_factory_selects_azure_primary_then_explicit_provider() -> None:
    class Settings:
        ENVIRONMENT = "production"
        LLM_PROVIDER = ""
        AZURE_OPENAI_ENDPOINT = "https://example.openai.azure.com"
        AZURE_OPENAI_API_KEY = "azure-key"
        AZURE_OPENAI_MODEL = "gpt-4o"
        AZURE_OPENAI_API_VERSION = "2024-02-01"
        ANTHROPIC_API_KEY = ""
        GROQ_API_KEY = "groq-key"
        GROQ_MODEL = "llama3-70b-8192"
        LLM_TIMEOUT_SECONDS = 5
        LLM_MAX_RETRIES = 1

    router = build_provider_router(Settings())
    assert [provider.name for provider in router._providers] == ["azure", "groq"]

    Settings.LLM_PROVIDER = "groq"
    router = build_provider_router(Settings())
    assert [provider.name for provider in router._providers] == ["groq", "azure"]


def test_llm_provider_configuration_fails_closed_for_missing_or_invalid_selection() -> None:
    class Settings:
        ENVIRONMENT = "production"
        LLM_PROVIDER = "anthropic"
        AZURE_OPENAI_ENDPOINT = ""
        AZURE_OPENAI_API_KEY = ""
        ANTHROPIC_API_KEY = ""
        GROQ_API_KEY = "groq-key"
        GROQ_MODEL = "llama3-70b-8192"
        LLM_TIMEOUT_SECONDS = 5

    with pytest.raises(RuntimeError, match="API key is missing"):
        build_provider_router(Settings())

    Settings.LLM_PROVIDER = "unsupported"
    with pytest.raises(RuntimeError, match="Unsupported LLM_PROVIDER"):
        build_provider_router(Settings())


def test_provider_constructors_and_cost_estimates_are_fail_closed() -> None:
    with pytest.raises(ValueError, match="AZURE_OPENAI_ENDPOINT"):
        AzureOpenAIProvider("", "key", "gpt-4o")
    with pytest.raises(ValueError, match="AZURE_OPENAI_API_KEY"):
        AzureOpenAIProvider("https://example.openai.azure.com", "", "gpt-4o")
    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        GroqProvider("", "llama3-70b-8192")

    azure = AzureOpenAIProvider("https://example.openai.azure.com/", "key", "gpt-4o")
    assert azure._endpoint == "https://example.openai.azure.com"
    assert azure._estimate_cost(500, 500) == pytest.approx(0.002)
    assert _anthropic_cost("claude-sonnet-4-20250514", 1_000_000, 1_000_000) == pytest.approx(18.0)
    assert _anthropic_cost("unknown-model", 10, 10) == 0.0


@pytest.mark.asyncio
async def test_provider_health_checks_report_success_and_fail_closed(monkeypatch) -> None:
    azure = AzureOpenAIProvider("https://example.openai.azure.com", "key", "gpt-4o")
    anthropic = AnthropicProvider("key", "claude-sonnet-4-20250514")
    groq = GroqProvider("key", "llama3-70b-8192")

    async def ok_generate(**_kwargs):
        return GenerationResult(
            text="OK",
            provider="fake",
            model="fake",
            usage=TokenUsage(1, 1, 2, 0.0),
            latency_ms=1.0,
        )

    async def non_ok_generate(**_kwargs):
        return GenerationResult(
            text="not ready",
            provider="fake",
            model="fake",
            usage=TokenUsage(1, 1, 2, 0.0),
            latency_ms=1.0,
        )

    async def failing_generate(**_kwargs):
        raise ProviderError("dependency unavailable", "fake")

    monkeypatch.setattr(azure, "generate", ok_generate)
    monkeypatch.setattr(anthropic, "generate", non_ok_generate)
    monkeypatch.setattr(groq, "generate", failing_generate)

    assert await azure.health_check() is True
    assert await anthropic.health_check() is False
    assert await groq.health_check() is False


def test_content_review_policy_environment_parses_safe_values_and_rejects_unsafe(monkeypatch) -> None:
    monkeypatch.setenv("CONTENT_CONSENSUS_THRESHOLD", "4")
    monkeypatch.setenv("CONTENT_CONSENSUS_TIMEOUT_HOURS", "12")
    monkeypatch.setenv("CONTENT_CREATOR_APPROVAL_COUNTS", "yes")
    monkeypatch.setenv("CONTENT_DIRECT_PUBLISH_ALLOWED", "on")

    policy = ReviewGovernancePolicy.from_environment()

    assert policy.quorum_threshold == 4
    assert policy.stale_after_hours == 12
    assert policy.creator_approval_counts is True
    assert policy.direct_publish_allowed is True

    monkeypatch.setenv("CONTENT_CONSENSUS_THRESHOLD", "1")
    with pytest.raises(ValueError, match="between 2 and 10"):
        ReviewGovernancePolicy.from_environment()

    monkeypatch.setenv("CONTENT_CONSENSUS_THRESHOLD", "3")
    monkeypatch.setenv("CONTENT_CONSENSUS_TIMEOUT_HOURS", "0")
    with pytest.raises(ValueError, match="must be positive"):
        ReviewGovernancePolicy.from_environment()


def test_content_review_source_payload_and_rubric_helpers_are_conservative() -> None:
    source = ContentArtifactSource(
        source_document_id="caps-doc",
        source_chunk_id="chunk-1",
        source_title="CAPS source",
        source_type="curriculum",
        citation_text="Department source excerpt",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MAT",
        language="en",
        license_status="government_open",
        source_quality_score=0.95,
        chunk_hash="c" * 64,
        source_hash="s" * 64,
        source_role="primary_context",
        source_metadata={"reviewed_by": "educator"},
    )

    payload = _source_payload(source)

    assert payload["source_document_id"] == "caps-doc"
    assert payload["source_quality_score"] == 0.95
    assert payload["reviewed_by"] == "educator"
    assert _rubric_passed(True) is True
    assert _rubric_passed(0.8) is True
    assert _rubric_passed(" approved ") is True
    assert _rubric_passed({"result": "passed"}) is True
    assert _rubric_passed({"passed": 0.79}) is False
    assert _rubric_passed(False) is False
    assert _rubric_passed(None) is False


@pytest.mark.asyncio
async def test_external_provider_generate_fails_closed_when_sdks_are_missing(monkeypatch) -> None:
    real_import = __import__

    def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in {"anthropic", "groq", "openai"}:
            raise ImportError(f"{name} unavailable")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", blocked_import)

    providers = [
        AnthropicProvider("key", "claude-sonnet-4-20250514"),
        GroqProvider("key", "llama3-70b-8192"),
        AzureOpenAIProvider("https://example.openai.azure.com", "key", "gpt-4o"),
    ]

    for provider in providers:
        with pytest.raises(ProviderError, match="SDK not installed|request failed"):
            await provider.generate(system="safe", user="learner question")
