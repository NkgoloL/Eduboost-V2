# 7. Diagnostics, assessment, item bank, and mastery model

## 7.1 IRT engine validation

- [verify] `[critical]` Define diagnostic item schema: item ID, subject, grade, topic, skill, difficulty, discrimination, correct answer, distractors, explanation, and CAPS reference.
- [verify] `[critical]` Validate IRT parameters for difficulty bounds, discrimination bounds, probability output, overflow, and invalid input. Evidence: `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/irt_params.py`, `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`, `tests/unit/test_irt_properties.py`. Verification gap: granular IRT validation backlog below still has open item-level checks.
- [verify] `[critical]` Add tests for probability of correctness, Fisher information, ability update, edge responses, empty responses, all-correct, and all-incorrect. Evidence: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`, `tests/legacy/unit/modules/diagnostics/test_irt_engine.py`, `tests/unit/test_irt_gap_probe.py`. Verification gap: granular test bullets below are not all individually reconciled to passing test evidence.
- [verify] `[high]` Add item calibration workflow. Evidence: `app/modules/diagnostics/calibration_service.py`, `tests/unit/modules/practice/test_practice_and_calibration.py`. Verification gap: granular item-bank backlog still lists calibration workflow verification as open.
- [verify] `[high]` Add item exposure limits so learners do not repeatedly see the same questions. Evidence: `app/models/item_exposure.py`, `app/modules/diagnostics/item_selection_service.py`, `tests/unit/modules/diagnostics/test_item_bank_service.py`. Verification gap: granular item-bank backlog still lists exposure limits and item reuse policy as open.
- [verify] `[high]` Add diagnostic session recovery after disconnect. Evidence: `app/modules/diagnostics/session_recovery_service.py`, `app/repositories/diagnostic_session_repository.py`, `tests/unit/modules/diagnostics/test_session_lifecycle.py`. Verification gap: granular diagnostic-session backlog still lists pause/resume and recovery checks as open.
- [verify] `[medium]` Add confidence intervals for ability estimates. Evidence: `app/modules/diagnostics/irt_engine.py`, `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`. Verification gap: granular diagnostic-session backlog still lists confidence interval checks as open.
- [verify] `[medium]` Add item bias review across language, region, and socioeconomic context. Evidence: `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/item_validator.py`, `tests/unit/modules/diagnostics/test_item_validator.py`. Verification gap: no green end-to-end bias review evidence is recorded here yet.

Granular verification backlog:

- [verify] `P0` Define diagnostic item schema. Evidence: `docs/diagnostics/item_contract.md`, `app/domain/item_schema.py`, `tests/unit/modules/diagnostics/test_item_bank_models.py`.
- [verify] `P0` Include item ID. Evidence: `docs/diagnostics/item_contract.md`, `app/domain/item_schema.py`.
- [verify] `P0` Include subject. Evidence: `docs/diagnostics/item_contract.md`, `app/domain/item_schema.py`.
- [verify] `P0` Include grade. Evidence: `docs/diagnostics/item_contract.md`, `app/domain/item_schema.py`.
- [verify] `P0` Include topic. Evidence: `docs/diagnostics/item_contract.md`, `app/domain/item_schema.py`.
- [verify] `P0` Include skill. Evidence: `docs/diagnostics/item_contract.md`, `app/domain/item_schema.py`.
- [verify] `P0` Include difficulty parameter. Evidence: `app/domain/item_schema.py`, `app/modules/diagnostics/irt_engine.py`.
- [verify] `P0` Include discrimination parameter. Evidence: `app/domain/item_schema.py`, `app/modules/diagnostics/irt_engine.py`.
- [verify] `P0` Include correct answer. Evidence: `docs/diagnostics/item_contract.md`, `app/domain/item_schema.py`.
- [verify] `P0` Include distractors. Evidence: `docs/diagnostics/item_contract.md`, `app/domain/item_schema.py`.
- [verify] `P0` Include explanation. Evidence: `docs/diagnostics/item_contract.md`, `app/domain/item_schema.py`.
- [verify] `P0` Include CAPS reference. Evidence: `docs/diagnostics/item_contract.md`, `app/domain/item_schema.py`.
- [verify] `P0` Validate theta bounds. Evidence: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`, `tests/unit/test_irt_properties.py`.
- [verify] `P0` Validate discrimination bounds. Evidence: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`.
- [verify] `P0` Validate difficulty bounds. Evidence: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`.
- [verify] `P0` Validate probability output. Evidence: `scripts/ci/check_diagnostics_assessment.py`, `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`.
- [verify] `P0` Validate overflow safety. Evidence: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`.
- [verify] `P0` Validate invalid input handling. Evidence: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`.
- [verify] `P0` Add test for probability of correctness. Evidence: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`.
- [verify] `P0` Add test for Fisher information. Evidence: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`, `scripts/ci/check_diagnostics_assessment.py`.
- [verify] `P0` Add test for ability update. Evidence: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`, `tests/unit/modules/diagnostics/test_session_lifecycle.py`.
- [verify] `P0` Add test for EAP estimate. Evidence: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`.
- [verify] `P0` Add test for empty responses. Evidence: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`.
- [verify] `P0` Add test for all-correct responses. Evidence: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`.
- [verify] `P0` Add test for all-incorrect responses. Evidence: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`.
- [verify] `P0` Add test for stopping criteria. Evidence: `tests/unit/modules/diagnostics/test_session_lifecycle.py`.
- [verify] `P0` Add test for grade-equivalent mapping.
- [verify] `P1` Add test for item selection by Fisher information.
- [verify] `P1` Add test for gap identification.

## 7.2 Item bank

- [verify] `[critical]` Build minimum viable item bank for each supported launch grade/subject.
- [verify] `[critical]` Add item review status: draft, AI-generated, human-reviewed, approved, retired.
- [verify] `[high]` Add distractor quality review and explanation quality review.
- [verify] `[medium]` Tag items by misconception.
- [verify] `[medium]` Add adaptive practice generator based on diagnostic gaps. Evidence: `app/modules/practice/practice_generator.py`, `tests/unit/modules/practice/test_practice_and_calibration.py`. Verification gap: item-bank and gap-identification granular backlog remains open.
- [verify] `[medium]` Add spaced repetition and retrieval practice. Evidence: `app/modules/practice/spaced_repetition_scheduler.py`, `tests/unit/modules/practice/test_practice_and_calibration.py`. Verification gap: no recorded green release/runtime evidence for the practice workflow is attached here yet.

Granular item-bank backlog:

- [verify] `P0` Build minimum viable item bank for each launch grade.
- [verify] `P0` Build minimum viable item bank for each launch subject.
- [verify] `P0` Add item review status `draft`.
- [verify] `P0` Add item review status `AI-generated`.
- [verify] `P0` Add item review status `human-reviewed`.
- [verify] `P0` Add item review status `approved`.
- [verify] `P0` Add item review status `retired`.
- [verify] `P1` Add item calibration workflow. Evidence: `app/modules/diagnostics/calibration_service.py`, `tests/unit/modules/practice/test_practice_and_calibration.py`.
- [verify] `P1` Add item exposure limits. Evidence: `app/models/item_exposure.py`, `app/modules/diagnostics/item_bank_service.py`, `tests/unit/modules/diagnostics/test_item_bank_service.py`.
- [verify] `P1` Add item reuse policy. Evidence: `docs/learning_science/learning_evidence.md`, `app/modules/diagnostics/item_bank_service.py`; verification gap: production item analytics still required.
- [verify] `P1` Add item retirement workflow.
- [verify] `P1` Add item import/export tooling.
- [verify] `P2` Add item authoring interface.
- [verify] `P2` Add item analytics dashboard.

## 7.3 Diagnostic session lifecycle

- [verify] `[critical]` Define mastery model combining diagnostic estimate, practice performance, recency, consistency, and confidence. Evidence: `app/modules/progress/mastery_model.py`, `tests/unit/modules/progress/test_mastery_model.py`. Verification gap: diagnostic-session lifecycle backlog below still has open runtime path checks.
- [verify] `[high]` Add progress timelines per learner. Evidence: `app/modules/progress/progress_timeline_service.py`, `tests/integration/test_parent_progress_authorization.py`, `tests/unit/test_parent_progress_authorization_wiring.py`. Verification gap: learner-facing timeline behavior is not tied to green runtime/CI evidence here yet.
- [verify] `[high]` Add subject-level and topic-level mastery. Evidence: `app/repositories/mastery_repository.py`, `app/modules/progress/mastery_model.py`, `tests/integration/test_learner_mastery_authorization.py`, `tests/unit/test_learner_mastery_authorization_wiring.py`. Verification gap: granular diagnostic result retrieval and authorization checks remain open below.
- [verify] `[medium]` Add learning velocity, risk-of-falling-behind signal, and next-best-activity recommendation. Evidence: `app/modules/progress/learning_velocity_service.py`, `tests/unit/modules/progress/test_mastery_model.py`. Verification gap: no green release/runtime evidence for the recommendation path is attached here yet.
- [todo] `[research]` Evaluate Bayesian Knowledge Tracing or Deep Knowledge Tracing once enough usage data exists.

Granular diagnostic-session backlog:

- [verify] `P0` Implement diagnostic session start. Evidence: `app/modules/diagnostics/diagnostic_session_service.py`, `tests/unit/modules/diagnostics/test_session_lifecycle.py`.
- [verify] `P0` Implement question serving. Evidence: `app/modules/diagnostics/diagnostic_session_service.py`, `tests/unit/modules/diagnostics/test_session_lifecycle.py`.
- [verify] `P0` Implement answer submission. Evidence: `app/modules/diagnostics/diagnostic_session_service.py`, `tests/unit/modules/diagnostics/test_session_lifecycle.py`.
- [verify] `P0` Implement ability update. Evidence: `app/modules/diagnostics/irt_engine.py`, `tests/unit/modules/diagnostics/test_session_lifecycle.py`.
- [verify] `P0` Implement result retrieval. Evidence: `app/modules/diagnostics/diagnostic_session_service.py`, `tests/unit/modules/diagnostics/test_session_lifecycle.py`.
- [verify] `P0` Implement consent check before diagnostic. Evidence: `docs/security/diagnostics_consent_gate.md`, `tests/unit/test_diagnostics_consent_gate_wiring.py`.
- [verify] `P0` Implement object authorization check before diagnostic. Evidence: `docs/security/diagnostic_items_authorization_wiring.md`, `docs/security/diagnostic_submit_authorization_wiring.md`.
- [verify] `P1` Add diagnostic pause/resume. Evidence: `app/modules/diagnostics/session_recovery_service.py`, `tests/unit/modules/diagnostics/test_session_lifecycle.py`.
- [verify] `P1` Add diagnostic session recovery after disconnect. Evidence: `app/modules/diagnostics/session_recovery_service.py`, `tests/unit/modules/diagnostics/test_session_lifecycle.py`.
- [verify] `P1` Add maximum item cap. Evidence: `app/modules/diagnostics/termination_service.py`, `tests/unit/modules/diagnostics/test_session_lifecycle.py`.
- [verify] `P1` Add minimum evidence threshold before final result. Evidence: `app/modules/diagnostics/termination_service.py`, `tests/unit/modules/diagnostics/test_session_lifecycle.py`.
- [verify] `P1` Add confidence interval. Evidence: `app/modules/diagnostics/irt_engine.py`, `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`.
- [verify] `P2` Add diagnostic review by educator.

## 7.4 Bias, quality, and fairness

- [verify] `P1` Add item bias review across language.
- [verify] `P1` Add item bias review across region.
- [verify] `P1` Add item bias review across socioeconomic context.
- [verify] `P1` Add distractor quality review.
- [verify] `P1` Add explanation quality review.
- [verify] `P1` Tag items by misconception.
- [verify] `P2` Add bias-review dashboard.
- [verify] `P2` Add educator sign-off process.

## 7.5 Mastery and remediation

- [verify] `P1` Define mastery model. Evidence: `app/modules/progress/mastery_model.py`, `docs/learning_science/mastery_model.md`, `tests/unit/modules/progress/test_mastery_model.py`.
- [verify] `P1` Combine diagnostic estimate into mastery. Evidence: `app/modules/progress/mastery_model.py`, `tests/unit/modules/progress/test_mastery_model.py`.
- [verify] `P1` Combine practice performance into mastery. Evidence: `app/modules/progress/mastery_model.py`, `tests/unit/modules/progress/test_mastery_model.py`.
- [verify] `P1` Combine recency into mastery. Evidence: `app/modules/progress/mastery_model.py`, `tests/unit/modules/progress/test_mastery_model.py`.
- [verify] `P1` Combine consistency into mastery. Evidence: `app/modules/progress/mastery_model.py`, `tests/unit/modules/progress/test_mastery_model.py`.
- [verify] `P1` Combine confidence into mastery. Evidence: `app/modules/progress/mastery_model.py`, `tests/unit/modules/progress/test_mastery_model.py`.
- [verify] `P1` Add topic-level mastery. Evidence: `app/modules/progress/mastery_model.py`, `app/repositories/mastery_repository.py`.
- [verify] `P1` Add subject-level mastery. Evidence: `app/modules/progress/mastery_model.py`, `app/repositories/mastery_repository.py`.
- [verify] `P1` Add progress timelines. Evidence: `app/modules/progress/progress_timeline_service.py`.
- [verify] `P1` Add adaptive practice generator. Evidence: `app/modules/practice/practice_generator.py`, `tests/unit/modules/practice/test_practice_and_calibration.py`.
- [verify] `P1` Add remediation based on misconception.
- [verify] `P2` Add spaced repetition.
- [verify] `P2` Add retrieval practice.
- [verify] `P2` Add learning velocity.
- [verify] `P2` Add risk-of-falling-behind signal.
- [verify] `P2` Add next-best-activity recommendation.
- [todo] `Research` Evaluate Bayesian Knowledge Tracing after sufficient data exists.
- [todo] `Research` Evaluate Deep Knowledge Tracing after sufficient data exists.

---


## 7.6 Repository-side implementation evidence

- [verify] `P0` Production diagnostics and assessment readiness checker added. Evidence: `scripts/check_diagnostics_assessment_production_readiness.py`, `tests/unit/test_diagnostics_assessment_production_readiness.py`, `make diagnostics-assessment-production-readiness-check`.
- [verify] `P0` Canonical dependency-light production contracts added for diagnostic item schema, review workflow, Fisher-information item selection, grade-equivalent mapping, gap identification, launch item-bank audit, bias dimensions, and misconception remediation routing. Evidence: `app/modules/diagnostics/production_readiness_contracts.py`.
- [verify] `P0` Diagnostics assessment readiness contract added. Evidence: `docs/diagnostics/production_diagnostics_assessment_readiness_contract.md`.
- [verify] `P0` Item bank launch coverage and review workflow contract added. Evidence: `docs/diagnostics/item_bank_launch_coverage_contract.md`.
- [verify] `P1` Mastery, remediation, spaced repetition, retrieval practice, velocity, risk, and next-best-activity contract added. Evidence: `docs/diagnostics/mastery_model_assessment_contract.md`.
- [verify] `P1` Assessment quality and fairness contract added for language, region, socioeconomic context, distractor quality, explanation quality, misconception tagging, and educator sign-off. Evidence: `docs/diagnostics/assessment_quality_fairness_contract.md`.
- [todo] `Research` Research items remain outstanding until sufficient usage data exists: Bayesian Knowledge Tracing and Deep Knowledge Tracing evaluation.

Verification command:

```bash
make diagnostics-assessment-production-readiness-check
pytest -c pytest.ini tests/unit/test_diagnostics_assessment_production_readiness.py -q --no-cov
```
