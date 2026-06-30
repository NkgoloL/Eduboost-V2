# 19. Roadmap after production-readiness baseline

## 19.1 Product expansion

- [verify] `P2` Add teacher dashboard if not in beta scope.
- [verify] `P2` Add classroom diagnostics.
- [verify] `P2` Add class intervention groups.
- [verify] `P2` Add teacher-facing CAPS coverage export.
- [verify] `P2` Add parent co-pilot weekly guidance.
- [verify] `P2` Add sponsored learner model.
- [verify] `P2` Add NGO/community partnership workflows.
- [verify] `P2` Add printable worksheets.
- [verify] `P2` Add offline lesson packs.
- [verify] `P3` Add all 11 official South African languages.
- [verify] `P3` Add advanced analytics for learning velocity.
- [verify] `P3` Add curriculum graph visualization.

## 19.2 Technical scale

- [verify] `P2` Add load testing suite.
- [verify] `P2` Define concurrency targets.
- [verify] `P2` Define learner journey SLOs.
- [verify] `P2` Define LLM latency SLOs.
- [verify] `P2` Define diagnostic latency SLOs.
- [verify] `P2` Add autoscaling policy.
- [verify] `P2` Add cache hit-rate goals.
- [verify] `P2` Add cost-per-lesson metric.
- [verify] `P3` Split inference service only if load evidence demands it.
- [verify] `P3` Consider diagnostics service split only if load evidence demands it.

## 19.3 Research

- [verify] `Research` Investigate retrieval-augmented generation using approved CAPS content only.
- [verify] `Research` Investigate local/smaller models.
- [verify] `Research` Investigate Bayesian Knowledge Tracing.
- [verify] `Research` Investigate Deep Knowledge Tracing.
- [verify] `Research` Conduct educator review of generated lessons.
- [verify] `Research` Conduct parent usability interviews.
- [verify] `Research` Conduct learner usability testing with consent.
- [verify] `Research` Conduct low-bandwidth UX testing.

---



## 19.6 Repository-side implementation evidence

- [verify] Post-baseline roadmap decision is documented in `docs/adr/ADR-019-roadmap-after-production-readiness-baseline.md`.
- [verify] Post-baseline roadmap architecture is documented in `docs/roadmap/post_baseline_roadmap_architecture_contract.md`.
- [verify] Production-readiness baseline boundary is documented in `docs/roadmap/production_readiness_baseline_boundary_contract.md`.
- [verify] Post-baseline roadmap register is documented in `docs/roadmap/post_baseline_roadmap_register.md`.
- [verify] Deferred scope register is documented in `docs/roadmap/deferred_scope_register.md`.
- [verify] Roadmap dependency register is documented in `docs/roadmap/roadmap_dependency_register.md`.
- [verify] Roadmap graduation criteria are documented in `docs/roadmap/roadmap_graduation_criteria.md`.
- [verify] Roadmap review cadence is documented in `docs/roadmap/roadmap_review_cadence_contract.md`.
- [verify] Post-baseline risk register is documented in `docs/roadmap/post_baseline_risk_register.md`.
- [verify] GA graduation boundary is documented in `docs/roadmap/ga_graduation_boundary_contract.md`.
- [verify] Deterministic repository contracts live in `app/modules/roadmap/production_readiness_contracts.py`.
- [verify] Repository validation is provided by `scripts/check_roadmap_after_production_readiness_baseline.py`.
- [verify] Domain validation wrapper is provided by `scripts/check_domain_19_roadmap_after_baseline_evidence.py`.
- [verify] Unit coverage is provided by `tests/unit/test_roadmap_after_production_readiness_baseline.py`.
- [verify] Make target is `make roadmap-after-production-readiness-baseline-check`.

### Verification boundary

This implementation provides repository-side post-baseline roadmap, deferred scope, dependency, graduation, review cadence, GA boundary, and risk-tracking readiness evidence. It does not create GitHub issues, approve future scope, complete deferred work, satisfy external/manual dependencies, or authorize production launch.
