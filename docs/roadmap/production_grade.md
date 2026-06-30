# Todo Production Grade

Last updated: 2026-06-01 (Sprint 6 implementation pass)
Branch: remediation/phase0-phase1

## Completed So Far

- [x] Sprint 1: settings bootstrap + production compose contract hardening
- [x] Sprint 1: added/validated prod compose contract checks
- [x] Sprint 2: P0 auth/security coverage tranche completed
- [x] Sprint 2: auth router tests expanded to full route-path coverage
- [x] Sprint 2: security helper and jwt keyring runtime paths covered
- [x] Sprint 3: POPIA/consent runtime coverage tranche completed
- [x] Sprint 3: canonical consent service behavior tests added
- [x] Sprint 3: canonical consent repository behavior tests added
- [x] Sprint 3: POPIA data-rights router contract tests added
- [x] Sprint 4: P1 core product coverage
- [x] Sprint 4: content factory service tests added (27 new tests covering ETLProvenanceService, ContentValidationService, stable_json_hash)
- [x] Sprint 4: lesson generation pipeline tests added (9 new tests covering LessonGenerator validation branches)
- [x] Sprint 4: assessment service v2 tests added (8 new tests covering field variants, normalization, edge cases)
- [x] Sprint 5: repository coverage expansion for assessment + gamification repositories

## Evidence Snapshot

- Sprint 1 commit: af708814
- Sprint 2 commits: 2dc7cbfd, cf2af16c
- Sprint 3 commit: f6a800d8
- Sprint 4 commits: f8832ab7, 73c60db0, 0634c6cb, cea29fba
- Sprint 5 commit: 046be013
- Focused suites added since Sprint 4/5:
  - tests/unit/test_content_factory_services.py
  - tests/unit/test_lesson_generator.py
  - tests/unit/test_v2_services_full.py
  - tests/unit/test_v2_repositories_full.py
- Validation run (2026-06-01): 97 passed in focused Sprint 4/5 suites

## Current State (Post Sprint 1-5)

- [x] Sprint 5 repository tranche delivered (assessment + gamification repository tests)
- [ ] Overall backend coverage target (>= 80%) is not met yet
- [ ] Full integration/e2e production-path coverage is still pending
- [ ] Final release hardening evidence pack is still pending
- [x] Sprint 6: added coverage tranche for ETL + LLM gateway v2 + router contracts
- [x] Sprint 6: added assessment production-path integration test coverage
- [x] Sprint 6: restored `.coveragerc` and raised CI coverage floor from 60% to 67%

## Test velocity & coverage plan

See **`Todo_Test_Velocity_And_Coverage.md`** for the full phased checklist (fast pytest defaults, xdist, governance marker, router/service coverage, CI ratchet).

## Current P0 Blocker Detail

PR #192 introduced an updated production-grade blocker tracker. It is preserved as supporting roadmap detail at [production_grade_p0_blockers_2026_06_01.md](production_grade_p0_blockers_2026_06_01.md). Root `TODO.md` remains authoritative.

## Remaining To Reach Production Grade

- [ ] Expand coverage for remaining critical low-coverage modules (continue beyond Sprint 6 additions)
- [ ] Add integration tests for critical production paths end-to-end (continue beyond assessment path)
- [ ] Raise and stabilize overall backend coverage toward production target (80%+)
- [ ] Enforce final coverage gate and re-run authoritative CI evidence (authoritative full-suite run pending)
- [ ] Final production hardening, release validation, and go/no-go evidence refresh

## Current Risk Notes

- Sprint 1-5 materially improved unit-level confidence for auth/security/POPIA and core learning services.
- Coverage instrumentation now runs for the focused suites, but global backend coverage remains far below production target.
- Production readiness remains blocked on broad coverage uplift, integration validation, and final release evidence closure.
