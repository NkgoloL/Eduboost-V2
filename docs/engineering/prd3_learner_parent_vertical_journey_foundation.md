# PRD-3.0-3.4 Learner and Parent Vertical Journey Foundation

This slice starts PRD-3 by adding a single learner/parent journey contract on
top of the already-existing onboarding, consent, diagnostics, runtime KG,
lessons, assessment, mastery, study-plan, gamification, parent portal, and
POPIA rights paths.

## Scope

- Add `app.modules.vertical_journey` as a deterministic journey-state service.
- Add `/api/v2/vertical-journey/learners/{learner_id}` and `/v2/...` route registration.
- Surface consent blockers instead of silently treating the vertical journey as complete.
- Include runtime-KG gap-profile metadata while preserving PRD-2's opt-in boundary.
- Preserve POPIA export and erasure route visibility without authorising live traffic.

## Explicit non-goals

- No public beta authorisation.
- No live learner traffic authorisation.
- No production release or deployment authorisation.
- No PRD-4 implementation.

The next PRD-3 bundle should complete the remaining hardening work: deeper
route tests, parent report output, POPIA export/erasure drill proof, final
PRD-3 evidence, and controlled handoff to PRD-4.
