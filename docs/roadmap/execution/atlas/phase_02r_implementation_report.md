# Phase 2R Implementation Report

**Report status:** In Progress
**Current gate:** 2R.1
**Next gate:** Blocked
**Plan version:** 1.5

**Update:** The Phase 2R Gates 2R.2-2R.8 implementation patch has now been applied on the current worktree. It adds the later-gate grounding models, services, verifier scripts, and migration scaffolding, but it does not change the Gate 2R.1 control posture.

## Gate 2R.1 implementation reconciliation

| Work item | Actual implementation | Current disposition |
|---|---|---|
| P02R-0101 | Added `curriculum_sources`, `curriculum_source_versions`, `curriculum_rights_decisions`, `curriculum_inventory_versions`, `curriculum_inventory_items`, and `curriculum_review_decisions`; added Alembic revision `20260616_1200_phase02r_authority` and append-only triggers. | Implemented; PostgreSQL upgrade/constraint/trigger verification pending. |
| P02R-0102 | Added explicit per-use rights fields, separate translation/publication permissions, structured conditions, expiry checks, and a default-deny policy engine. | Implemented; real source-version rights decisions and rights approval pending. |
| P02R-0103 | Added the bounded Grade 4 Mathematics CAPS source-completeness register and deterministic structural/freeze validator. | Implemented; register remains draft and cannot satisfy closure. |
| P02R-0104 | Added an independent append-only review-domain ledger and policy checks preventing one review domain from satisfying another. | Implemented; signed human decisions pending. |

## Governance corrections

- Reverted the premature control transition to `approved_gate=2R.0` and `authorised_next_gate=2R.1`.
- Marked the earlier dirty-worktree Gate 2R.1 evidence as superseded.
- Changed the collector to require a clean Git worktree and to emit candidate evidence only.
- Added separate implementation and closure verification modes.
- Added gate-state validation that prevents a transition to unsupported automation or a contradictory plan/evidence state.
- Added a pending Gate 2R.1 approval record; no reviewer decision is fabricated by this patch.
- Applied the later-gate implementation bundle for Gates 2R.2-2R.8 while keeping Gate 2R.1 as the only authorised gate.

## Files added

- `app/models/curriculum_authority.py`
- `app/services/curriculum/rights_policy.py`
- `alembic/versions/20260616_1200_phase02r_authority_controls.py`
- `data/curriculum/registries/grade4_mathematics_caps_source_completeness.json`
- `scripts/phase02r_gate_control.py`
- `scripts/validate_phase02r_authority_schema.py`
- `scripts/curriculum/validate_source_completeness_register.py`
- `tests/unit/phase02r/`
- `alembic/versions/20260618_1200_phase02r_grounding_controls.py`
- `app/models/curriculum_grounding.py`
- `app/services/curriculum/acquisition.py`
- `app/services/curriculum/answer_verification.py`
- `app/services/curriculum/claim_validation.py`
- `app/services/curriculum/corpus.py`
- `app/services/curriculum/evaluation.py`
- `app/services/curriculum/extraction.py`
- `app/services/curriculum/graph.py`
- `app/services/curriculum/grounding.py`
- `app/services/curriculum/legacy.py`
- `app/services/curriculum/phase02r_verification.py`
- `app/services/curriculum/tutor_grounding.py`
- `scripts/verify_phase02r_gate2r2_to_2r8.py`
- `tests/unit/phase02r/test_gate2r2_to_2r8_services.py`
- `tests/unit/phase02r/test_grounding_models.py`

## Remaining Gate 2R.1 closure work

1. Apply the migration to a clean PostgreSQL database and an upgrade-from-current-head database.
2. Verify append-only triggers by attempting prohibited update/delete operations.
3. Enter real logical source and immutable source-version records.
4. Record per-use rights decisions with evidence for every active source version.
5. Resolve and freeze the completeness register.
6. Record independent rights, source-authority, and inventory-completeness approvals.
7. Collect candidate evidence from a clean worktree, commit evidence, then issue a separate gate-approval commit.

Gate 2R.2 remains blocked until all items above pass.
