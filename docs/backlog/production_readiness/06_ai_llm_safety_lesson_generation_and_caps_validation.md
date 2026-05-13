# 6. AI, LLM safety, lesson generation, and CAPS validation

## 6.1 LLM gateway

- [verify] `P0` Define canonical LLM gateway interface.
- [verify] `P0` Include provider name in gateway metadata.
- [verify] `P0` Include model/version in gateway metadata.
- [verify] `P0` Include prompt template version in gateway metadata.
- [verify] `P0` Include input schema in gateway metadata.
- [verify] `P0` Include output schema in gateway metadata.
- [verify] `P0` Include latency in gateway metadata.
- [verify] `P0` Include token usage in gateway metadata.
- [verify] `P0` Include safety status in gateway metadata.
- [verify] `P0` Include fallback status in gateway metadata.
- [verify] `P1` Add provider fallback.
- [verify] `P1` Add timeout per provider.
- [verify] `P1` Add retry policy per provider.
- [verify] `P1` Add circuit breaker.
- [verify] `P1` Add budget guardrails.
- [verify] `P1` Add deterministic mock provider.
- [verify] `P1` Add local/offline fallback for development only.
- [verify] `P1` Add provider health checks.
- [verify] `P1` Add emergency flag `DISABLE_LESSON_GENERATION`.
- [verify] `P2` Add model comparison harness.

## 6.2 PII safety in LLM calls

- [verify] `P0` Ensure no raw learner name enters prompts.
- [verify] `P0` Ensure no guardian name enters prompts.
- [verify] `P0` Ensure no email enters prompts.
- [verify] `P0` Ensure no phone number enters prompts.
- [verify] `P0` Ensure no address enters prompts.
- [verify] `P0` Ensure no raw learner UUID enters external prompts if pseudonym is available.
- [verify] `P0` Ensure `pseudonym_id` is used for LLM context.
- [verify] `P0` Expand `scripts/popia_sweep.py`.
- [verify] `P0` Add PII seeded tests for lesson generation.
- [verify] `P0` Add PII seeded tests for parent summaries.
- [verify] `P0` Add PII seeded tests for RLHF feedback.
- [verify] `P0` Add PII seeded tests for logs.
- [verify] `P0` Fail CI if PII is detected in prompt paths.
- [verify] `P1` Add PII redaction metrics.
- [verify] `P1` Add redaction failure alerts.

## 6.3 Structured lesson output

- [verify] `P0` Define lesson output field `topic`.
- [verify] `P0` Define lesson output field `grade`.
- [verify] `P0` Define lesson output field `subject`.
- [verify] `P0` Define lesson output field `CAPS reference`.
- [verify] `P0` Define lesson output field `objectives`.
- [verify] `P0` Define lesson output field `explanation`.
- [verify] `P0` Define lesson output field `worked examples`.
- [verify] `P0` Define lesson output field `practice questions`.
- [verify] `P0` Define lesson output field `answer key`.
- [verify] `P0` Define lesson output field `remediation hints`.
- [verify] `P0` Define lesson output field `difficulty`.
- [verify] `P0` Define lesson output field `language level`.
- [verify] `P0` Define lesson output field `safety classification`.
- [verify] `P0` Define lesson output field `alignment confidence`.
- [verify] `P0` Define lesson output field `quality score`.
- [verify] `P0` Reject generated lesson if schema invalid.
- [verify] `P0` Reject generated lesson if CAPS alignment invalid.
- [verify] `P0` Reject generated lesson if age-inappropriate.
- [verify] `P0` Reject generated lesson if unsafe.
- [verify] `P0` Reject generated lesson if PII detected.
- [verify] `P0` Reject generated lesson if answer key missing.
- [verify] `P0` Reject generated lesson if answer key inconsistent.
- [verify] `P1` Add schema examples to OpenAPI.
- [verify] `P1` Add lesson schema documentation.

## 6.4 Content correctness validators

- [verify] `P0` Add arithmetic correctness validator.
- [verify] `P0` Add answer-key consistency validator.
- [verify] `P0` Add grade-level readability validator.
- [verify] `P0` Add missing-explanation validator.
- [verify] `P0` Add unsafe-content validator.
- [verify] `P0` Add PII-leakage validator.
- [verify] `P0` Add independent answer-key checking.
- [verify] `P1` Add content quality score.
- [verify] `P1` Add quality score threshold.
- [verify] `P1` Add low-confidence rejection path.
- [verify] `P1` Add low-confidence human-review path.
- [verify] `P2` Add lesson regression suite.
- [verify] `P2` Add accepted lesson snapshot tests.
- [verify] `P2` Add prompt regression tests.

## 6.5 Golden prompt coverage

- [verify] `P1` Add golden prompt test for each supported grade.
- [verify] `P1` Add golden prompt test for each supported subject.
- [verify] `P1` Add golden prompt test for each launch topic.
- [verify] `P1` Add golden prompt test for English.
- [verify] `P1` Add golden prompt test for isiZulu.
- [verify] `P1` Add golden prompt test for Afrikaans.
- [verify] `P1` Add golden prompt test for isiXhosa.
- [verify] `P1` Add golden prompt test for standard lesson variant.
- [verify] `P1` Add golden prompt test for visual variant.
- [verify] `P1` Add golden prompt test for story-based variant.
- [verify] `P1` Add golden prompt test for step-by-step variant.
- [verify] `P1` Add golden prompt test for exam-style variant.
- [verify] `P1` Add golden prompt test for real-world South African examples.
- [verify] `P2` Add golden prompt report artifact.

## 6.6 CAPS alignment

- [verify] `P0` Create canonical CAPS topic map.
- [verify] `P0` Include phase.
- [verify] `P0` Include grade.
- [verify] `P0` Include subject.
- [verify] `P0` Include term.
- [verify] `P0` Include topic.
- [verify] `P0` Include subtopic.
- [verify] `P0` Include prerequisites.
- [verify] `P0` Include assessment standards.
- [verify] `P0` Validate generated content references a valid CAPS topic.
- [verify] `P0` Prevent claims of full CAPS coverage until coverage is validated.
- [verify] `P1` Add curriculum coverage dashboard.
- [verify] `P1` Detect topics without lessons.
- [verify] `P1` Detect topics without diagnostics.
- [verify] `P1` Detect topics without practice questions.
- [verify] `P1` Detect topics without quality-reviewed content.
- [verify] `P1` Add alignment confidence score per lesson.
- [verify] `P2` Add teacher-facing CAPS coverage export.
- [verify] `P2` Version curriculum maps.

## 6.7 RLHF and feedback loop

- [verify] `P1` Verify RLHF feedback capture.
- [verify] `P1` Verify PII scrubbing before RLHF storage.
- [verify] `P1` Verify PII scrubbing before RLHF export.
- [verify] `P1` Add RLHF export format for OpenAI preference datasets if retained.
- [verify] `P1` Add RLHF export format for Anthropic preference datasets if retained.
- [verify] `P1` Add consent check before RLHF processing.
- [verify] `P1` Add guardian/learner feedback issue-reporting flow.
- [verify] `P2` Add RLHF quality analytics.
- [verify] `P2` Add feedback moderation queue.
- [verify] `P2` Add educator review workflow.

---

## 6.8 Repository-side implementation evidence

- [verify] `P0` Canonical LLM gateway interface is implemented in `app/services/llm/gateway.py`.
- [verify] `P0` Gateway metadata includes provider name, model/version, prompt template version, input schema, output schema, latency, token usage, safety status, and fallback status.
- [verify] `P0` POPIA-safe prompt context building and PII redaction are implemented in `app/services/content_safety/pii.py`.
- [verify] `P0` Structured lesson output validation and rejection paths are implemented in `app/services/content_safety/lesson_contracts.py`.
- [verify] `P0` Canonical CAPS topic-map structure and topic validation evidence are implemented in `app/services/content_safety/lesson_contracts.py` and documented in `docs/curriculum/caps_topic_map_production_contract.md`.
- [verify] `P1` Golden prompt coverage fixture is implemented in `tests/fixtures/ai/golden_prompt_coverage.json`.
- [verify] `P1` RLHF consent gating and PII scrubbing are implemented in `app/services/content_safety/pii.py`.
- [verify] `P1` Domain 06 repository evidence checker now includes concrete `app/services/llm` and `app/services/content_safety` implementation paths.
- [verify] `P1` Verification command is `make ai-llm-safety-caps-production-readiness-check`.

### Verification boundary

This marks repository-side implementation evidence as ready for verification. It does not claim external provider certification, GPU/model registry readiness, human AI-safety approval, legal/privacy approval, or full national CAPS coverage.
