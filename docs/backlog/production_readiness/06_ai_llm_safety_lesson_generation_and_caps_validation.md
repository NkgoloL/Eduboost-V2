# 6. AI, LLM safety, lesson generation, and CAPS validation

## 6.1 LLM gateway

- [ ] `P0` Define canonical LLM gateway interface.
- [ ] `P0` Include provider name in gateway metadata.
- [ ] `P0` Include model/version in gateway metadata.
- [ ] `P0` Include prompt template version in gateway metadata.
- [ ] `P0` Include input schema in gateway metadata.
- [ ] `P0` Include output schema in gateway metadata.
- [ ] `P0` Include latency in gateway metadata.
- [ ] `P0` Include token usage in gateway metadata.
- [ ] `P0` Include safety status in gateway metadata.
- [ ] `P0` Include fallback status in gateway metadata.
- [ ] `P1` Add provider fallback.
- [ ] `P1` Add timeout per provider.
- [ ] `P1` Add retry policy per provider.
- [ ] `P1` Add circuit breaker.
- [ ] `P1` Add budget guardrails.
- [ ] `P1` Add deterministic mock provider.
- [ ] `P1` Add local/offline fallback for development only.
- [ ] `P1` Add provider health checks.
- [ ] `P1` Add emergency flag `DISABLE_LESSON_GENERATION`.
- [ ] `P2` Add model comparison harness.

## 6.2 PII safety in LLM calls

- [ ] `P0` Ensure no raw learner name enters prompts.
- [ ] `P0` Ensure no guardian name enters prompts.
- [ ] `P0` Ensure no email enters prompts.
- [ ] `P0` Ensure no phone number enters prompts.
- [ ] `P0` Ensure no address enters prompts.
- [ ] `P0` Ensure no raw learner UUID enters external prompts if pseudonym is available.
- [ ] `P0` Ensure `pseudonym_id` is used for LLM context.
- [ ] `P0` Expand `scripts/popia_sweep.py`.
- [ ] `P0` Add PII seeded tests for lesson generation.
- [ ] `P0` Add PII seeded tests for parent summaries.
- [ ] `P0` Add PII seeded tests for RLHF feedback.
- [ ] `P0` Add PII seeded tests for logs.
- [ ] `P0` Fail CI if PII is detected in prompt paths.
- [ ] `P1` Add PII redaction metrics.
- [ ] `P1` Add redaction failure alerts.

## 6.3 Structured lesson output

- [ ] `P0` Define lesson output field `topic`.
- [ ] `P0` Define lesson output field `grade`.
- [ ] `P0` Define lesson output field `subject`.
- [ ] `P0` Define lesson output field `CAPS reference`.
- [ ] `P0` Define lesson output field `objectives`.
- [ ] `P0` Define lesson output field `explanation`.
- [ ] `P0` Define lesson output field `worked examples`.
- [ ] `P0` Define lesson output field `practice questions`.
- [ ] `P0` Define lesson output field `answer key`.
- [ ] `P0` Define lesson output field `remediation hints`.
- [ ] `P0` Define lesson output field `difficulty`.
- [ ] `P0` Define lesson output field `language level`.
- [ ] `P0` Define lesson output field `safety classification`.
- [ ] `P0` Define lesson output field `alignment confidence`.
- [ ] `P0` Define lesson output field `quality score`.
- [ ] `P0` Reject generated lesson if schema invalid.
- [ ] `P0` Reject generated lesson if CAPS alignment invalid.
- [ ] `P0` Reject generated lesson if age-inappropriate.
- [ ] `P0` Reject generated lesson if unsafe.
- [ ] `P0` Reject generated lesson if PII detected.
- [ ] `P0` Reject generated lesson if answer key missing.
- [ ] `P0` Reject generated lesson if answer key inconsistent.
- [ ] `P1` Add schema examples to OpenAPI.
- [ ] `P1` Add lesson schema documentation.

## 6.4 Content correctness validators

- [ ] `P0` Add arithmetic correctness validator.
- [ ] `P0` Add answer-key consistency validator.
- [ ] `P0` Add grade-level readability validator.
- [ ] `P0` Add missing-explanation validator.
- [ ] `P0` Add unsafe-content validator.
- [ ] `P0` Add PII-leakage validator.
- [ ] `P0` Add independent answer-key checking.
- [ ] `P1` Add content quality score.
- [ ] `P1` Add quality score threshold.
- [ ] `P1` Add low-confidence rejection path.
- [ ] `P1` Add low-confidence human-review path.
- [ ] `P2` Add lesson regression suite.
- [ ] `P2` Add accepted lesson snapshot tests.
- [ ] `P2` Add prompt regression tests.

## 6.5 Golden prompt coverage

- [ ] `P1` Add golden prompt test for each supported grade.
- [ ] `P1` Add golden prompt test for each supported subject.
- [ ] `P1` Add golden prompt test for each launch topic.
- [ ] `P1` Add golden prompt test for English.
- [ ] `P1` Add golden prompt test for isiZulu.
- [ ] `P1` Add golden prompt test for Afrikaans.
- [ ] `P1` Add golden prompt test for isiXhosa.
- [ ] `P1` Add golden prompt test for standard lesson variant.
- [ ] `P1` Add golden prompt test for visual variant.
- [ ] `P1` Add golden prompt test for story-based variant.
- [ ] `P1` Add golden prompt test for step-by-step variant.
- [ ] `P1` Add golden prompt test for exam-style variant.
- [ ] `P1` Add golden prompt test for real-world South African examples.
- [ ] `P2` Add golden prompt report artifact.

## 6.6 CAPS alignment

- [ ] `P0` Create canonical CAPS topic map.
- [ ] `P0` Include phase.
- [ ] `P0` Include grade.
- [ ] `P0` Include subject.
- [ ] `P0` Include term.
- [ ] `P0` Include topic.
- [ ] `P0` Include subtopic.
- [ ] `P0` Include prerequisites.
- [ ] `P0` Include assessment standards.
- [ ] `P0` Validate generated content references a valid CAPS topic.
- [ ] `P0` Prevent claims of full CAPS coverage until coverage is validated.
- [ ] `P1` Add curriculum coverage dashboard.
- [ ] `P1` Detect topics without lessons.
- [ ] `P1` Detect topics without diagnostics.
- [ ] `P1` Detect topics without practice questions.
- [ ] `P1` Detect topics without quality-reviewed content.
- [ ] `P1` Add alignment confidence score per lesson.
- [ ] `P2` Add teacher-facing CAPS coverage export.
- [ ] `P2` Version curriculum maps.

## 6.7 RLHF and feedback loop

- [ ] `P1` Verify RLHF feedback capture.
- [ ] `P1` Verify PII scrubbing before RLHF storage.
- [ ] `P1` Verify PII scrubbing before RLHF export.
- [ ] `P1` Add RLHF export format for OpenAI preference datasets if retained.
- [ ] `P1` Add RLHF export format for Anthropic preference datasets if retained.
- [ ] `P1` Add consent check before RLHF processing.
- [ ] `P1` Add guardian/learner feedback issue-reporting flow.
- [ ] `P2` Add RLHF quality analytics.
- [ ] `P2` Add feedback moderation queue.
- [ ] `P2` Add educator review workflow.

---

